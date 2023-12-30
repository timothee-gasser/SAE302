# SAE302

Ce dépôt GitHub contient les fichiers pour la SAE302.


## Les fichiers sont organisés de la manière suivante :

-**SAE**
  - **Serveur**
    - `SAE302.sql` (importation de la base de données)
    - `SRV.py` (programme principal du serveur)
    - `administration.py` (fonctions annexes pour le serveur)
    - `connect.py` (fonctions de connexion pour le serveur)
    
  - **Client**
    - `Client.py` (Programme client avec interface graphique) [non terminé]
    - `Client_CLI.py` (Programme client sans interface)  

          

   
## Etat d'avencement du projet :


Actuellement, le serveur répond à mes exigences, même si un système de messagerie privée pourrait encore être implémenté.  
Du côté du client, avec une interface graphique, le résultat n'est pas du tout abouti,il manque beaucoup de choses à implémenter, notamment l'interface pour les administrateurs.

## Structure du code :
 
La structure du code est assez chaotique, cela est notamment dû à un développement sur une longue durée avec des évolutions dans la réflexion technique.  

Pour faciliter la compréhension, toute la partie de la connexion des utilisateurs au serveur est déléguée dans le fichier `connect.py`. Quant aux fonctions appelées par les utilisateurs, elles se situent dans le fichier `administratif.py`.  

Malgré une structure de code pas très claire, une docstring complète y est apportée pour aider à la compréhension.

