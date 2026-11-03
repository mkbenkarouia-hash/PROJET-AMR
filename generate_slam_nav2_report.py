import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

# ══════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION DOCUMENT
# ══════════════════════════════════════════════════════════════════════════════
doc = docx.Document()

for s in doc.sections:
    s.top_margin    = Inches(0.65)
    s.bottom_margin = Inches(0.65)
    s.left_margin   = Inches(0.65)
    s.right_margin  = Inches(0.65)

COLOR_PRIMARY   = RGBColor(0,   51,  102)   # Bleu Nuit
COLOR_SECONDARY = RGBColor(0,  102,  178)   # Bleu Roi
COLOR_SUCCESS   = RGBColor(0,  128,   64)   # Vert validation
COLOR_DARK      = RGBColor(34,  34,   34)
COLOR_MUTED     = RGBColor(100, 100,  100)
COLOR_WHITE     = RGBColor(255, 255,  255)

# ══════════════════════════════════════════════════════════════════════════════
#  FONCTIONS UTILITAIRES
# ══════════════════════════════════════════════════════════════════════════════
def set_cell_background(cell, hex_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd  = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=45, bottom=45, left=65, right=65):
    tcPr  = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def add_header(title, level=1):
    h   = doc.add_heading(level=level)
    run = h.add_run(title)
    if level == 1:
        run.font.size  = Pt(13)
        run.font.bold  = True
        run.font.color.rgb = COLOR_PRIMARY
        h.paragraph_format.space_before = Pt(9)
        h.paragraph_format.space_after  = Pt(2)
    elif level == 2:
        run.font.size  = Pt(11)
        run.font.bold  = True
        run.font.color.rgb = COLOR_SECONDARY
        h.paragraph_format.space_before = Pt(6)
        h.paragraph_format.space_after  = Pt(2)
    return h

def add_body(text, bold_parts=None, space_after=3):
    """Ajoute un paragraphe de corps avec parties optionnellement en gras."""
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(space_after)
    if bold_parts is None:
        r = p.add_run(text)
        r.font.size = Pt(9)
        r.font.color.rgb = COLOR_DARK
    else:
        for fragment, is_bold in bold_parts:
            r = p.add_run(fragment)
            r.font.size = Pt(9)
            r.font.bold = is_bold
            r.font.color.rgb = COLOR_DARK
    return p

def add_code_block(code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F4F5F7")
    set_cell_margins(cell, top=50, bottom=50, left=110, right=110)
    tcPr    = cell._element.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="18" w:space="0" w:color="0066B2"/>'
        f'<w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    p   = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after  = Pt(1)
    run = p.add_run(code_text)
    run.font.name  = "Consolas"
    run.font.size  = Pt(8.5)
    run.font.color.rgb = RGBColor(20, 20, 20)
    doc.add_paragraph().paragraph_format.space_after = Pt(3)

def add_callout(text, title="NOTE TECHNIQUE :", color="EBF3FA", border="0055A5"):
    tbl  = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, color)
    set_cell_margins(cell, top=45, bottom=45, left=90, right=90)
    tcPr    = cell._element.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="16" w:space="0" w:color="{border}"/>'
        f'<w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    p   = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after  = Pt(1)
    r_t = p.add_run(f"{title} ")
    r_t.font.bold  = True
    r_t.font.size  = Pt(8.5)
    r_t.font.color.rgb = COLOR_PRIMARY
    r_b = p.add_run(text)
    r_b.font.size  = Pt(8.5)
    r_b.font.color.rgb = COLOR_DARK
    doc.add_paragraph().paragraph_format.space_after = Pt(3)

def add_table_2col(rows_data, col_widths=(Inches(2.4), Inches(4.8)),
                   header_bg="003366", alt_bg=("F9FAFC", "FFFFFF")):
    """Tableau générique 2 colonnes avec en-tête bleu."""
    tbl = doc.add_table(rows=len(rows_data) + 1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit   = False
    # En-tête : première ligne = clés
    headers = list(rows_data[0].keys())
    for ci, h in enumerate(headers):
        cell = tbl.cell(0, ci)
        cell.width = col_widths[ci]
        set_cell_background(cell, header_bg)
        set_cell_margins(cell, top=40, bottom=40, left=55, right=55)
        r = cell.paragraphs[0].add_run(h)
        r.font.bold = True
        r.font.size = Pt(8)
        r.font.color.rgb = COLOR_WHITE
    for ri, row in enumerate(rows_data, start=1):
        bg = alt_bg[ri % 2]
        for ci, val in enumerate(row.values()):
            cell = tbl.cell(ri, ci)
            cell.width = col_widths[ci]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=35, bottom=35, left=55, right=55)
            r = cell.paragraphs[0].add_run(val)
            r.font.size = Pt(8)
    doc.add_paragraph().paragraph_format.space_after = Pt(3)

def add_separator():
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    border = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'<w:bottom w:val="single" w:sz="6" w:space="1" w:color="C0C8D4"/>'
        f'</w:pBdr>'
    )
    p._p.get_or_add_pPr().append(border)

# ══════════════════════════════════════════════════════════════════════════════
#  EN-TÊTE DU DOCUMENT
# ══════════════════════════════════════════════════════════════════════════════
title_p = doc.add_paragraph()
title_p.paragraph_format.space_before = Pt(0)
title_p.paragraph_format.space_after  = Pt(1)
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
t_run = title_p.add_run("RAPPORT TECHNIQUE — JALON 2 : CARTOGRAPHIE SLAM & NAVIGATION AUTONOME Nav2")
t_run.font.size  = Pt(15)
t_run.font.bold  = True
t_run.font.color.rgb = COLOR_PRIMARY

sub_p = doc.add_paragraph()
sub_p.paragraph_format.space_after = Pt(3)
sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub_r = sub_p.add_run(
    "Implémentation du pipeline complet d'autonomie AMR :\n"
    "Cartographie 2D par slam_toolbox • Navigation par stack Nav2 (AMCL + NavFn + DWB)\n"
    "Plateforme : raia_amr | ROS 2 Humble | Gazebo 11 | WSL2/WSLg"
)
sub_r.font.size  = Pt(9.5)
sub_r.font.bold  = True
sub_r.font.color.rgb = COLOR_SECONDARY

meta_p = doc.add_paragraph()
meta_p.paragraph_format.space_after = Pt(6)
meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
m_run = meta_p.add_run(
    "Master Professionnel RAIA • ISET Bizerte  |  Réf. Mémoire : RAIA 01.26  "
    "|  Encadrement : M. Hmida Hmaied  |  Suite du Rapport de Validation Jalon 1"
)
m_run.font.size   = Pt(8.5)
m_run.font.italic = True
m_run.font.color.rgb = COLOR_MUTED

p_line = doc.add_paragraph()
p_line.paragraph_format.space_after = Pt(6)
border_xml = parse_xml(
    f'<w:pBdr {nsdecls("w")}>'
    f'<w:bottom w:val="single" w:sz="12" w:space="1" w:color="0055A5"/>'
    f'</w:pBdr>'
)
p_line._p.get_or_add_pPr().append(border_xml)

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 5 — CARTOGRAPHIE 2D PAR SLAM
# ══════════════════════════════════════════════════════════════════════════════
add_header("5. Cartographie 2D : SLAM avec slam_toolbox", level=1)

# 5.0 Contexte
add_body(
    "Fort du Jalon 1 validé (simulation Gazebo, RViz 2 et téléopération /cmd_vel "
    "opérationnels), le Jalon 2 engage l'étape de cartographie autonome de l'atelier "
    "d'usine (factory_workshop.world). L'objectif est de produire une "
    "carte de grille d'occupation (Occupancy Grid Map) au format .yaml/.pgm "
    "couvrant l'intégralité du plan de l'usine, qui servira de base fixe à la "
    "navigation autonome Nav2.",
    bold_parts=[
        ("Fort du Jalon 1 validé (simulation Gazebo, RViz 2 et téléopération /cmd_vel "
         "opérationnels), le Jalon 2 engage l'étape de ", False),
        ("cartographie autonome ", True),
        ("de l'atelier d'usine (factory_workshop.world). L'objectif est de produire une ", False),
        ("carte de grille d'occupation (Occupancy Grid Map) ", True),
        ("au format .yaml/.pgm couvrant l'intégralité du plan de l'usine, qui servira "
         "de base fixe à la navigation autonome Nav2.", False),
    ]
)

# ── 5.1 Principe SLAM ─────────────────────────────────────────────────────
add_header("5.1  Principe du SLAM et Flux de Données", level=2)

add_body(
    "Le SLAM (Simultaneous Localization and Mapping) résout le problème "
    "de la poule et de l'œuf : le robot doit connaître sa position pour "
    "construire une carte, et doit avoir une carte pour se localiser. "
    "slam_toolbox (ROS 2) utilise la technique du Graph-Based SLAM :",
    bold_parts=[
        ("Le ", False),
        ("SLAM (Simultaneous Localization and Mapping) ", True),
        ("résout le problème de la poule et de l'œuf : le robot doit connaître "
         "sa position pour construire une carte, et doit avoir une carte pour se "
         "localiser. slam_toolbox (ROS 2) utilise la technique du ", False),
        ("Graph-Based SLAM :", True),
    ]
)

# Tableau principe SLAM
add_table_2col(
    rows_data=[
        {"Étape": "1. Acquisition scan",
         "Description": "Le plugin LiDAR Gazebo publie sur /scan (sensor_msgs/LaserScan) "
                         "à 10 Hz — 360 rayons, portée 0.15–12 m. Le nœud slam_toolbox "
                         "s'abonne à ce topic."},
        {"Étape": "2. Odométrie différentielle",
         "Description": "Le plugin diff_drive publie sur /odom (nav_msgs/Odometry) et "
                         "la transformation TF odom → base_footprint à 30 Hz, fournissant "
                         "l'estimation de déplacement entre scans consécutifs."},
        {"Étape": "3. Scan Matching",
         "Description": "slam_toolbox aligne chaque nouveau scan LiDAR sur la carte "
                         "partielle existante (ICP/NDT) et raffine la pose du robot. "
                         "La résolution de la grille est 0.05 m/cellule."},
        {"Étape": "4. Fermeture de boucle",
         "Description": "Lorsque le robot revisite une zone, le solveur Ceres (Levenberg-"
                         "Marquardt) détecte la boucle et optimise globalement toutes les "
                         "poses du graphe, éliminant la dérive odométrique accumulée."},
        {"Étape": "5. Publication /map",
         "Description": "La carte fusionnée est publiée sur /map "
                         "(nav_msgs/OccupancyGrid) toutes les 5 s "
                         "(map_update_interval) et visualisée en temps réel dans RViz 2."},
    ],
    col_widths=(Inches(2.2), Inches(5.0)),
)

add_callout(
    "Topics clés surveillés durant la cartographie :\n"
    "  /scan       → sensor_msgs/LaserScan     (source principale du SLAM)\n"
    "  /odom       → nav_msgs/Odometry          (prédiction de mouvement)\n"
    "  /map        → nav_msgs/OccupancyGrid     (carte en cours de construction)\n"
    "  /tf         → geometry_msgs/TransformStamped  (arbre map→odom→base_footprint)",
    title="TOPICS ROS 2 ACTIFS :"
)

# ── 5.2 Installation slam_toolbox ──────────────────────────────────────────
add_header("5.2  Installation du Package slam_toolbox", level=2)

add_body(
    "slam_toolbox est disponible dans les dépôts binaires ROS 2 Humble. "
    "Aucune compilation depuis les sources n'est nécessaire :")

add_code_block(
    "# Dans le terminal WSL2 :\n"
    "sudo apt update\n"
    "sudo apt install ros-humble-slam-toolbox\n\n"
    "# Vérifier l'installation :\n"
    "ros2 pkg list | grep slam_toolbox\n"
    "# → slam_toolbox"
)

add_body(
    "Le fichier de paramètres slam_params.yaml (ajouté dans config/) est "
    "calibré pour raia_amr avec les valeurs extraites directement du modèle URDF/Xacro :"
)

# Tableau des paramètres SLAM clés
add_table_2col(
    rows_data=[
        {"Paramètre SLAM":     "base_frame",
         "Valeur / Justification": "base_footprint — repère racine défini dans robot_core.xacro"},
        {"Paramètre SLAM":     "scan_topic",
         "Valeur / Justification": "/scan — topic publié par libgazebo_ros_ray_sensor.so"},
        {"Paramètre SLAM":     "max_laser_range",
         "Valeur / Justification": "12.0 m — aligné avec <max> de lidar.xacro"},
        {"Paramètre SLAM":     "minimum_laser_range",
         "Valeur / Justification": "0.15 m — aligné avec <min> de lidar.xacro"},
        {"Paramètre SLAM":     "resolution",
         "Valeur / Justification": "0.05 m/cellule — standard OGM, suffisant pour châssis 0.56 m"},
        {"Paramètre SLAM":     "minimum_travel_distance",
         "Valeur / Justification": "0.10 m — déclenchement mise à jour tous les 10 cm"},
        {"Paramètre SLAM":     "map_update_interval",
         "Valeur / Justification": "5.0 s — fréquence publication /map (charge CPU WSL2)"},
        {"Paramètre SLAM":     "do_loop_closing",
         "Valeur / Justification": "true — optimisation Ceres activée pour correction dérive"},
        {"Paramètre SLAM":     "loop_search_maximum_distance",
         "Valeur / Justification": "4.0 m — adapté aux allées de l'atelier factory_workshop"},
    ],
    col_widths=(Inches(2.5), Inches(4.7)),
)

# ── 5.3 Lancement de la Cartographie ──────────────────────────────────────
add_header("5.3  Fichier de Lancement et Procédure de Cartographie", level=2)

add_body(
    "Le fichier slam.launch.py (ajouté dans launch/) démarre en une seule commande "
    "les 5 processus nécessaires à la cartographie :"
)

add_table_2col(
    rows_data=[
        {"Processus":          "gzserver + gzclient",
         "Rôle dans slam.launch.py": "Moteur physique + rendu 3D — monde factory_workshop chargé"},
        {"Processus":          "robot_state_publisher",
         "Rôle dans slam.launch.py": "Publie /robot_description et arbre TF statique URDF"},
        {"Processus":          "spawn_entity.py",
         "Rôle dans slam.launch.py": "Insère raia_amr dans la scène Gazebo à (0,0,0.05)"},
        {"Processus":          "async_slam_toolbox_node",
         "Rôle dans slam.launch.py": "Nœud SLAM asynchrone — lit /scan, publie /map et TF map→odom"},
        {"Processus":          "rviz2",
         "Rôle dans slam.launch.py": "Supervise /scan, /map, /tf et la trajectoire robot en temps réel"},
    ],
    col_widths=(Inches(2.3), Inches(4.9)),
)

add_body("Commandes de lancement en séquence :", space_after=2)

add_code_block(
    "# ── TERMINAL 1 : Simulation + SLAM + RViz2 ──────────────────────────────\n"
    "cd ~/ros2_ws\n"
    "colcon build --symlink-install --packages-select raia_amr_description\n"
    "source install/setup.bash\n"
    "ros2 launch raia_amr_description slam.launch.py\n\n"
    "# ── TERMINAL 2 : Téléopération clavier pour explorer l'usine ─────────────\n"
    "source /opt/ros/humble/setup.bash\n"
    "ros2 run teleop_twist_keyboard teleop_twist_keyboard\n"
    "#   i = avancer    ,  = reculer    j/l = rotation    k = stop\n\n"
    "# ── TERMINAL 3 (optionnel) : Vérification du graphe TF ───────────────────\n"
    "ros2 run tf2_tools view_frames\n"
    "# → Génère frames.pdf : map → odom → base_footprint → laser_frame"
)

add_callout(
    "Procédure de cartographie recommandée :\n"
    "  1. Avancer lentement dans les allées principales (vitesse ≤ 0.3 m/s)\n"
    "  2. Tourner progressivement aux intersections (angle ≤ 30°/s)\n"
    "  3. Revenir au point de départ pour déclencher la fermeture de boucle\n"
    "  4. Vérifier dans RViz 2 que la carte est cohérente (pas de murs dédoublés)\n"
    "  5. Attendre la stabilisation de la carte (5–10 s sans mouvement)",
    title="PROCÉDURE CARTOGRAPHIE :"
)

# ── 5.4 Sauvegarde de la Carte ─────────────────────────────────────────────
add_header("5.4  Sauvegarde et Format de la Carte OGM", level=2)

add_body(
    "Une fois la cartographie complète, la carte est sauvegardée via "
    "map_saver_cli du package nav2_map_server :"
)

add_code_block(
    "# ── TERMINAL 4 : Sauvegarde de la carte finale ───────────────────────────\n"
    "source /opt/ros/humble/setup.bash\n"
    "mkdir -p ~/ros2_ws/src/raia_amr_description/maps\n"
    "cd ~/ros2_ws/src/raia_amr_description/maps\n\n"
    "ros2 run nav2_map_server map_saver_cli \\\n"
    "  --ros-args -p map_subscribe_transient_local:=true \\\n"
    "  -f raia_factory_map\n\n"
    "# Résultat : deux fichiers générés dans maps/\n"
    "#   raia_factory_map.yaml   → métadonnées (résolution, origine, seuils)\n"
    "#   raia_factory_map.pgm    → image PGM (blanc=libre, noir=obstacle, gris=inconnu)"
)

add_body("Structure du fichier raia_factory_map.yaml généré :")

add_code_block(
    "image: raia_factory_map.pgm\n"
    "resolution: 0.050000           # m/pixel — correspond à slam_params.yaml\n"
    "origin: [-X0, -Y0, 0.000000]  # pose monde de l'angle inférieur gauche\n"
    "negate: 0\n"
    "occupied_thresh: 0.65          # P(occupé) > 0.65 → cellule noire\n"
    "free_thresh: 0.25              # P(libre) < 0.25  → cellule blanche"
)

add_callout(
    "La carte OGM générée par slam_toolbox est directement compatible avec "
    "le serveur de carte Nav2 (map_server). Elle sera chargée automatiquement "
    "par nav2.launch.py via l'argument --ros-args -p yaml_filename:=raia_factory_map.yaml. "
    "Aucune conversion de format n'est requise.",
    title="COMPATIBILITÉ Nav2 :"
)

add_separator()

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — NAVIGATION AUTONOME Nav2
# ══════════════════════════════════════════════════════════════════════════════
add_header("6. Navigation Autonome : Stack Nav2", level=1)

# 6.0 Intro
add_body(
    "Avec la carte de l'atelier disponible, la plateforme raia_amr entre dans "
    "la phase de navigation autonome. La stack Nav2 (Navigation2) constitue "
    "le système de navigation de référence pour ROS 2. Elle orchestre la "
    "localisation, la planification de trajectoire globale et le contrôle "
    "local du robot en temps réel.",
    bold_parts=[
        ("Avec la carte de l'atelier disponible, la plateforme raia_amr entre dans "
         "la phase de ", False),
        ("navigation autonome", True),
        (". La stack ", False),
        ("Nav2 (Navigation2) ", True),
        ("constitue le système de navigation de référence pour ROS 2. Elle orchestre la "
         "localisation, la planification de trajectoire globale et le contrôle "
         "local du robot en temps réel.", False),
    ]
)

# ── 6.1 Architecture Nav2 ──────────────────────────────────────────────────
add_header("6.1  Architecture de la Stack Nav2", level=2)

add_body("La stack Nav2 est organisée en 4 couches fonctionnelles interdépendantes :")

add_table_2col(
    rows_data=[
        {"Couche Nav2":       "1. Localisation — AMCL",
         "Description & Configuration raia_amr": "Adaptive Monte Carlo Localization : le filtre "
             "particulaire AMCL fusionne les données /scan avec la carte chargée pour estimer la "
             "pose du robot dans le repère map. Paramètre clé : robot_model_type = "
             "DifferentialMotionModel (propulsion différentielle)."},
        {"Couche Nav2":       "2. Costmaps (Global + Local)",
         "Description & Configuration raia_amr": "Grilles de coûts superposées à la carte OGM. "
             "La costmap globale (résolution 0.05 m) planifie sur l'ensemble de l'usine. "
             "La costmap locale (fenêtre 3×3 m, 5 Hz) détecte les obstacles dynamiques. "
             "robot_radius = 0.22 m, inflation_radius = 0.55 m."},
        {"Couche Nav2":       "3. Planificateur global — NavFn",
         "Description & Configuration raia_amr": "NavFn/Dijkstra calcule le chemin optimal "
             "de coût minimal sur la costmap globale. Tolérance : 0.5 m. Compatible "
             "A* (use_astar: true pour atelier dense). Publie le plan sur /plan."},
        {"Couche Nav2":       "4. Contrôleur local — DWB",
         "Description & Configuration raia_amr": "Dynamic Window Approach (DWB) suit le chemin "
             "global en générant des commandes /cmd_vel temps-réel. Contraintes physiques raia_amr : "
             "v_max=0.5 m/s, ω_max=1.0 rad/s, a_max=2.0 m/s² (identique à max_wheel_acceleration)."},
        {"Couche Nav2":       "5. Recovery Behaviors",
         "Description & Configuration raia_amr": "Comportements de récupération automatique en cas "
             "de blocage : Spin (rotation 360° sur place), BackUp (reculer 0.5 m), "
             "Wait (attente 5 s). Gérés par le serveur behavior_server."},
    ],
    col_widths=(Inches(2.3), Inches(4.9)),
)

# ── 6.2 Installation Nav2 ─────────────────────────────────────────────────
add_header("6.2  Installation de la Stack Nav2", level=2)

add_body("Installation des packages Nav2 via les dépôts binaires ROS 2 Humble :")

add_code_block(
    "# Installation complète de Nav2 :\n"
    "sudo apt update\n"
    "sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup\n\n"
    "# Vérification des packages installés :\n"
    "ros2 pkg list | grep nav2\n"
    "# → nav2_amcl, nav2_bt_navigator, nav2_controller, nav2_costmap_2d,\n"
    "#   nav2_map_server, nav2_planner, nav2_behaviors, nav2_bringup, ..."
)

# ── 6.3 Configuration nav2_params.yaml ────────────────────────────────────
add_header("6.3  Configuration nav2_params.yaml — Paramètres Adaptés à raia_amr", level=2)

add_body(
    "Le fichier nav2_params.yaml (ajouté dans config/) est entièrement "
    "calibré à partir des spécifications mécaniques du modèle URDF raia_amr. "
    "Les valeurs critiques issues de gazebo_control.xacro et robot_core.xacro sont :"
)

add_table_2col(
    rows_data=[
        {"Paramètre Nav2":        "max_vel_x (DWB)",
         "Valeur & Source URDF": "0.50 m/s — cohérent avec max_wheel_torque=25 Nm"},
        {"Paramètre Nav2":        "max_vel_theta (DWB)",
         "Valeur & Source URDF": "1.0 rad/s — stabilité gyroscopique châssis 8.5 kg"},
        {"Paramètre Nav2":        "acc_lim_x (DWB)",
         "Valeur & Source URDF": "2.0 m/s² — identique à max_wheel_acceleration dans gazebo_control.xacro"},
        {"Paramètre Nav2":        "wheel_separation (DWB)",
         "Valeur & Source URDF": "0.35 m — wheel_separation de gazebo_control.xacro"},
        {"Paramètre Nav2":        "robot_radius (Costmap)",
         "Valeur & Source URDF": "0.22 m — demi-largeur (0.32/2) + marge 0.06 m"},
        {"Paramètre Nav2":        "inflation_radius (Costmap)",
         "Valeur & Source URDF": "0.55 m — espace de sécurité autour du châssis 0.56 m"},
        {"Paramètre Nav2":        "xy_goal_tolerance (DWB)",
         "Valeur & Source URDF": "0.25 m — précision d'arrêt sur les waypoints"},
        {"Paramètre Nav2":        "base_frame_id (AMCL)",
         "Valeur & Source URDF": "base_footprint — repère racine URDF (robot_core.xacro)"},
        {"Paramètre Nav2":        "scan_topic (AMCL)",
         "Valeur & Source URDF": "/scan — sortie du plugin libgazebo_ros_ray_sensor.so"},
        {"Paramètre Nav2":        "resolution (Costmaps)",
         "Valeur & Source URDF": "0.05 m — même résolution que la carte OGM SLAM"},
    ],
    col_widths=(Inches(2.6), Inches(4.6)),
)

# ── 6.4 Lancement Nav2 ────────────────────────────────────────────────────
add_header("6.4  Lancement de la Navigation Autonome", level=2)

add_body(
    "Le fichier nav2.launch.py démarre la chaîne complète de navigation. "
    "Il requiert la carte OGM préalablement générée par le Jalon SLAM :"
)

add_code_block(
    "# ── TERMINAL 1 : Navigation autonome complète ───────────────────────────\n"
    "cd ~/ros2_ws\n"
    "colcon build --symlink-install --packages-select raia_amr_description\n"
    "source install/setup.bash\n\n"
    "ros2 launch raia_amr_description nav2.launch.py \\\n"
    "  map:=$HOME/ros2_ws/src/raia_amr_description/maps/raia_factory_map.yaml\n\n"
    "# Processus démarrés par nav2.launch.py :\n"
    "#  ✓ gzserver + gzclient       → simulation physique\n"
    "#  ✓ robot_state_publisher      → arbre TF URDF\n"
    "#  ✓ spawn_entity               → insertion raia_amr dans Gazebo\n"
    "#  ✓ nav2_bringup               → stack complète (amcl, bt_navigator,\n"
    "#                                  controller_server, planner_server,\n"
    "#                                  map_server, behavior_server)\n"
    "#  ✓ rviz2                      → interface de supervision Nav2"
)

add_body("Vérification de l'état de la stack Nav2 :")

add_code_block(
    "# ── TERMINAL 2 : Vérification des noeuds Nav2 actifs ────────────────────\n"
    "source /opt/ros/humble/setup.bash\n"
    "ros2 node list | grep -E 'amcl|planner|controller|bt_navigator|map'\n\n"
    "# Résultat attendu :\n"
    "#  /amcl\n"
    "#  /bt_navigator\n"
    "#  /controller_server\n"
    "#  /planner_server\n"
    "#  /map_server\n"
    "#  /behavior_server\n"
    "#  /velocity_smoother\n\n"
    "# Vérification du topic de localisation :\n"
    "ros2 topic echo /amcl_pose --once\n"
    "# → geometry_msgs/PoseWithCovarianceStamped avec pose.pose estimée"
)

# ── 6.5 Envoi de destinations autonomes ────────────────────────────────────
add_header("6.5  Envoi de Destinations Autonomes (2D Nav Goal)", level=2)

add_body(
    "Une fois Nav2 opérationnel et AMCL convergé, le robot peut recevoir des "
    "objectifs de navigation depuis RViz 2 ou en ligne de commande :"
)

add_body("Méthode 1 — Interface RViz 2 (2D Nav Goal) :", space_after=2)

add_code_block(
    "# Dans RViz 2 :\n"
    "# 1. Vérifier que le Fixed Frame est réglé sur 'map'\n"
    "# 2. Initialiser la pose AMCL : cliquer '2D Pose Estimate' → placer le robot\n"
    "# 3. Envoyer un objectif   : cliquer 'Nav2 Goal'          → cliquer destination\n"
    "#    → Nav2 calcule le chemin (NavFn/Dijkstra) et publie sur /cmd_vel\n"
    "#    → Le robot navigue jusqu'à la destination en évitant les obstacles"
)

add_body("Méthode 2 — Ligne de commande (autonome/waypoints) :", space_after=2)

add_code_block(
    "# ── Envoi d'un objectif ponctuel depuis le terminal ──────────────────────\n"
    "ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \\\n"
    "  '{pose: {header: {frame_id: map},\n"
    "   pose: {position: {x: 3.5, y: 2.0, z: 0.0},\n"
    "          orientation: {x: 0.0, y: 0.0, z: 0.707, w: 0.707}}}}'\n\n"
    "# ── Navigation multi-waypoints (tournée d'atelier) ─────────────────────\n"
    "# Script Python utilisant le WaypointFollower Nav2 :\n"
    "#\n"
    "# STATION_A = PoseStamped(map, x=1.5, y= 0.5, θ=0°)   # Poste chargement\n"
    "# STATION_B = PoseStamped(map, x=5.0, y= 2.0, θ=90°)  # Table assemblage\n"
    "# STATION_C = PoseStamped(map, x=5.0, y=-2.0, θ=180°) # Poste déchargement\n"
    "# DOCK      = PoseStamped(map, x=0.0, y= 0.0, θ=0°)   # Base de retour\n"
    "#\n"
    "# nav2_navigator.followWaypoints([STATION_A, STATION_B, STATION_C, DOCK])"
)

add_callout(
    "Vérification de l'arbre TF complet pendant la navigation :\n"
    "  map → odom → base_footprint → base_link → laser_frame\n"
    "La transformation map→odom est publiée par AMCL (localisation). "
    "La transformation odom→base_footprint est publiée par le plugin diff_drive "
    "(odométrie Gazebo). L'absence de l'une des deux transformations provoque "
    "l'erreur 'Could not get transform' dans Nav2.",
    title="ARBRE TF NAVIGATION :"
)

# ── 6.6 Résultats et Métriques attendus ────────────────────────────────────
add_header("6.6  Résultats Attendus et Métriques de Validation", level=2)

add_table_2col(
    rows_data=[
        {"Critère de Validation":  "Convergence AMCL",
         "Valeur Cible / Méthode": "Nuage de particules concentré en < 30 s après "
                                    "initialisation de la pose (2D Pose Estimate). "
                                    "Vérifiable via ros2 topic echo /particlecloud."},
        {"Critère de Validation":  "Précision de localisation",
         "Valeur Cible / Méthode": "Erreur de position < 0.10 m par rapport à la "
                                    "vérité terrain Gazebo (ros2 topic echo /amcl_pose "
                                    "vs. /odom)."},
        {"Critère de Validation":  "Planification de trajectoire",
         "Valeur Cible / Méthode": "Chemin calculé par NavFn en < 500 ms pour une "
                                    "destination à 8 m. Vérifiable via ros2 topic echo /plan."},
        {"Critère de Validation":  "Suivi de trajectoire DWB",
         "Valeur Cible / Méthode": "Déviation maximale < 0.20 m par rapport au chemin "
                                    "global. Contrôleur DWB publie /cmd_vel à 20 Hz."},
        {"Critère de Validation":  "Arrêt sur objectif",
         "Valeur Cible / Méthode": "Le robot s'immobilise à xy_goal_tolerance=0.25 m "
                                    "et yaw_goal_tolerance=0.25 rad de la destination."},
        {"Critère de Validation":  "Évitement d'obstacle dynamique",
         "Valeur Cible / Méthode": "Détection d'un obstacle placé en cours de route, "
                                    "recalcul de trajectoire en < 1 s sans collision."},
        {"Critère de Validation":  "Navigation complète A→B→C→Base",
         "Valeur Cible / Méthode": "Tournée complète des 3 postes de l'atelier "
                                    "via WaypointFollower sans intervention humaine."},
    ],
    col_widths=(Inches(2.6), Inches(4.6)),
)

add_callout(
    "Le succès de ce Jalon 2 représente la transition décisive de l'AMR RAIA "
    "d'un robot téléopéré vers un Autonomous Mobile Robot (AMR) au sens strict : "
    "capacité de se localiser sur une carte, de planifier une trajectoire vers "
    "une destination arbitraire et de l'exécuter en évitant les obstacles, "
    "sans intervention humaine.",
    title="RÉSULTAT JALON 2 :",
    color="E6F4EA",
    border="00803F"
)

add_separator()

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 7 — SYNTHÈSE ET PROCHAINES ÉTAPES
# ══════════════════════════════════════════════════════════════════════════════
add_header("7. Synthèse des Jalons et Roadmap Finale du Projet RAIA 01.26", level=1)

add_table_2col(
    rows_data=[
        {"Jalon":   "[V] Jalon 1 - Simulation Dynamique",
         "Statut & Livrables": "VALIDE. Gazebo 11 + RViz 2 + /cmd_vel. "
                                "Resolution incident WSLg (llvmpipe + modeles locaux). "
                                "Livrables : sim.launch.py, rviz.launch.py, URDF/Xacro complet."},
        {"Jalon":   "[>] Jalon 2 - Cartographie SLAM",
         "Statut & Livrables": "EN COURS. Livrables : slam.launch.py, slam_params.yaml, "
                                "raia_factory_map.yaml/.pgm. "
                                "Procedure : teleoperer l'AMR dans l'atelier puis sauvegarder la carte."},
        {"Jalon":   "[>] Jalon 2 - Navigation Nav2",
         "Statut & Livrables": "EN COURS. Livrables : nav2.launch.py, nav2_params.yaml. "
                                "Validation : navigation autonome A->B->C->Base sans collision."},
        {"Jalon":   "[P] Jalon 3 - Integration Industrielle",
         "Statut & Livrables": "PLANIFIE. Mission multi-waypoints programmee, supervision IHM "
                                "Python, integration systeme MES/ERP de l'atelier ISET Bizerte."},
    ],
    col_widths=(Inches(2.8), Inches(4.4)),
)

add_code_block(
    "# ── Récapitulatif des fichiers ajoutés au package (Jalon 2) ────────────\n"
    "raia_amr_description/\n"
    "├── config/\n"
    "│   ├── slam_params.yaml      ← Paramètres SLAM calibrés pour raia_amr\n"
    "│   ├── nav2_params.yaml      ← Stack Nav2 complète (AMCL, DWB, NavFn...)\n"
    "│   └── rviz_config.rviz      ← Config RViz 2 (existant, Jalon 1)\n"
    "├── launch/\n"
    "│   ├── slam.launch.py        ← Gazebo + SLAM + RViz2 (nouveau)\n"
    "│   ├── nav2.launch.py        ← Gazebo + Nav2 complet + RViz2 (nouveau)\n"
    "│   ├── sim.launch.py         ← Simulation + téléop (existant, Jalon 1)\n"
    "│   └── rviz.launch.py        ← Visualisation seule (existant, Jalon 1)\n"
    "└── maps/\n"
    "    ├── raia_factory_map.yaml ← Métadonnées carte OGM (généré par SLAM)\n"
    "    └── raia_factory_map.pgm  ← Image carte occupation (généré par SLAM)"
)

# ── Pied de page ─────────────────────────────────────────────────────────
p_end = doc.add_paragraph()
p_end.paragraph_format.space_before = Pt(10)
p_end.alignment = WD_ALIGN_PARAGRAPH.CENTER
r_end = p_end.add_run(
    "Rapport généré automatiquement — Master Professionnel RAIA • ISET Bizerte\n"
    "Réf. Mémoire : RAIA 01.26 | Encadrement : M. Hmida Hmaied"
)
r_end.font.size  = Pt(8)
r_end.font.italic = True
r_end.font.color.rgb = COLOR_MUTED

# ══════════════════════════════════════════════════════════════════════════════
#  SAUVEGARDE
# ══════════════════════════════════════════════════════════════════════════════
output_file = "Rapport_SLAM_Nav2_AMR.docx"
doc.save(output_file)
print(f"[OK] Rapport genere avec succes : {output_file}")
print("   Sections couvertes :")
print("   - Section 5  Cartographie SLAM (slam_toolbox)")
print("     5.1 Principe SLAM & flux de donnees")
print("     5.2 Installation & parametres calibres raia_amr")
print("     5.3 slam.launch.py & procedure de cartographie")
print("     5.4 Sauvegarde carte OGM (.yaml/.pgm)")
print("   - Section 6  Navigation Autonome Nav2")
print("     6.1 Architecture 4 couches Nav2")
print("     6.2 Installation nav2_bringup")
print("     6.3 nav2_params.yaml calibres raia_amr")
print("     6.4 nav2.launch.py & lancement")
print("     6.5 Envoi de destinations (RViz2 + CLI + waypoints)")
print("     6.6 Metriques de validation")
print("   - Section 7  Synthese jalons & roadmap RAIA 01.26")
