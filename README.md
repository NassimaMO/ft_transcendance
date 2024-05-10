# Ft_transcendance

Ce projet consiste à créer un site web pour participer à une compétition du célèbre jeu Pong !

App Authentication
    Gérer l'inscription, la connexion et la gestion des utilisateurs.
    Implémenter la sécurité avec le chiffrement des mots de passe.
    Assurer la protection contre les injections SQL/XSS.
    Mettre en place la connexion HTTPS.
    Valider les formulaires et les entrées utilisateur côté serveur.
App Profil
    Permettre aux utilisateurs de mettre à jour leurs informations de profil.
    Gérer les avatars des utilisateurs.
    Ajouter des amis et afficher leur statut en ligne/hors ligne/en partie.
    Afficher les statistiques des utilisateurs (victoires, défaites, etc.).
    Afficher l'historique des parties pour les utilisateurs authentifiés.
App Tournoi
    Organiser les tournois et gérer le matchmaking des participants.
    Permettre aux joueurs de s'inscrire avec leur alias.
    Annoncer les prochains matchs.
    Afficher l'ordre des joueurs dans le tournoi.
App Pong
    Développer le jeu Pong côté serveur avec ThreeJS/WebGL pour des effets visuels 3D.
    Gérer le gameplay, le mouvement de la balle et le comptage des points.
    Implémenter l'intelligence artificielle pour contrôler l'adversaire.
    Créer une API pour interagir avec le jeu Pong, permettant une utilisation via CLI et une interface web.
App Dashboard
    Fournir des tableaux de bord conviviaux pour les utilisateurs.
    Afficher des statistiques détaillées et des données sur les résultats pour chaque match.
    Afficher des informations sur les propres statistiques des utilisateurs.

Backend :
    - API
        la gestion des utilisateurs, l'authentification, la gestion des tournois, la gestion des statistiques et de l'historique des parties, la communication avec la base de données, modèles 3D Pong, interaction Pong
    - Sécurité
        le chiffrement des mots de passe, la protection contre les injections SQL/XSS, la connexion HTTPS, le multi et la validation des formulaires côté serveur.
    - Scripts JS
        IA Pong, Gamplay Pong
Frontend :
    - Architecture globale du site
    - Affichage pages
        HTML / Bootstrap / CSS / JS
    - Rendu 3D Pong
        Three JS
    - Accesibilité
        compatibilité navigateurs et appareils