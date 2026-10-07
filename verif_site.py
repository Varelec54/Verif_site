from datetime import datetime
import threading
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse


class SyntaxCheckerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Vérificateur de Site Web (Audit SEO, Technique & Performance)")
        self.root.geometry("850x720")

        top_frame = tk.Frame(root, padx=10, pady=10)
        top_frame.pack(fill=tk.X)

        self.label = tk.Label(
            top_frame, text="Adresse du site (URL) :", font=("Arial", 11, "bold")
        )
        self.label.pack(side=tk.LEFT, padx=5)

        self.url_entry = tk.Entry(top_frame, width=40, font=("Arial", 11))
        self.url_entry.pack(side=tk.LEFT, padx=5)
        self.url_entry.insert(0, "https://")

        self.btn_start = tk.Button(
            top_frame,
            text="Scanner le site",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.start_analysis_thread,
        )
        self.btn_start.pack(side=tk.LEFT, padx=5)

        console_frame = tk.Frame(root, padx=10, pady=5)
        console_frame.pack(fill=tk.BOTH, expand=True)

        self.log_area = scrolledtext.ScrolledText(
            console_frame,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg="#1e1e1e",
            fg="#00ff00",
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.insert(
            tk.END,
            "Prêt. Entrez l'URL de votre site et cliquez sur 'Scanner le site'.\n",
        )

        bottom_frame = tk.Frame(root, padx=10, pady=10)
        bottom_frame.pack(fill=tk.X)

        self.progress_bar = ttk.Progressbar(bottom_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill=tk.X, side=tk.TOP, pady=2)

        self.status_label = tk.Label(bottom_frame, text="Statut : En attente de lancement", font=("Arial", 9, "italic"))
        self.status_label.pack(side=tk.LEFT, pady=2)

    def log(self, message):
        def _log():
            self.log_area.insert(tk.END, message + "\n")
            self.log_area.see(tk.END)
        self.root.after(0, _log)

    def update_progress(self, current, total):
        def _progress():
            self.progress_bar["value"] = (current / total) * 100
            self.status_label.config(text=f"Statut : Analyse de la page {current} sur {total}...")
        self.root.after(0, _progress)

    def start_analysis_thread(self):
        url = self.url_entry.get().strip()
        if not url or url == "https://":
            messagebox.showwarning(
                "Attention", "Veuillez entrer une URL valide s'il vous plaît."
            )
            return

        self.btn_start.config(state=tk.DISABLED, bg="grey")
        self.log_area.delete(1.0, tk.END)
        self.progress_bar["value"] = 0
        self.status_label.config(text="Statut : Initialisation du scan...")

        threading.Thread(
            target=self.run_full_scan, args=(url,), daemon=True
        ).start()

    def analyze_page(self, url, headers, base_url):
        try:
            start_time = time.time()
            response = requests.get(url, headers=headers, timeout=10)
            load_time = time.time() - start_time
            
            if response.status_code != 200:
                return False, f"Code HTTP {response.status_code}", [], []

            html_content = response.text
            soup = BeautifulSoup(html_content, "html.parser")

            errors = []
            warnings = []
            page_links = []

            if load_time > 2.0:
                warnings.append(f"Temps de chargement lent ({load_time:.2f} sec / max recommandé: 2.0s).")

            content_encoding = response.headers.get("Content-Encoding", "").lower()
            if not any(enc in content_encoding for enc in ["gzip", "br", "deflate"]):
                warnings.append("Compression HTTP (Gzip/Brotli) non détectée sur cette page.")

            if not url.startswith("https://"):
                warnings.append("La page n'utilise pas le protocole sécurisé HTTPS.")

            if "<!doctype html>" not in html_content.lower() and "<!DOCTYPE HTML>" not in html_content:
                errors.append("DOCTYPE manquant ou invalide.")

            title_tag = soup.find("title")
            if not title_tag or not title_tag.text.strip():
                errors.append("Balise <title> manquante ou vide.")
            else:
                title_len = len(title_tag.text.strip())
                if title_len > 60:
                    warnings.append(f"Balise <title> trop longue ({title_len} caract. / max: 60).")

            meta_desc = soup.find("meta", attrs={"name": "description"})
            if not meta_desc or not meta_desc.get("content", "").strip():
                warnings.append("Meta description manquante.")
            else:
                desc_len = len(meta_desc.get("content", "").strip())
                if desc_len < 110 or desc_len > 160:
                    warnings.append(f"Meta description hors normes ({desc_len} caract. / recommandé: 110-160).")

            html_tag = soup.find("html")
            if html_tag and not html_tag.get("lang"):
                warnings.append("Attribut 'lang' absent de la balise <html>.")

            if not soup.find("meta", attrs={"name": "viewport"}):
                warnings.append("Balise meta 'viewport' absente (Non responsive mobile).")

            if not soup.find("link", rel=lambda x: x and any(term in x.lower() for term in ["icon", "shortcut icon"])):
                warnings.append("Aucun favicon détecté.")

            if not soup.find("link", attrs={"rel": "canonical"}):
                warnings.append("Balise canonique (<link rel='canonical'>) absente.")

            h1_tags = soup.find_all("h1")
            if len(h1_tags) == 0:
                warnings.append("Aucune balise <h1> détectée.")
            elif len(h1_tags) > 1:
                warnings.append(f"Plusieurs balises <h1> détectées ({len(h1_tags)}).")

            headings = [int(tag.name[1]) for tag in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
            if headings and headings[0] != 1:
                warnings.append(f"La structure commence par un h{headings[0]} au lieu d'un h1.")
            last_level = 0
            for h in headings:
                if last_level > 0 and h > last_level + 1:
                    warnings.append(f"Saut de niveau de titre (h{last_level} vers h{h}).")
                last_level = h

            missing_alt = sum(1 for img in soup.find_all("img") if not img.get("alt") or not img.get("alt").strip())
            if missing_alt > 0:
                warnings.append(f"{missing_alt} image(s) sans attribut 'alt'.")

            for a in soup.find_all("a", href=True):
                href = a["href"]
                full_link = urljoin(url, href)
                if urlparse(base_url).netloc in full_link and not full_link.startswith("mailto:") and not full_link.startswith("tel:"):
                    page_links.append(full_link)

            return True, errors, warnings, list(set(page_links))
        except Exception as e:
            return False, str(e), [], []

    def run_full_scan(self, base_url):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }

        base_url = base_url.rstrip("/")
        self.log(f"[*] Recherche des pages à partir de : {base_url}")

        total_errors = 0
        total_warnings = 0

        robots_url = f"{base_url}/robots.txt"
        try:
            r_resp = requests.get(robots_url, headers=headers, timeout=5)
            if r_resp.status_code == 200:
                self.log("  [✔] Fichier robots.txt trouvé.")
            else:
                self.log(f"  [?] Avertissement : robots.txt absent ou inaccessible (HTTP {r_resp.status_code}).")
                total_warnings += 1
        except Exception:
            pass

        htaccess_url = f"{base_url}/.htaccess"
        try:
            h_resp = requests.get(htaccess_url, headers=headers, timeout=5)
            if h_resp.status_code == 200:
                self.log("  [X] ALERTE SÉCURITÉ : .htaccess accessible publiquement !")
                total_errors += 1
            elif h_resp.status_code in [403, 404]:
                self.log("  [✔] Fichier .htaccess correctement protégé.")
        except Exception:
            pass

        fake_404_url = f"{base_url}/page-test-inexistante-404-xyz123789"
        try:
            f_resp = requests.get(fake_404_url, headers=headers, timeout=5)
            if f_resp.status_code == 404:
                self.log("  [✔] Gestion de la page 404 correcte.")
            elif f_resp.status_code == 200:
                self.log("  [!] Avertissement 'Soft 404' : Une page inexistante renvoie un code 200.")
                total_warnings += 1
        except Exception:
            pass

        urls_to_scan = set()
        urls_to_scan.add(base_url + "/")

        sitemap_url = f"{base_url}/sitemap.xml"
        try:
            self.log(f"[*] Vérification du sitemap : {sitemap_url}")
            sm_resp = requests.get(sitemap_url, headers=headers, timeout=5)
            if sm_resp.status_code == 200:
                sm_soup = BeautifulSoup(sm_resp.text, "html.parser")
                for loc in sm_soup.find_all("loc"):
                    urls_to_scan.add(loc.text.strip())
                self.log(f"[+] Sitemap trouvé ! {len(urls_to_scan)} URL(s) récupérée(s).")
            else:
                self.log("[-] Pas de sitemap.xml, analyse des liens de la page d'accueil...")
                resp = requests.get(base_url, headers=headers, timeout=10)
                for a in BeautifulSoup(resp.text, "html.parser").find_all("a", href=True):
                    full_url = urljoin(base_url + "/", a["href"])
                    if urlparse(full_url).netloc == urlparse(base_url).netloc:
                        urls_to_scan.add(full_url)
        except Exception as e:
            self.log(f"[-] Erreur découverte des pages : {e}")

        total_pages = len(urls_to_scan)
        self.log(f"\n[i] Début du scan de {total_pages} page(s)...")

        all_discovered_links = set()

        for i, page_url in enumerate(list(urls_to_scan), 1):
            self.update_progress(i, total_pages)

            if "google" in page_url and page_url.endswith(".html"):
                continue

            self.log(f"\n[{i}/{total_pages}] Analyse de : {page_url}")

            success, errors, warnings, page_links = self.analyze_page(page_url, headers, base_url)
            all_discovered_links.update(page_links)

            if not success:
                self.log(f"  [X] Erreur de traitement : {errors}")
                total_errors += 1
            else:
                if errors:
                    self.log(f"  [!] {len(errors)} erreur(s) critique(s) :")
                    for err in errors:
                        self.log(f"    • {err}")
                    total_errors += len(errors)
                else:
                    self.log("  [✔] Aucune erreur critique.")

            if warnings:
                self.log(f"  [?] {len(warnings)} avertissement(s) :")
                for warn in warnings:
                    self.log(f"    • {warn}")
                total_warnings += len(warnings)

        self.log("\n[*] Vérification rapide des liens internes...")
        broken_links_count = 0
        for link in list(all_discovered_links)[:25]: 
            try:
                r = requests.head(link, headers=headers, timeout=4)
                if r.status_code >= 400:
                    r = requests.get(link, headers=headers, timeout=4)
                if r.status_code >= 400:
                    self.log(f"  [X] Lien cassé détecté ({r.status_code}) : {link}")
                    broken_links_count += 1
            except Exception:
                pass
        
        if broken_links_count > 0:
            total_warnings += broken_links_count
            self.log(f"  [!] {broken_links_count} lien(s) cassé(s) trouvé(s).")
        else:
            self.log("  [✔] Aucun lien cassé majeur détecté dans l'échantillon.")

        self.log("\n" + "=" * 40)
        self.log("--- RAPPORT FINAL ---")
        self.log(f"Total erreurs : {total_errors} | Total avertissements : {total_warnings}")
        self.log("=" * 40)

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"rapport_scan_{timestamp}.txt"
            content = self.log_area.get(1.0, tk.END)

            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"Rapport d'analyse généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}\n")
                f.write(f"Site analysé : {base_url}\n")
                f.write("-" * 50 + "\n")
                f.write(content)

            self.log(f"\n[+] Rapport enregistré avec succès : {filename}")
        except Exception as exp_err:
            self.log(f"\n[-] Échec de la sauvegarde du rapport : {exp_err}")

        def finalize():
            self.status_label.config(text="Statut : Analyse terminée avec succès !")
            self.btn_start.config(state=tk.NORMAL, bg="#4CAF50")
        self.root.after(0, finalize)


if __name__ == "__main__":
    root = tk.Tk()
    app = SyntaxCheckerApp(root)
    root.mainloop()
