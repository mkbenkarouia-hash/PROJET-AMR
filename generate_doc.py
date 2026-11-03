 import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

doc = docx.Document()

# Margins: 0.6 in for professional compact layout
for s in doc.sections:
    s.top_margin = Inches(0.6)
    s.bottom_margin = Inches(0.6)
    s.left_margin = Inches(0.65)
    s.right_margin = Inches(0.65)

# Palette de couleurs corporate / académique
COLOR_PRIMARY = RGBColor(0, 51, 102)     # Bleu nuit
COLOR_SECONDARY = RGBColor(0, 102, 178) # Bleu dynamique
COLOR_DARK = RGBColor(34, 34, 34)       # Texte principal
COLOR_MUTED = RGBColor(100, 100, 100)   # Gris métadonnées

def set_cell_background(cell, hex_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=50, bottom=50, left=70, right=70):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_header(title, level=1):
    h = doc.add_heading(level=level)
    run = h.add_run(title)
    if level == 1:
        run.font.size = Pt(12.5)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(2)
    elif level == 2:
        run.font.size = Pt(10.5)
        run.font.bold = True
        run.font.color.rgb = COLOR_SECONDARY
        h.paragraph_format.space_before = Pt(5)
        h.paragraph_format.space_after = Pt(2)
    return h

def add_code_block(code_text):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F4F5F7")
    set_cell_margins(cell, top=45, bottom=45, left=100, right=100)
    
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="18" w:space="0" w:color="0066B2"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    run = p.add_run(code_text)
    run.font.name = "Consolas"
    run.font.size = Pt(8)
    run.font.color.rgb = RGBColor(20, 20, 20)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def add_callout(text, title="NOTE / JUSTIFICATION :"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "EBF3FA")
    set_cell_margins(cell, top=50, bottom=50, left=90, right=90)
    
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="16" w:space="0" w:color="0055A5"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r_t = p.add_run(f"{title} ")
    r_t.font.bold = True
    r_t.font.size = Pt(8)
    r_t.font.color.rgb = COLOR_PRIMARY
    
    r_b = p.add_run(text)
    r_b.font.size = Pt(8)
    r_b.font.color.rgb = COLOR_DARK
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

# ==================== TITRE DU DOCUMENT ====================
title_p = doc.add_paragraph()
title_p.paragraph_format.space_before = Pt(0)
title_p.paragraph_format.space_after = Pt(1)
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
t_run = title_p.add_run("GUIDE ET RAPPORT TECHNIQUE DE CONFIGURATION")
t_run.font.size = Pt(16)
t_run.font.bold = True
t_run.font.color.rgb = COLOR_PRIMARY

sub_p = doc.add_paragraph()
sub_p.paragraph_format.space_after = Pt(3)
sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub_run = sub_p.add_run("Simulation Robotique Avancée (AMR) : Ubuntu 22.04 LTS (WSL 2), ROS 2 Humble & Gazebo")
sub_run.font.size = Pt(10)
sub_run.font.bold = True
sub_run.font.color.rgb = COLOR_SECONDARY

meta_p = doc.add_paragraph()
meta_p.paragraph_format.space_after = Pt(6)
meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
m_run = meta_p.add_run("Projet : Master Professionnel RAIA • ISET Bizerte | Réf. Rapport : RAIA 01.26 | Encadrement : M. Hmida Hmaied")
m_run.font.size = Pt(8.5)
m_run.font.italic = True
m_run.font.color.rgb = COLOR_MUTED

# Separator line
p_line = doc.add_paragraph()
p_line.paragraph_format.space_after = Pt(6)
p_line_border = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="1" w:color="0055A5"/></w:pBdr>')
p_line._p.get_or_add_pPr().append(p_line_border)

# ==================== 1. CONTEXTE ET TRANSITION AGV -> AMR ====================
add_header("1. Contexte du Projet : Évolution d'un AGV vers un AMR", level=1)
p1 = doc.add_paragraph()
p1.paragraph_format.space_after = Pt(3)
p1.add_run("Le projet initial présenté dans le mémoire ")
p1.add_run("RAIA 01.26").font.bold = True
p1.add_run(" porte sur un système de manutention de cartes électroniques (PCB). La version d'origine est un ")
p1.add_run("AGV (Automated Guided Vehicle)").font.bold = True
p1.add_run(" guidé par une ligne au sol via capteurs infrarouges TCRT5000 et Arduino Uno. L'objectif est de transformer ce robot en un ")
p1.add_run("AMR (Autonomous Mobile Robot)").font.bold = True
p1.add_run(" capable d'opérer sans repère au sol grâce à la cartographie LiDAR 2D, l'odométrie, le SLAM et la navigation autonome dynamique (Nav2). La simulation sous ")
p1.add_run("Gazebo et RViz 2 ").font.bold = True
p1.add_run("constitue le jumeau numérique validant cette transition.")

# Tableau comparatif AGV vs AMR
table = doc.add_table(rows=5, cols=3)
table.alignment = WD_TABLE_ALIGNMENT.CENTER
table.autofit = False

headers = ["Critère", "AGV Initial (Rapport RAIA 01.26)", "Nouvelle Version AMR (Projet)"]
col_widths = [Inches(1.2), Inches(3.0), Inches(3.0)]

for col_idx, text in enumerate(headers):
    cell = table.cell(0, col_idx)
    cell.width = col_widths[col_idx]
    set_cell_background(cell, "003366")
    set_cell_margins(cell, top=35, bottom=35, left=50, right=50)
    p = cell.paragraphs[0]
    r = p.add_run(text)
    r.font.bold = True
    r.font.size = Pt(8)
    r.font.color.rgb = RGBColor(255, 255, 255)

data = [
    ("Guidage", "Ligne optique au sol (TCRT5000 IR)", "Cartographie LiDAR 2D + SLAM (sans ligne au sol)"),
    ("Perception", "Capteurs IR tout-ou-rien + Caméra IMX219", "LiDAR 2D 360°, Encodeurs différentiels, IMU, Caméra"),
    ("Architecture", "Microcontrôleur Arduino Uno (ATmega328P)", "Architecture distribuée : ROS 2 (Cerveau) + microcontrôleur"),
    ("Navigation", "Trajectoire fixe et rigide", "Planification dynamique (Nav2 : Global & Local Planner)")
]

for row_idx, row_data in enumerate(data, start=1):
    bg_color = "F9FAFC" if row_idx % 2 == 1 else "FFFFFF"
    for col_idx, text in enumerate(row_data):
        cell = table.cell(row_idx, col_idx)
        cell.width = col_widths[col_idx]
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=30, bottom=30, left=50, right=50)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        r.font.size = Pt(7.5)
        if col_idx == 0:
            r.font.bold = True

doc.add_paragraph().paragraph_format.space_after = Pt(3)

# ==================== 2. JUSTIFICATION DU CHOIX WSL 2 ====================
add_header("2. Justification Technologique : Pourquoi WSL 2 plutôt que VirtualBox ou Docker ?", level=1)
p_just = doc.add_paragraph()
p_just.paragraph_format.space_after = Pt(3)
p_just.add_run("Dans le cadre du développement de cet AMR, le choix s'est porté sur ")
p_just.add_run("WSL 2 avec WSLg").font.bold = True
p_just.add_run(" plutôt que sur une machine virtuelle classique (VirtualBox) ou des conteneurs (Docker Desktop). Cette décision répond à des impératifs d'ingénierie et de cohérence avec la chaîne d'outils du projet :")

# Argument 1 : VirtualBox
add_header("2.1. Avantages de WSL 2 face à une Machine Virtuelle complète (VirtualBox)", level=2)
p_vb = doc.add_paragraph()
p_vb.paragraph_format.space_after = Pt(2)
p_vb.add_run("• Passerelle directe avec la CAO SolidWorks : ").font.bold = True
p_vb.add_run("La conception mécanique du robot a été réalisée sous SolidWorks (environnement Windows, page 44 du rapport). Avec WSL 2, les systèmes de fichiers Windows et Linux sont nativement fusionnés (/mnt/c/). L'exportation des modèles 3D (fichiers STL, URDF) depuis SolidWorks est utilisable instantanément par Gazebo sans manipulation de dossiers partagés ou de clés USB.\n")
p_vb.add_run("• Accélération 3D native (WSLg) sans émulation logicielle : ").font.bold = True
p_vb.add_run("Gazebo 11 et RViz 2 reposent sur des moteurs graphiques 3D exigeants (OGRE, OpenGL 3.3+). Dans VirtualBox, les pilotes graphiques virtualisés (VBoxSVGA) brident le rendu et causent de fréquentes instabilités. WSL 2 sous Windows 11 utilise la technologie WSLg, qui route directement les appels graphiques vers le GPU physique sans couche de virtualisation lourde.\n")
p_vb.add_run("• Performance du middleware ROS 2 (DDS) : ").font.bold = True
p_vb.add_run("ROS 2 utilise le protocole réseau DDS pour les topics à haute fréquence (LiDAR à 10 Hz, odométrie à 50 Hz). Les couches réseau émulées de VirtualBox (NAT) introduisent des latences qui faussent le calcul des trajectoires de l'AMR.")

# Argument 2 : Docker Desktop
add_header("2.2. Avantages de WSL 2 face à la conteneurisation (Docker Desktop)", level=2)
p_dk = doc.add_paragraph()
p_dk.paragraph_format.space_after = Pt(3)
p_dk.add_run("• Outils interactifs et graphiques vs environnement serveur : ").font.bold = True
p_dk.add_run("Docker est optimisé pour déployer des microservices et serveurs sans interface graphique (headless). Or, le développement d'un AMR nécessite une manipulation visuelle constante : ajustement des mondes Gazebo, téléopération au clavier, visualisation des nuages de points dans RViz. Faire transiter ces interfaces à travers un conteneur Docker sous Windows requiert des configurations d'écrans X11 complexes et fragiles.\n")
p_dk.add_run("• Cycle de développement itératif (Workspace colcon) : ").font.bold = True
p_dk.add_run("La création des packages ROS 2, la compilation via colcon build et le réglage des paramètres de navigation Nav2 sont fluides et persistants dans une distribution Ubuntu résidente, évitant le re-packaging perpétuel d'images Docker.")

add_callout("WSL 2 offre le compromis d'ingénierie idéal : conserver les outils de CAO (SolidWorks) sous Windows tout en exploitant la puissance native du noyau Linux pour les algorithmes robotiques (ROS 2, Gazebo, Nav2).", "SYNTHÈSE DU CHOIX D'ARCHITECTURE :")

# ==================== 3. PHASE 1 : PRÉREQUIS SYSTÈME ====================
add_header("3. Phase 1 : Prérequis Matériels et Système (Windows & BIOS)", level=1)
p2 = doc.add_paragraph()
p2.paragraph_format.space_after = Pt(2)
p2.add_run("Deux étapes fondamentales ont préparé l'ordinateur à accueillir cet environnement :")
doc.add_paragraph("• Espace disque suffisant : Prévoir 25 à 30 Go pour la suite complète ROS 2, Gazebo et les bibliothèques d'analyse.", style='List Bullet')
doc.add_paragraph("• Activation de la virtualisation dans le BIOS : Intel Virtualization Technology (VT-x) activée dans le BIOS HP (System Configuration > Virtualization Technology : <Enabled>) afin d'autoriser l'hyperviseur WSL 2.", style='List Bullet')

# ==================== 4. PHASE 2 : DÉPLOIEMENT D'UBUNTU 22.04 SUR WSL 2 ====================
add_header("4. Phase 2 : Déploiement d'Ubuntu 22.04 LTS (PowerShell)", level=1)
p3 = doc.add_paragraph()
p3.paragraph_format.space_after = Pt(2)
p3.add_run("Commande exécutée dans PowerShell en tant qu'administrateur :")
add_code_block("wsl --install -d Ubuntu-22.04")

p3_expl = doc.add_paragraph()
p3_expl.paragraph_format.space_after = Pt(2)
p3_expl.add_run("Rôle technique : ").font.bold = True
p3_expl.add_run("Active le sous-système WSL 2, télécharge l'image officielle d'Ubuntu 22.04 LTS (Jammy Jellyfish) et initialise le système de fichiers ext4. L'utilisateur configure son compte UNIX et son mot de passe d'administration (sudo).")

# ==================== 5. PHASE 3 : INSTALLATION DE ROS 2, GAZEBO ET NAV2 ====================
add_header("5. Phase 3 : Installation de ROS 2 Humble, Gazebo et Nav2 (Terminal Ubuntu)", level=1)
p4 = doc.add_paragraph()
p4.paragraph_format.space_after = Pt(3)
p4.add_run("Toutes les commandes ont été exécutées dans le terminal Ubuntu. Voici l'explication précise de chacune :")

# Table of commands
tbl_cmd = doc.add_table(rows=1, cols=2)
tbl_cmd.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_cmd.autofit = False

tbl_cmd.cell(0, 0).width = Inches(3.3)
tbl_cmd.cell(0, 1).width = Inches(3.9)
set_cell_background(tbl_cmd.cell(0, 0), "003366")
set_cell_background(tbl_cmd.cell(0, 1), "003366")
set_cell_margins(tbl_cmd.cell(0, 0), top=40, bottom=40, left=60, right=60)
set_cell_margins(tbl_cmd.cell(0, 1), top=40, bottom=40, left=60, right=60)

p_h0 = tbl_cmd.cell(0, 0).paragraphs[0]
r_h0 = p_h0.add_run("Commandes Saisies")
r_h0.font.bold = True
r_h0.font.size = Pt(8)
r_h0.font.color.rgb = RGBColor(255, 255, 255)

p_h1 = tbl_cmd.cell(0, 1).paragraphs[0]
r_h1 = p_h1.add_run("Description et Rôle Technique")
r_h1.font.bold = True
r_h1.font.size = Pt(8)
r_h1.font.color.rgb = RGBColor(255, 255, 255)

commands_list = [
    (
        "sudo apt update && sudo apt upgrade -y",
        "Actualise l'index des paquets logiciels disponibles (apt update) et met à jour les bibliothèques et logiciels du système Ubuntu 22.04 (apt upgrade)."
    ),
    (
        "sudo apt install -y locales\n"
        "sudo locale-gen en_US en_US.UTF-8\n"
        "sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8\n"
        "export LANG=en_US.UTF-8",
        "Configure l'encodage système en UTF-8. ROS 2 exige impérativement un encodage UTF-8 pour sérialiser et parser les messages sans erreur de caractères."
    ),
    (
        "sudo apt install -y software-properties-common curl\n"
        "sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg",
        "Télécharge la clé cryptographique publique officielle d'Open Robotics (ros.key) et la stocke dans le trousseau GPG d'Ubuntu pour certifier l'authenticité des paquets."
    ),
    (
        'echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null',
        "Ajoute le dépôt officiel des paquets ROS 2 Humble aux sources logicielles APT d'Ubuntu pour permettre leur installation via 'apt install'."
    ),
    (
        "sudo apt update\n"
        "sudo apt install -y ros-humble-desktop",
        "Installe le socle logiciel complet de ROS 2 Humble : le middleware DDS, les bibliothèques C++ (rclcpp) et Python (rclpy), les outils CLI (ros2 topic...), et RViz 2."
    ),
    (
        "sudo apt install -y ros-humble-gazebo-ros-pkgs",
        "Installe le simulateur physique 3D Gazebo (Classic 11) et les plugins de communication ROS (transmission différentielle, LiDAR virtuel, caméra, IMU)."
    ),
    (
        "sudo apt install -y ros-humble-navigation2 \\\n"
        "                    ros-humble-nav2-bringup \\\n"
        "                    ros-humble-slam-toolbox \\\n"
        "                    ros-humble-robot-localization \\\n"
        "                    ros-humble-xacro \\\n"
        "                    ros-humble-joint-state-publisher-gui",
        "Installe la pile complète de navigation autonome pour l'AMR :\n"
        "• Nav2 : Planification globale (A*) et évitement d'obstacles en temps réel.\n"
        "• SLAM Toolbox : Cartographie laser 2D en temps réel.\n"
        "• robot_localization : Filtre de Kalman étendu pour fusionner odométrie et IMU.\n"
        "• xacro : Modélisation paramétrable du robot en URDF.\n"
        "• joint_state_publisher_gui : Contrôle manuel des articulations."
    ),
    (
        'echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc\n'
        "source ~/.bashrc",
        "Inscrit automatiquement l'environnement ROS 2 dans le profil utilisateur (.bashrc) pour que toutes les commandes ROS soient disponibles à chaque ouverture de session."
    )
]

for cmd_text, desc_text in commands_list:
    row = tbl_cmd.add_row()
    c0 = row.cells[0]
    c1 = row.cells[1]
    c0.width = Inches(3.3)
    c1.width = Inches(3.9)
    set_cell_background(c0, "F8F9FA")
    set_cell_background(c1, "FFFFFF")
    set_cell_margins(c0, top=30, bottom=30, left=50, right=50)
    set_cell_margins(c1, top=30, bottom=30, left=50, right=50)
    
    p0 = c0.paragraphs[0]
    p0.paragraph_format.space_before = Pt(1)
    p0.paragraph_format.space_after = Pt(1)
    r0 = p0.add_run(cmd_text)
    r0.font.name = "Consolas"
    r0.font.size = Pt(7)
    r0.font.color.rgb = COLOR_DARK
    
    p1 = c1.paragraphs[0]
    p1.paragraph_format.space_before = Pt(1)
    p1.paragraph_format.space_after = Pt(1)
    r1 = p1.add_run(desc_text)
    r1.font.size = Pt(7.5)
    r1.font.color.rgb = COLOR_DARK

doc.add_paragraph().paragraph_format.space_after = Pt(2)

# ==================== 6. PHASE 4 : VALIDATION GRAPHIQUE 3D ====================
add_header("6. Phase 4 : Validation Graphique 3D (WSLg, RViz 2 et Gazebo)", level=1)
p5 = doc.add_paragraph()
p5.paragraph_format.space_after = Pt(2)
p5.add_run("Grâce à ")
p5.add_run("WSLg").font.bold = True
p5.add_run(" (Windows 11), les applications Linux 3D s'ouvrent directement sous Windows avec accélération matérielle.")

add_code_block("rviz2")
p_rviz = doc.add_paragraph()
p_rviz.paragraph_format.space_after = Pt(2)
p_rviz.add_run("Rôle de RViz 2 : ").font.bold = True
p_rviz.add_run("Visualiseur 3D des données capteurs. Permet d'afficher la carte SLAM, les nuages de points LiDAR (/scan), la position estimée (/odom et repères tf) et d'envoyer des objectifs '2D Nav Goal'.")

add_code_block("gazebo")
p_gaz = doc.add_paragraph()
p_gaz.paragraph_format.space_after = Pt(2)
p_gaz.add_run("Rôle de Gazebo : ").font.bold = True
p_gaz.add_run("Simulateur physique 3D qui calcule les équations dynamiques (masse, frottement, inertie, gravité) et simule les interactions mécaniques dans l'atelier.")

add_callout("export MESA_D3D12_DEFAULT_ADAPTER_NAME=Intel  (dans ~/.bashrc)\n"
            "Cette variable force le pilote Mesa Gallium D3D12 à router les requêtes OpenGL de Gazebo directement vers le GPU Intel sous Windows 11 pour garantir un rendu 3D fluide sans blocage.", "OPTIMISATION GPU INTEL :")

# ==================== 7. CONCLUSION ET PROCHAINES ÉTAPES ====================
add_header("7. Passerelle avec le Projet Réel et Prochaines Étapes", level=1)
p6 = doc.add_paragraph()
p6.paragraph_format.space_after = Pt(2)
p6.add_run("Vos fichiers du projet sont directement accessibles depuis Ubuntu via le point de montage Windows :\n")
add_code_block('cd "/mnt/c/Users/khalil/Desktop/STUDY/Bizerte/2eme/PROJET HMIDA"')

p_next = doc.add_paragraph()
p_next.paragraph_format.space_after = Pt(2)
p_next.add_run("Feuille de route pour la suite du projet AMR :\n").font.bold = True
doc.add_paragraph("1. Modélisation URDF/Xacro : Exportation des pièces SolidWorks du robot et création de la structure différentielle.", style='List Bullet')
doc.add_paragraph("2. Intégration des plugins : Configuration du LiDAR 2D virtuel (/scan) et de la commande différentielle (/cmd_vel).", style='List Bullet')
doc.add_paragraph("3. Monde industriel : Modélisation sous Gazebo de l'atelier de manutention des cartes électroniques (PCB).", style='List Bullet')
doc.add_paragraph("4. SLAM & Nav2 : Cartographie laser de l'usine et validation de la navigation autonome avec contournement des obstacles.", style='List Bullet')

doc.save("Guide_Installation_WSL2_ROS2_AMR.docx")
print("Updated DOCX successfully generated with Section 2!")
