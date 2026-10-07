# Site Checker - Analyse Locale & SEO Avancée

Une application de bureau simple et efficace développée en Python avec **Tkinter** permettant de réaliser un audit complet d'un site web (SEO, performance, sécurité, accessibilité et structure technique).

## 🚀 Fonctionnalités

- **Découverte automatique des pages** : Recherche via le fichier `sitemap.xml` ou, à défaut, par extraction intelligente des liens depuis la page d'accueil.
- **Audit de Sécurité** :
  - Vérification de l'utilisation du protocole HTTPS.
  - Test de sécurité du fichier `.htaccess` (alerte s'il est publiquement accessible).
- **SEO & Optimisation des balises** :
  - Détection des balises `<title>` et `meta description` manquantes ou mal dimensionnées.
  - Vérification de la présence des balises canoniques (`canonical`) et de l'attribut de langue `lang`.
  - Contrôle de la hiérarchie des titres (unicité du `H1` et détection des sauts de niveau).
- **Performance & Compression** :
  - Mesure du temps de chargement des pages.
  - Vérification de l'activation de la compression HTTP (**Gzip / Brotli**).
- **Expérience Utilisateur & Mobile** :
  - Vérification de la présence de la meta `viewport` (Responsive Design).
  - Détection de la présence d'un favicon.
  - Test de la gestion de la page 404 (détection des "Soft 404").
- **Accessibilité & Liens** :
  - Comptage des images dépourvues de l'attribut `alt`.
  - Analyse rapide d'un échantillon de liens internes pour détecter les liens cassés.
- **Sauvegarde automatique** : Génération d'un rapport textuel complet (`rapport_scan_AAAAMMJJ_HHMMSS.txt`) à la fin de chaque scan.
- **Asynchrone** : L'analyse s'exécute dans un thread séparé pour garder l'interface fluide.

## 🛠️ Prérequis

Assurez-vous d'avoir Python 3 installé sur votre machine, ainsi que les bibliothèques nécessaires :

```bash
pip install beautifulsoup4 requests

```

> **Note** : Le module `tkinter` est inclus par défaut avec l'installation standard de Python.

## 💻 Utilisation

1. Clonez ce dépôt ou téléchargez le script de l'application.
2. Lancez l'application en exécutant la commande suivante dans votre terminal :

```bash
python verify_site.py

```

3. Saisissez l'URL complète de votre site (ex: `https://example.com`) et cliquez sur **Scanner le site**.
4. À la fin du scan, retrouvez le fichier de compte-rendu texte généré automatiquement dans le dossier du projet.

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE.txt](https://www.google.com/search?q=LICENSE.txt) pour plus de détails.

```
