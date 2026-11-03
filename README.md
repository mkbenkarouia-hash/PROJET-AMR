# 🤖 RAIA AMR 4.0 — Robot Mobile Autonome Industriel
### Système de Navigation Autonome Inter-Lignes de Production CMS & Borne de Recharge Industrielle MiR Charge
**Projet HMIDA — ISET Bizerte | Rapport de Référence RAIA 01.26**

---

![ROS 2](https://img.shields.io/badge/ROS%202-Humble%20%7C%20Jazzy-22314E?logo=ros&logoColor=white)
![Gazebo](https://img.shields.io/badge/Gazebo-11%20ODE-FF6F00?logo=gazebo&logoColor=white)
![Nav2](https://img.shields.io/badge/Nav2-Navigation%20Stack-blue)
![Python](https://img.shields.io/badge/Python-3.10-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-Apache%202.0-green)

---

## 📌 1. Présentation du Projet

Ce projet a pour objectif la conception, la modélisation cinématique, la simulation physique et le déploiement d'un **Robot Mobile Autonome industriel (AMR / AGV)** destiné à l'intralogistique d'un atelier CMS (*Surface Mount Technology*) de fabrication électronique.

L'AMR assure le transfert automatisé, fiable et sans intervention humaine de circuits imprimés (**PCB**) entre les différentes machines de la chaîne de fabrication, et dispose d'un cycle complet de retour à la borne de recharge industrielle **MiR Charge**.

```mermaid
flowchart TD
    subgraph Station_Recharge ["Borne MiR Charge (ST0 - Quai Sud)"]
        S0["En veille 100% | Amarrage 24V DC"]
    end

    subgraph Ligne_1 ["Ligne 1 - Sérigraphie MPM (ST1)"]
        S1["Prise de la carte PCB sérigraphiée"]
    end

    subgraph Ligne_2 ["Ligne 2 - Convoyeur de Transfert (ST2)"]
        S2["Dépose de la carte PCB sur rouleaux"]
    end

    Signal["Appel Opérateur / Superviseur\n/operator_call ou /line_call_button"] -->|Déclenchement| S0
    S0 -->|Départ autonome (0.45 m/s)| S1
    S1 -->|Acheminement inter-lignes| S2
    S2 -->|Retour automatique & Réalignement| S0
```

---

## 🏗️ 2. Architecture Technique

Le système repose sur une architecture modulaire conforme aux standards industriels ROS 2 :

| Composant | Technologie | Rôle dans le système |
| :--- | :--- | :--- |
| **Middleware** | **ROS 2 Humble / Jazzy** | Communication inter-nœuds, actions asynchrones, TF2 |
| **Simulateur Physique** | **Gazebo 11 (ODE)** | Simulation dynamique, contacts sol-roues, inerties, capteurs |
| **Modélisation Robot** | **URDF / Xacro** | Cinématique différentielle, plateaux support PCB, récepteur de charge |
| **Navigation Autonome** | **Nav2 Navigation Stack** | Planification globale (`Navfn`), contrôle local (`RPPC`), Behavior Tree |
| **Localisation** | **AMCL & Odométrie** | Filtre particulaire probabiliste recalé par scan LiDAR 2D |
| **Cartographie** | **SLAM Toolbox** | Occupancy Grid Map (OGM) 2D à résolution 0.05 m/pixel |
| **Supervision Mission** | **Python 3 (`rclpy`)** | Orchestration multi-stations, écoute du bouton d'appel opérateur |

---

## 📐 3. Modélisation du Robot AMR

### Caractéristiques physiques & cinématiques
- **Type de déplacement** : Entraînement différentiel (*Differential Drive*) avec deux roues motrices latérales et deux roues folles libres (*casters*) avant et arrière.
- **Dimensions hors-tout** : Longueur $0.56\text{ m}$, Largeur $0.32\text{ m}$, Hauteur châssis $0.33\text{ m}$.
- **Masse totale** : $9.8\text{ kg}$ (centre de gravité bas pour une stabilité optimale lors des accélérations).
- **Rayon des roues** : $0.05\text{ m}$ ($5\text{ cm}$) | **Empattement** : $0.35\text{ m}$.
- **Charge utile** : Double plateau étagé avec glissières de guidage pour racks de cartes électroniques PCB.

### Capteurs embarqués
- **LiDAR 2D à balayage 360°** (`laser_frame`) : Fréquence $10\text{ Hz}$, portée $12\text{ m}$, résolution angulaire de $1^\circ$, champ complet sans angle mort.
- **Caméra de profondeur RGB-D** (`camera_link`) : Détection d'obstacles bas et volumétriques.
- **Odométrie haute précision** (`/odom`) : Encodeurs de roues couplés au plugin `libgazebo_ros_diff_drive.so`.

### Interface de recharge embarquée (Compatible MiR Charge)
À l'arrière droit du robot se trouve le module récepteur d'amarrage automatique :
- **Plots femelles conducteurs en cuivre** : Raccordement automatique aux broches +24V DC et masse GND.
- **Guide mécanique en V** : Chanfrein de centrage facilitant l'accostage sans frottement destructif.
- **Témoin d'état LED 24V** : Voyant vert fixe confirmant l'amarrage et la liaison de puissance active.
- **Jauge de batterie 5 barres** : Afficheur d'état de charge sur le capot supérieur de l'AMR.

---

## 🏭 4. Atelier Industriel CMS (Digital Twin Gazebo)

L'environnement de production reproduit l'atelier CMS modélisé dans [`worlds/factory_workshop.world`](file:///c:/Users/khalil/Desktop/STUDY/Bizerte/2eme/PROJET%20HMIDA/raia_amr_description/worlds/factory_workshop.world) ($10\text{ m} \times 10\text{ m}$) :

```
     Y (Nord)
     ▲
+5.0 ┼─────────────────────────────────────────────────────────┤
     │   [Ligne 2 - SPEA 4050 IA]         [Ligne 1 - MPM Sérigraphie]
+2.2 │   (-2.80, 2.20)                    (2.80, 2.20)         │
     │                                                         │
+0.65│   === ST2 Convoyeur ===            === ST1 Sérigraphie ===
     │   (-1.80, 0.65, -90°)              (1.80, 0.65, +90°)   │
     │                                                         │
 0.0 ┼─────────────────── [ALLÉE CENTRALE] ───────────────────┼
     │                                                         │
-0.65│   [Zone Logistique/Palettes]       [Ligne 3 - Four ICT] │
-2.2 │   (-2.80, -2.20)                   (2.80, -2.20)        │
     │                                                         │
-3.80│   ===== ST0 BORNE DE RECHARGE INDUSTRIELLE MiR CHARGE =====
-4.68│   (0.00, -3.80, +90° - Quai Sud dégagé le long du mur)  │
-5.0 ┼─────────────────────────────────────────────────────────┤
    -5.0                                                     +5.0 ──► X (Est)
```

### La Borne Industrielle MiR Charge
Conçue selon les standards industriels **Mobile Industrial Robots (MiR)** :
- **Emplacement déporté hors du centre** : Installée en quai mural Sud à $(x=0.00, y=-4.68)$, garantissant que le couloir de circulation central $(0, 0)$ reste libre de tout encombrement.
- **Châssis blanc industriel** surélevé sur deux supports noirs résistants.
- **Façade avec logo MiR** en relief et cavité de préhension centrale.
- **Deux broches horizontales de contact** en saillie sous le logo (24V DC + et GND -).
- **Sas de sécurité au sol** (*AMR Docking Bay*) jaune et noir zébré.

---

## 🔄 5. Déroulement du Cycle de Production Autonome

L'automatisation est orchestrée par [`run_mission.py`](file:///c:/Users/khalil/Desktop/STUDY/Bizerte/2eme/PROJET%20HMIDA/raia_amr_description/run_mission.py) et [`navigation_manager.py`](file:///c:/Users/khalil/Desktop/STUDY/Bizerte/2eme/PROJET%20HMIDA/raia_amr_description/navigation_manager.py) :

1. **Initialisation & Veille** :
   - L'AMR est spawn à son poste de charge ST0 $(0.00, -3.80, +90^\circ)$.
   - Le filtre AMCL se synchronise automatiquement sur la pose initiale.
   - Les plots 24V sont couplés, la batterie est à 100%. L'AMR est en veille sécurisée.
2. **Appel Opérateur de Ligne** :
   - Le système écoute en temps réel sur les topics `/operator_call` (message chaîne) et `/line_call_button` (booléen).
   - Dès réception d'un appel opérateur (ou après 4s de maintien de charge en mode démo automatique), l'ordre de mission est validé, les plots de charge se découplent virtuellement et l'AMR s'élance.
3. **Étape 1 — Prise PCB à la Sérigraphie MPM (ST1)** :
   - L'AMR navigue à $0.45\text{ m/s}$ vers $(1.80, 0.65, +90^\circ)$.
   - Arrêt de précision (écart position $< 18\text{ cm}$).
   - Temporisation de chargement automatique : la carte PCB sérigraphiée est arrimée sur le rack de l'AMR.
4. **Étape 2 — Acheminement & Dépose au Quai Convoyeur (ST2)** :
   - L'AMR franchit l'allée centrale vers $(-1.80, 0.65, -90^\circ)$.
   - Orientation face aux rouleaux du convoyeur de transfert.
   - Temporisation de transfert : la carte PCB est déposée sur le convoyeur motorisé.
5. **Étape 3 — Retour Autonome & Amarrage Borne MiR Charge (ST0)** :
   - L'AMR quitte la ligne 2 et redescend l'allée Sud vers $(0.00, -3.80, +90^\circ)$.
   - Réalignement final face au Nord dans le sas d'amarrage.
   - Connexion automatique aux broches de recharge 24V DC. Statut : *EN VEILLE / PRÊT POUR LA PROCHAINE MISSION*.

---

## ⚙️ 6. Configuration & Paramétrage Nav2

### Contrôleur Local Regulated Pure Pursuit (RPPC)
Dans [`config/nav2_params.yaml`](file:///c:/Users/khalil/Desktop/STUDY/Bizerte/2eme/PROJET%20HMIDA/raia_amr_description/config/nav2_params.yaml) :
- `desired_linear_vel: 0.45 m/s` : Vitesse de croisière nominale en usine.
- `lookahead_dist: 0.50 m` & `min_lookahead_dist: 0.35 m` : Évite toute oscillation ou arrêt prématuré.
- `xy_goal_tolerance: 0.22 m` : Tolérance d'arrivée stricte compatible avec les convoyeurs.
- `failure_tolerance: 10.0 s` : Marge robuste éliminant les faux abandons sous WSL2.
- `max_robot_pose_search_dist: 10.0 m` : Assure le suivi ininterrompu du plan global lors des grands virages.

### Gestion des Costmaps
- **Costmap Locale (4×4 m)** : Fenêtre dynamique d'évitement d'obstacles en temps réel via voxel LiDAR.
- **Costmap Globale (10×10 m)** : Couche statique de la carte d'atelier, couche d'obstacles et rayon d'inflation réglé à $0.28\text{ m}$ pour garantir des couloirs de circulation fluides.

---

## 🚀 7. Guide d'Installation et d'Utilisation

### Prérequis
- Système d'exploitation : **Ubuntu 22.04 LTS** (natif ou via **WSL2** sous Windows 11).
- Distribution : **ROS 2 Humble** ou **ROS 2 Jazzy**.
- Paquets ROS 2 requis :
  ```bash
  sudo apt update
  sudo apt install -y ros-$ROS_DISTRO-navigation2 ros-$ROS_DISTRO-nav2-bringup \
                      ros-$ROS_DISTRO-gazebo-ros-pkgs ros-$ROS_DISTRO-xacro \
                      ros-$ROS_DISTRO-robot-state-publisher ros-$ROS_DISTRO-joint-state-publisher-gui
  ```

### Compilation du package
```bash
# Se placer dans votre workspace ROS 2
cd ~/ros2_ws
colcon build --symlink-install --packages-select raia_amr_description
source install/setup.bash
```

### Lancement de la démonstration 100% automatique
Une seule commande démarre Gazebo, RViz2, la pile Nav2 et exécute le cycle complet :
```bash
cd ~/ros2_ws/src/raia_amr_description
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
bash start_all_and_navigate.sh
```

### Déclenchement manuel par l'opérateur (optionnel)
Pour déclencher manuellement le départ de l'AMR depuis un autre terminal pendant qu'il est en veille à la borne :
```bash
# Appel opérateur classique
ros2 topic pub --once /operator_call std_msgs/msg/String "{data: 'APPEL_LIGNE_1_PCB_PRET'}"

# Ou simulation du bouton physique de ligne
ros2 topic pub --once /line_call_button std_msgs/msg/Bool "{data: true}"
```

---

## 📊 8. Résultats de Validation Technique

Les tests de validation en boucle fermée confirment la fiabilité totale du système :

```
╔═══════════════════════════════════════════════════════════════════╗
║     CYCLE DE PRODUCTION INDUSTRIEL AUTONOME — RAIA AMR 4.0        ║
║     Atelier CMS | factory_workshop.world (Rapport RAIA 01.26)     ║
╚═══════════════════════════════════════════════════════════════════╝

 -> Pose AMR synchronisée : (0.00, -3.80), Cap : 90.0°
 [STATION DE RECHARGE] Robot amarré à la borne industrielle MiR Charge (Quai Sud)
   -> Broches de recharge 24V DC couplées | Tension : 24.3 V | Batterie : 100%

>>> [ÉTAPE 1/3] Départ vers Ligne 1 - Sérigraphie MPM (ST1)
[SUCCÈS] Arrivée confirmée à [ST1] | Écart position : 17.6 cm, Écart cap : 16.0°
✓ [CHARGEMENT PCB TERMINÉ] Circuit imprimé sérigraphié fixé sur le rack.

>>> [ÉTAPE 2/3] Acheminement vers Ligne 2 - Quai Convoyeur (ST2)
[SUCCÈS] Arrivée confirmée à [ST2] | Écart position : 12.3 cm, Écart cap : 16.4°
✓ [DÉCHARGEMENT PCB TERMINÉ] Circuit imprimé transféré sur le convoyeur.

>>> [ÉTAPE 3/3] Retour autonome vers la Station de Recharge (ST0)
[SUCCÈS] Arrivée confirmée à [ST0] | Écart position : 17.2 cm, Écart cap : 18.0°
✓ [CONNEXION 24V DC RÉUSSIE] Amarrage mécanique et recharge en cours.

═══════════════════════════════════════════════════════════════════
 [SUCCÈS TOTAL] Cycle de production inter-lignes 100% VALIDÉ !
═══════════════════════════════════════════════════════════════════
```

---

## 📁 9. Arborescence du Répertoire

```
.
├── config/
│   ├── nav2_params.yaml          # Paramètres centraux Nav2 (RPPC, Costmaps, AMCL, BT)
│   ├── stations.yaml             # Registre des coordonnées exactes des stations industrielles
│   └── rviz_nav2.rviz            # Configuration d'affichage RViz2
├── maps/
│   ├── raia_factory_map.pgm      # Carte d'occupation 2D avec borne MiR Charge
│   └── raia_factory_map.yaml     # Métadonnées géoréférencées de la carte
├── launch/
│   ├── nav2.launch.py            # Lancement unifié Gazebo + Robot + Nav2 + RViz2
│   ├── rsp.launch.py             # Robot State Publisher & parsing Xacro
│   └── online_async_launch.py    # Lancement SLAM Toolbox pour cartographie
├── urdf/
│   ├── robot.urdf.xacro          # Fichier maître URDF de l'AMR
│   ├── robot_core.xacro          # Châssis, roues motrices, casters, récepteur MiR Charge
│   ├── gazebo_control.xacro      # Plugin différentiel Gazebo ODE & odométrie
│   ├── lidar.xacro               # Capteur LiDAR 2D 360°
│   ├── camera.xacro              # Caméra de profondeur RGB-D
│   ├── materials.xacro           # Matériaux et teintes industrielles (cuivre, bleu, blanc MiR)
│   └── inertial_macros.xacro     # Calculs physiques des matrices d'inertie
├── worlds/
│   └── factory_workshop.world    # Monde Gazebo complet : machines CMS, convoyeurs & borne MiR Charge
├── DOCS/                         # Guides d'installation, rapports de validation & présentations
├── navigation_manager.py         # Gestionnaire sécurisé des actions Nav2
├── station_manager.py            # API d'accès aux stations industrielles
├── run_mission.py                # Script exécutif du cycle de production complet
├── start_all_and_navigate.sh     # Script bash de démarrage automatisé
├── CMakeLists.txt                # Configuration de build ament_cmake
├── package.xml                   # Métadonnées du package ROS 2
├── .gitignore                    # Filtres d'exclusion Git
└── README.md                     # Documentation complète du projet
```

---

## 👥 Auteur & Remerciements
- **Projet** : RAIA AMR 4.0 — Intralogistique & Navigation Autonome Industrielle.
- **Cadre** : Projet HMIDA — ISET Bizerte.
- **Référence** : Document RAIA 01.26.
