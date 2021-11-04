# Journal des modifications

Ressources :
- [Semantic Versioning](http://semver.org/)
- [CHANGELOG recommendations](http://keepachangelog.com/).

## [1.1] - 2021-11-05

### Ajouté

- Début du changelog (premier sprint post-migration)
- Pages :
    - Lien vers la liste des facilitateurs (google doc) sur la page "C'est quoi l'inclusion"
    - Mise en avant des partenaires sur la page d'accueil (carrousel)
- Recherche :
    - Pouvoir filtrer par réseau
- Tech :
    - Pouvoir faire des review apps à la volée sur des PR ouvertes (donnée de test grâce à des fixtures)
    - Afficher un bandeau pour différencier les environnements

### Modifié

- Pages :
    - Quelques mini changements sur la page d'accueil : typo, renommé le bouton Newsletter, meilleur affichage sur mobile
- Recherche :
    - Correctif pour ne pas afficher la modal pour les utilisateurs connectés
    - Correctif pour éviter de renvoyer des doublons
    - Modifié les résultats lorsqu'une ville est cherchée: les structures présentes dans la ville, mais avec périmètre d'intervention autre que Distance ou Département, sont quand même renvoyés
    - Pouvoir chercher par code postal
    - Pouvoir chercher avec plusieurs types de structures à la fois
    - Clarifié le nom du bouton de réinitialisation de la recherche par secteurs
    - Certaines structures n'apparaissaient pas dans les résultats (is_active=False pendant la migration). C'est réparé. Cela concernait ~1000 structures
    - Réparé la redirection lorsqu'une personne non-connectée souhaite télécharger la liste des résultats
- Inscription/connexion :
    - réparé un bug lorsque le lien de réinitialisation du mot de passe était invalide (déjà cliqué)
    - Redirections additionnelles pour les pages de connexion et d'inscription (Cocorico)
- Formulaire de contact :
    - le reply-to est maintenant l'email fourni par l'utilisateur (pour faciliter la réponse sur Zammad)
- API :
    - Pouvoir filtrer les structures par réseau
    - Renvoyer d'avantage d'information dans les détails d'une structure
    - Réorganisation de la documentation

### Supprimé

## [1.0] - 2021-10-26

- Migration de la prod Cocorico vers la prod Django 🚀

## [0.9] - 2021-10

- Ajout des pages espace utilisateur
- Ajout du formulaire de modification d'une structure
- Script de migration des images vers S3
- Recherche géographique complète
- Recherche par plusieurs secteurs
- API : afficher les champs d'origine pour les Siae
- Ajout des différents trackers et tierces parties Javascript

## [0.8] - 2021-09

- Premier script de migration pour récupérer la donnée des Siae, Réseaux, Secteurs, Prestations, Labels et Références
- Ajout du modèle SiaeOffer
- Ajout du modèle SiaeLabel
- Ajout du modèle SiaeClientReference
- Ajout de Flatpages pour créer des pages statiques directement dans l'admin
- Ajout des pages d'accueil, de recherche et de fiche Siae
- Ajout des pages de connexion, inscription & réinitialisation du mot de passe
- Ajout de la page contact
- API : les données des Sector proviennent du nouveau modèle
- API : nouveaux endpoints /siae/kinds & /siae/presta-types
- Outils : ajout des packets django-debug-toolbar & django-extensions
- Outils : ajout d'un template de PR
- Outils : ajout d'un pre-commit
- Outils : ajout de Github Actions
- Màj homepage API
- Correctif SASS Django pour developpement

## [0.7] - 2021-08

- Correctifs docker pour déploiement prod
- Bouge le modèle Siae dans sa propre app. Ajoute des champs manquants. Renomme les DateTimeFields.
- Recrée les modèle Sector & SectorGroup dans leur propre app
- Recrée le modèle Network dans sa propre app
- API : réorganisation du code atour du modèle Siae
- API : préfixe les urls avec /api
- Admin : premiers interfaces pour les modèles Siae et Sector

## [0.6] - 2021-07

- Intégration bootstrap
- Ajout flux de traitement SCSS/SASS
- Intégration theme ITOU
- Composants layout : base, header, footer, layout
- Première page & assets graphiques : c'est quoi l'inclusion
- Compression par défaut des assets CSS & JS

## [0.5] - 2021-07

- Écriture des vues simplifiée (ModelViewSet et Mixins
- Filtres sur certains champs
- Wording et endpoint
- Documentation revue
- Accès SIAE par identifiant et siret
- Ajout pagination sur liste SIAE
- Ajout date de mise à jour liste SIAE
- Nouvelle page d'accueil
- Recherche par plage de date de mise à jour

## [0.4] - 2021-07

- Logging amélioré
- Page d'accueil primitive
- Ajout donnée QPV
- Environnement Docker optimisé

## [0.3.1] - 2021-06

- Correction de la publication des fichiers statiques quand le déboguage de django est désactivé

## [0.3] - 2021-06

- Ajout intergiciel de tracking utilisateur

## [0.2] - 2021-06

- Réorganisation du code (structure fichiers, config, ...
- Utilisation de model.querysets pour les requêtes
- Utilisation contexte du serializer pour "hasher" les identifiants

## [0.1] - 2021-06

- Premiers pas
