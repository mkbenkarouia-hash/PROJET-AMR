# 📊 Présentation d'Avancement Technique — AMR RAIA 4.0

Ce dossier contient la présentation complète d'avancement du projet **AMR RAIA 4.0 (ISET Bizerte — Projet HMIDA)**, conçue avec des diapositives synthétiques, des captures d'écran explicatives de la simulation et des notes orateur détaillées pour la soutenance.

---

## 📁 Fichiers Disponibles

| Fichier | Format | Description |
| :--- | :--- | :--- |
| [`Avancement_Projet_AMR_RAIA.pptx`](./Avancement_Projet_AMR_RAIA.pptx) | **PowerPoint (16:9 HD)** | Fichier de présentation officiel modifiable avec cartes graphiques, images intégrées et **notes de l'orateur** sur chaque diapositive (vue Présentateur). |
| [`index.html`](./index.html) | **HTML interactif** | Diaporama web autonome consultable directement dans n'importe quel navigateur (Plein écran avec `F11`, touches `Flèche Gauche` / `Flèche Droite`, et affichage des notes orateur avec la touche `N`). |
| [`generate_pptx.py`](./generate_pptx.py) | **Script Python** | Script de génération automatique de la présentation utilisant `python-pptx`. |
| [`images/`](./images/) | **Dossier Images** | Ensemble des captures d'écran HD annotées issues de la simulation Gazebo / Nav2. |

---

## 🎯 Plan de la Présentation (10 Diapositives)

1. **Diapositive 1 : Couverture & Titre**
   - AMR RAIA 4.0 : Robot Mobile Autonome Industriel.
   - Présentation de l'étudiant (Khalil Ben Karouia) et de l'encadrant (M. Hmida).
2. **Diapositive 2 : Contexte Industriel & Cahier des Charges (Rapport RAIA 01.26)**
   - Transition Usine 4.0, automatisation du transit inter-lignes de cartes PCB, norme ISO 3691-4.
3. **Diapositive 3 : Architecture Système & Pile Logicielle ROS 2 Humble**
   - ROS 2 Humble, Fast-DDS, Gazebo 11 (solveur ODE à 250 Hz), Nav2 avec contrôleur RPPC et AMCL.
4. **Diapositive 4 : Modélisation de l'Atelier CMS & Cartographie (`factory_workshop.world`)**
   - Espace de $10\text{m} \times 10\text{m}$, ST0 (MiR Charge Sud), ST1 (Sérigraphie Est), ST2 (Convoyeur Ouest).
5. **Diapositive 5 : Sécurité Active ISO 3691-4 : Détection Piéton & Alerte Sonore**
   - Détection temps réel par LiDAR 2D, arrêt d'urgence matériel ($d \le 1.05\text{ m}$), diffusion de la mélodie d'alerte (`amr_safety_melody.wav`), reprise automatique.
6. **Diapositive 6 : Évitement Dynamique d'Obstacle Fixe : Contournement du Chariot**
   - Chariot technique au carrefour central, mise à jour des Costmaps, contournement autonome par le couloir Nord ($y \approx 1.25\text{ m}$) avec marge $> 0.60\text{ m}$.
7. **Diapositive 7 : Cycle de Production Inter-Lignes : Transfert de Cartes PCB**
   - Prise en charge à ST1 (sérigraphie MPM, écart 21 cm), transfert et dépose à ST2 (convoyeur, écart 15 cm), traçabilité des étapes sur `/mission_state`.
8. **Diapositive 8 : Station de Recharge Industrielle MiR Charge 24V & Docking Final**
   - Modèle industriel MiR Charge, manœuvre d'alignement de cap ($90^\circ$), amarrage de précision (< 15 cm) et couplage aux plots 24V DC.
9. **Diapositive 9 : Optimisations Techniques & Performance de Simulation (30 FPS)**
   - Résolution de l'écran noir WSLg via serveur virtuel `Xvfb`, allégement du rendu LiDAR, encodage fluide à 30 FPS constants (552 Ko).
10. **Diapositive 10 : Synthèse de l'Avancement & Prochains Jalons**
    - Bilan des résultats validés à 100%, perspectives de déploiement physique réel (châssis, LiDAR réel, STM32 / Jetson, supervision MES).

---

## 🎙️ Utilisation des Notes de l'Orateur

Pour chaque diapositive, des **commentaires orateurs complets** ont été rédigés.
* Dans **PowerPoint** : Utilisez le mode **Présentateur** (`Alt + F5` ou écran étendu) pour lire les commentaires pendant que le jury ne voit que les diapositives épurées.
* Dans le **Diaporama HTML (`index.html`)** : Cliquez sur le bouton **🎙️ Notes de l'Orateur** ou appuyez sur la touche `N` du clavier pour faire apparaître le bandeau de texte oral en bas de l'écran.
