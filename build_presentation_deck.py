import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ── PALETTE DE COULEURS ──────────────────────────────────────────────
C_NAVY_DARK   = RGBColor(11, 25, 44)      # Fond sombre / Titre
C_NAVY_MED    = RGBColor(19, 42, 74)      # Carte sombre / Bannière
C_BLUE_TECH   = RGBColor(2, 132, 199)     # Bleu électrique / Accent 1
C_ORANGE_IND  = RGBColor(217, 119, 6)     # Ambre / Orange industriel
C_GREEN_VAL   = RGBColor(16, 185, 129)    # Vert émeraude / Validation
C_RED_ALERT   = RGBColor(239, 68, 68)     # Rouge / Alerte
C_SLATE_DARK  = RGBColor(30, 41, 59)      # Texte principal
C_SLATE_MUTED = RGBColor(100, 116, 139)   # Texte secondaire / Muted
C_CARD_BG     = RGBColor(255, 255, 255)   # Fond carte blanc
C_CARD_BORDER = RGBColor(226, 232, 240)   # Bordure carte
C_PAGE_BG     = RGBColor(248, 250, 252)   # Fond slide très clair

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
blank_layout = prs.slide_layouts[6]

def set_slide_background(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, badge_text, title_text, subtitle_text, dark=False):
    # Badge catégorie
    b_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
    tf_b = b_box.text_frame
    tf_b.word_wrap = True
    tf_b.margin_left = tf_b.margin_top = tf_b.margin_right = tf_b.margin_bottom = 0
    p_b = tf_b.paragraphs[0]
    p_b.text = badge_text.upper()
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = C_BLUE_TECH if dark else C_ORANGE_IND
    
    # Titre de la slide
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.72), Inches(11.7), Inches(0.6))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
    p_t = tf_t.paragraphs[0]
    p_t.text = title_text
    p_t.font.size = Pt(22)
    p_t.font.bold = True
    p_t.font.color.rgb = RGBColor(255, 255, 255) if dark else C_NAVY_DARK
    
    # Sous-titre
    s_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.32), Inches(11.7), Inches(0.4))
    tf_s = s_box.text_frame
    tf_s.word_wrap = True
    tf_s.margin_left = tf_s.margin_top = tf_s.margin_right = tf_s.margin_bottom = 0
    p_s = tf_s.paragraphs[0]
    p_s.text = subtitle_text
    p_s.font.size = Pt(12)
    p_s.font.color.rgb = RGBColor(203, 213, 225) if dark else C_SLATE_MUTED

def add_card(slide, left, top, width, height, title="", border_color=C_CARD_BORDER, bg_color=C_CARD_BG):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1.2)
    
    if title:
        # Bannière titre
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.45))
        banner.fill.solid()
        banner.fill.fore_color.rgb = RGBColor(241, 245, 249) if bg_color == C_CARD_BG else RGBColor(30, 58, 102)
        banner.line.color.rgb = border_color
        banner.line.width = Pt(1.0)
        tf_ban = banner.text_frame
        tf_ban.margin_left = Inches(0.15)
        p = tf_ban.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_NAVY_DARK if bg_color == C_CARD_BG else RGBColor(255, 255, 255)
        
        # Textbox contenu dans la carte
        c_box = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.52), width - Inches(0.3), height - Inches(0.58))
    else:
        c_box = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.15), width - Inches(0.3), height - Inches(0.3))
    
    tf = c_box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
    return tf

# ── SLIDE 1 : TITRE & COUVERTURE (DARK THEME) ─────────────────────────
s1 = prs.slides.add_slide(blank_layout)
set_slide_background(s1, C_NAVY_DARK)

# Badge institutionnel
b1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.1), Inches(11.3), Inches(0.5))
tf1_b = b1.text_frame
p = tf1_b.paragraphs[0]
p.text = "INDUSTRIE 4.0 • MASTER PROFESSIONNEL RAIA • ISET BIZERTE"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = C_BLUE_TECH

# Titre Principal
t1 = s1.shapes.add_textbox(Inches(1.0), Inches(1.7), Inches(11.3), Inches(1.6))
tf1_t = t1.text_frame
tf1_t.word_wrap = True
p = tf1_t.paragraphs[0]
p.text = "Vers un AMR Industriel Intelligent"
p.font.size = Pt(36)
p.font.bold = True
p.font.color.rgb = RGBColor(255, 255, 255)

p2 = tf1_t.add_paragraph()
p2.text = "PHASE II : Concrétisation de l'Autonomie sous ROS 2, Gazebo & Nav2"
p2.font.size = Pt(22)
p2.font.bold = True
p2.font.color.rgb = C_ORANGE_IND
p2.space_before = Pt(8)

# Ligne de séparation
line1 = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.0), Inches(3.6), Inches(11.3), Inches(0.04))
line1.fill.solid()
line1.fill.fore_color.rgb = C_BLUE_TECH
line1.line.color.rgb = C_BLUE_TECH

# Description du saut
desc_box = s1.shapes.add_textbox(Inches(1.0), Inches(3.9), Inches(11.3), Inches(1.2))
tf1_d = desc_box.text_frame
tf1_d.word_wrap = True
p = tf1_d.paragraphs[0]
p.text = "Liaison & Amélioration majeure de la Présentation 1 : Validation formelle du Jumeau Numérique, Cartographie SLAM 2D de l'Usine FUBA et Déploiement de la Navigation Autonome Dynamique Nav2."
p.font.size = Pt(14)
p.font.color.rgb = RGBColor(226, 232, 240)

# Carte métadonnées bas
tf_meta = add_card(s1, Inches(1.0), Inches(5.4), Inches(11.3), Inches(1.3), border_color=C_BLUE_TECH, bg_color=C_NAVY_MED)
p = tf_meta.paragraphs[0]
p.text = "Projet RAIA 01.26 — Manutention & Contrôle Qualité PCB • Entreprise Partenaire : FUBA Printed Circuits"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = RGBColor(255, 255, 255)

p_m2 = tf_meta.add_paragraph()
p_m2.text = "Encadrement Académique : M. Hmida Hmaied   |   Étudiant / Présentateur : Ali Ouertani   |   Jalon 2 Validé"
p_m2.font.size = Pt(11)
p_m2.font.color.rgb = RGBColor(148, 163, 184)
p_m2.space_before = Pt(4)

# ── SLIDE 2 : LE FIL CONDUCTEUR — CONTINUITÉ AVEC LA PRÉSENTATION 1 ────
s2 = prs.slides.add_slide(blank_layout)
set_slide_background(s2, C_PAGE_BG)
add_header(s2, "Continuité & Liaison Méthodologique", "Le Fil Conducteur : De la Vision (Présentation 1) à la Réalisation", "Comment cette deuxième phase concrétise chaque promesse et résout chaque verrou initial")

# 3 Colonnes comparatives
# Col 1: Présentation 1
tf_p1 = add_card(s2, Inches(0.8), Inches(1.9), Inches(3.7), Inches(5.0), title="1. Présentation 1 : Le Diagnostic Initial", border_color=RGBColor(203, 213, 225))
p = tf_p1.paragraphs[0]
p.text = "Preuve de Concept (PoC) AGV :"
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK

bullets_p1 = [
    "Robot suiveur de ligne à base d'Arduino Uno (8-bit) et capteurs TCRT5000.",
    "Inspection visuelle PCB par caméra HD + YOLOv8 INT8 sur Raspberry Pi 4.",
    "Supervision Flask pour suivi unitaire.",
    "Constat critique : Goulet d'étranglement mécatronique (2 Ko RAM) et rigidité logistique absolue du filoguidage."
]
for b in bullets_p1:
    p = tf_p1.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_SLATE_DARK
    p.space_before = Pt(4)

# Col 2: Le Pivot Stratégique
tf_p2 = add_card(s2, Inches(4.8), Inches(1.9), Inches(3.7), Inches(5.0), title="2. Le Pivot Stratégique Formulé", border_color=C_ORANGE_IND)
p = tf_p2.paragraphs[0]
p.text = "La Promesse de Rupture :"
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_ORANGE_IND

bullets_p2 = [
    "Transition du modèle AGV passif vers l'AMR autonome sans repère au sol.",
    "Développement d'un Jumeau Numérique complet sous Gazebo & ROS 2.",
    "Suppression du risque financier : Valider toute l'autonomie en simulation avant investissement matériel.",
    "Objectif : Cartographie SLAM 2D, planification globale/locale et évitement d'obstacles en temps réel."
]
for b in bullets_p2:
    p = tf_p2.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_SLATE_DARK
    p.space_before = Pt(4)

# Col 3: Présentation 2 (Résultats)
tf_p3 = add_card(s2, Inches(8.8), Inches(1.9), Inches(3.7), Inches(5.0), title="3. Présentation 2 : Livrables & Validation", border_color=C_GREEN_VAL)
p = tf_p3.paragraphs[0]
p.text = "Les Jalons Définitivement Validés :"
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = C_GREEN_VAL

bullets_p3 = [
    "Jalon 1 Validé : Modèle URDF complet de raia_amr, atelier usine Gazebo et chaîne dynamique opérationnelle.",
    "Jalon 2 Validé : Carte SLAM haute fidélité (raia_factory_map.pgm, res 0.05 m) et pile Nav2 opérationnelle.",
    "Tournée d'atelier multi-waypoints accomplie sans aucune ligne au sol.",
    "Résolution d'incidents techniques réels (WSLg / GPU Mesa D3D12)."
]
for b in bullets_p3:
    p = tf_p3.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_SLATE_DARK
    p.space_before = Pt(4)

# ── SLIDE 3 : RAPPEL DES VERROUS TECHNIQUES (PRÉSENTATION 1) ───────────
s3 = prs.slides.add_slide(blank_layout)
set_slide_background(s3, C_PAGE_BG)
add_header(s3, "Analyse des Contraintes Initiales", "Rappel des Verrous Techniques Identifiés en Présentation 1", "Les limites fondamentales qui imposaient le saut technologique vers ROS 2 et l'AMR")

tf_v1 = add_card(s3, Inches(0.8), Inches(1.9), Inches(3.7), Inches(4.8), title="Verrou 1 : La Rigidité du Filoguidage", border_color=C_RED_ALERT)
bullets_v1 = [
    "Esclave de l'infrastructure : Le robot AGV est strictement asservi à une bande adhésive au sol.",
    "Dégradation mécanique : Passage intensif des chariots élévateurs FUBA détériorant les bandes au sol.",
    "Blocage systématique : Face au moindre obstacle imprévu, l'AGV s'arrête net et paralyse la ligne logistique.",
    "Coût de reconfiguration : Modifier un circuit impose d'arrêter l'usine et de redessiner physiquement les trajectoires."
]
for i, b in enumerate(bullets_v1):
    p = tf_v1.paragraphs[0] if i == 0 else tf_v1.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_SLATE_DARK
    p.space_before = Pt(6)

tf_v2 = add_card(s3, Inches(4.8), Inches(1.9), Inches(3.7), Inches(4.8), title="Verrou 2 : L'Étranglement Mécatronique", border_color=C_RED_ALERT)
bullets_v2 = [
    "Microcontrôleur 8-bit saturé : ATmega328P avec seulement 2 Ko de SRAM et 16 MHz d'horloge.",
    "Boucle mono-tâche bloquante : loop() gère simultanément les PWM moteurs et les capteurs sans priorisation.",
    "Absence de connectivité native : Câblage USB indispensable, aucun protocole Wi-Fi / BLE industriel.",
    "Incompatibilité structurelle : Impossible d'exécuter un OS Temps Réel (RTOS) ni d'embarquer des nœuds ROS 2."
]
for i, b in enumerate(bullets_v2):
    p = tf_v2.paragraphs[0] if i == 0 else tf_v2.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_SLATE_DARK
    p.space_before = Pt(6)

tf_v3 = add_card(s3, Inches(8.8), Inches(1.9), Inches(3.7), Inches(4.8), title="Verrou 3 : Le Risque d'Investissement", border_color=C_ORANGE_IND)
bullets_v3 = [
    "Coût d'un LiDAR industriel : Risqué à acquérir sans certitude sur l'adaptation aux allées étroites de FUBA.",
    "Risque de casse mécanique : Les algorithmes de navigation ne peuvent être testés directement sur le plancher d'usine.",
    "Nécessité d'un Jumeau Numérique : Besoin impératif de simuler la cinématique, les contacts et la dynamique.",
    "Solution adoptée : Modélisation complète sous Gazebo 11 + ROS 2 Humble sans dépenser un euro de matériel."
]
for i, b in enumerate(bullets_v3):
    p = tf_v3.paragraphs[0] if i == 0 else tf_v3.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_SLATE_DARK
    p.space_before = Pt(6)

# Bandeau bas de transition
tf_trans = add_card(s3, Inches(0.8), Inches(6.8), Inches(11.7), Inches(0.5), border_color=C_BLUE_TECH, bg_color=C_NAVY_MED)
p = tf_trans.paragraphs[0]
p.text = "DECISION D'INGENIEUR : Déployer une plateforme de simulation avancée (WSL 2 + ROS 2) pour lever ces trois verrous."
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = RGBColor(255, 255, 255)

# ── SLIDE 4 : PILIER 1 — L'INFRASTRUCTURE LOGICIELLE WSL 2 & ROS 2 ─────
s4 = prs.slides.add_slide(blank_layout)
set_slide_background(s4, C_PAGE_BG)
add_header(s4, "Infrastructure Technique (Guide Technique & Installation)", "Pilier 1 : Le Choix Stratégique WSL 2 & ROS 2 Humble", "Une architecture d'ingénierie optimisée pour la cohabitation CAO Windows et calcul robotique Linux")

# Carte gauche : Justification comparative
tf_just = add_card(s4, Inches(0.8), Inches(1.9), Inches(6.0), Inches(5.1), title="Justification de WSL 2 face aux alternatives")
comparisons = [
    ("WSL 2 vs VirtualBox (Machine Virtuelle classique) :", [
        "Consommation mémoire divisée par 2 grâce à l'allocation dynamique du noyau Linux.",
        "Accélération 3D native via WSLg et le pilote Mesa D3D12 (accès direct au GPU Intel / NVIDIA).",
        "Latence d'exécution 5x plus faible, évitant les saccades du moteur physique de Gazebo."
    ]),
    ("WSL 2 vs Docker Desktop (Conteneurisation) :", [
        "Affichage graphique 3D sans configurer de ponts X11 complexes et instables.",
        "Cycle de développement colcon build rapide et persistant sans rebuilder d'images Docker.",
        "Accès direct aux périphériques USB et aux ports de communication série."
    ])
]
for title_comp, points in comparisons:
    p = tf_just.add_paragraph()
    p.text = title_comp
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_before = Pt(4)
    for pt in points:
        p = tf_just.add_paragraph()
        p.text = "  • " + pt
        p.font.size = Pt(10)
        p.font.color.rgb = C_SLATE_DARK
        p.space_before = Pt(2)

# Carte droite : Architecture déployée
tf_env = add_card(s4, Inches(7.1), Inches(1.9), Inches(5.4), Inches(5.1), title="Environnement Déployé & Optimisations")
env_items = [
    ("Système Hôte & Matériel", "Windows 11 Professionnel, BIOS HP avec Intel VT-x activé, 30 Go alloués."),
    ("Distribution Linux Embarquée", "Ubuntu 22.04 LTS sous noyau WSL 2 (version kernel 5.15+)."),
    ("Framework Robotique", "ROS 2 Humble Hawksbill (Desktop-Full) avec colcon build et ament_python."),
    ("Simulateur Dynamique", "Gazebo 11 (gazebo_ros_pkgs) + visualiseur 3D RViz 2."),
    ("Optimisation Graphique Clé", "export MESA_D3D12_DEFAULT_ADAPTER_NAME=Intel et LLVMpipe configurés dans ~/.bashrc pour éliminer les instabilités d'affichage.")
]
for name, desc in env_items:
    p = tf_env.add_paragraph()
    p.text = name + " :"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_TECH
    p.space_before = Pt(6)
    p = tf_env.add_paragraph()
    p.text = desc
    p.font.size = Pt(10)
    p.font.color.rgb = C_SLATE_DARK

# ── SLIDE 5 : JALON 1 — LE JUMEAU NUMÉRIQUE DE L'AMR (URDF / XACRO) ────
s5 = prs.slides.add_slide(blank_layout)
set_slide_background(s5, C_PAGE_BG)
add_header(s5, "Jalon 1 : Modélisation Physique (Rapport de Validation)", "Conception du Jumeau Numérique de l'AMR RAIA", "Modélisation géométrique, inertielle et cinématique différentielle sous URDF/Xacro")

# Colonne gauche : Propriétés Châssis & Moteurs
tf_chassis = add_card(s5, Inches(0.8), Inches(1.9), Inches(4.5), Inches(5.1), title="Structure & Cinématique Différentielle")
c_specs = [
    ("Châssis Principal (base_link)", "Dimensions 0.56 m x 0.32 m x 0.11 m, masse 8.5 kg. Pare-chocs arrondis inspirés de la maquette physique."),
    ("Repère Racine (base_footprint)", "Projeté au sol sous le centre géométrique, joint fixe avec base_link (z = 0.05 m)."),
    ("Roues Motrices Différentielles", "2 roues gauche/droite : rayon r = 0.05 m, voie d = 0.35 m, masse 0.45 kg. Couples moteurs max de 25 Nm."),
    ("Roues Folles (Caster Wheels)", "2 billes stabilisatrices avant et arrière (r = 0.025 m) avec frottement quasi-nul pour empêcher le tangage."),
    ("Plugin Diff Drive (Gazebo)", "libgazebo_ros_diff_drive.so : écoute sur /cmd_vel, calcule les vitesses roues et publie /odom et la transformée TF odom->base_footprint.")
]
for title_sp, text_sp in c_specs:
    p = tf_chassis.add_paragraph()
    p.text = title_sp + " :"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_before = Pt(4)
    p = tf_chassis.add_paragraph()
    p.text = text_sp
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_SLATE_DARK

# Colonne milieu : Instrumentation Capteurs
tf_sens = add_card(s5, Inches(5.5), Inches(1.9), Inches(4.0), Inches(5.1), title="Perception Capteurs Embarquée")
sens_items = [
    ("LiDAR 2D 360° (laser_frame)", "Plugin libgazebo_ros_ray_sensor.so.\n• Fréquence de balayage : 10 Hz\n• Portée : 0.12 m à 12.00 m\n• Résolution : 360 échantillons (1°)\n• Publication : topic /scan\n• Rôle : Cartographie SLAM & détection des obstacles."),
    ("Caméra Industrielle (camera_link)", "Plugin libgazebo_ros_camera.so.\n• Résolution : 640x480 à 30 FPS\n• Topic : /camera/image_raw\n• Rôle : Préparée pour le contrôle optique des PCB par YOLOv8."),
    ("Arbre de Transformations (TF)", "Cohérence spatiale garantie :\nmap → odom → base_footprint → base_link → laser_frame & camera_link.")
]
for title_s, text_s in sens_items:
    p = tf_sens.add_paragraph()
    p.text = title_s + " :"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_TECH
    p.space_before = Pt(6)
    p = tf_sens.add_paragraph()
    p.text = text_s
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_SLATE_DARK

# Colonne droite : Image du Robot PoC
tf_img = add_card(s5, Inches(9.7), Inches(1.9), Inches(2.8), Inches(5.1), title="Maquette PoC RAIA")
if os.path.exists("scratch/robot_poc_crop.png"):
    s5.shapes.add_picture("scratch/robot_poc_crop.png", Inches(9.9), Inches(2.5), width=Inches(2.4))
p = tf_img.add_paragraph()
p.space_before = Pt(210)
p.text = "Modèle CAO / Physique fidèlement retranscrit en modèle Xacro dynamique avec calcul rigoureux des matrices d'inertie."
p.font.size = Pt(9.5)
p.font.color.rgb = C_SLATE_MUTED

# ── SLIDE 6 : JALON 1 — L'ATELIER FUBA (FACTORY_WORKSHOP.WORLD) ────────
s6 = prs.slides.add_slide(blank_layout)
set_slide_background(s6, C_PAGE_BG)
add_header(s6, "Environnement Virtuel (Rapport de Validation)", "Modélisation de l'Atelier Industriel FUBA", "Création sous Gazebo 11 du monde factory_workshop.world répliquant les contraintes d'usine")

# Carte gauche : Description du monde
tf_w = add_card(s6, Inches(0.8), Inches(1.9), Inches(5.8), Inches(5.1), title="Configuration de l'Atelier de Fabrication PCB")
world_specs = [
    ("Postes de Travail & Lignes d'Assemblage", "Modélisation des tables de montage, convoyeurs et postes de contrôle qualité conformes à la disposition FUBA."),
    ("Rayonnages & Allées de Circulation", "Délimitation d'allées de 1.5 m à 2.5 m de largeur, simulant les zones de stockage des composants et les racks de PCB bruts."),
    ("Conditions Physiques & Dynamiques ODE", "• Gravité : z = -9.81 m/s²\n• Friction de contact pneus / sol : mu = 1.2, mu2 = 1.2\n• Pas d'intégration physique : step time 1 ms (1000 Hz) garantissant un contact stable sans oscillation."),
    ("Validation des Collisions", "Chaque obstacle possède une enveloppe de collision rigide. Le châssis raia_amr ne peut traverser aucun mobilier.")
]
for title_w, desc_w in world_specs:
    p = tf_w.add_paragraph()
    p.text = title_w + " :"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_before = Pt(6)
    p = tf_w.add_paragraph()
    p.text = desc_w
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_SLATE_DARK

# Image droite : Rendu Gazebo / RViz
tf_wimg = add_card(s6, Inches(6.8), Inches(1.9), Inches(5.7), Inches(5.1), title="Jumeau Numérique en Action (Gazebo & RViz 2)")
if os.path.exists("scratch/gazebo_rviz_crop.png"):
    s6.shapes.add_picture("scratch/gazebo_rviz_crop.png", Inches(7.0), Inches(2.5), width=Inches(5.3))
p = tf_wimg.add_paragraph()
p.space_before = Pt(210)
p.text = "Vue synchronisée : À gauche, simulation physique sous Gazebo (atelier FUBA). À droite, perception temps réel du robot sous RViz 2 (impacts LiDAR rouges sur les murs et tables)."
p.font.size = Pt(10)
p.font.color.rgb = C_SLATE_MUTED

# ── SLIDE 7 : JALON 1 — RÉSOLUTION D'INCIDENTS CRITIQUES (RCA) ─────────
s7 = prs.slides.add_slide(blank_layout)
set_slide_background(s7, C_PAGE_BG)
add_header(s7, "Résolution de Problème & Démarche d'Ingénieur", "Jalon 1 : Analyse et Résolution de l'Incident WSLg", "Preuve de maturité technique : Détection, diagnostic de cause racine (RCA) et résolution de l'écran noir Gazebo")

# 3 Colonnes : Problème -> Analyse -> Solution
tf_rca1 = add_card(s7, Inches(0.8), Inches(1.9), Inches(3.7), Inches(4.5), title="1. Symptôme & Alerte", border_color=C_RED_ALERT)
bullets_rca1 = [
    "Écran noir complet au démarrage de Gazebo sous WSLg.",
    "L'interface utilisateur freeze et refuse de charger les modèles 3D.",
    "Blocage du pipeline de validation de la cinématique.",
    "Erreur de communication graphique OpenGL / Wayland."
]
for i, b in enumerate(bullets_rca1):
    p = tf_rca1.paragraphs[0] if i == 0 else tf_rca1.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_SLATE_DARK
    p.space_before = Pt(8)

tf_rca2 = add_card(s7, Inches(4.8), Inches(1.9), Inches(3.7), Inches(4.5), title="2. Analyse Cause Racine (RCA)", border_color=C_ORANGE_IND)
bullets_rca2 = [
    "Cause 1 (Rendu GPU) : Le pilote Mesa Gallium D3D12 échouait à allouer les contextes de shaders OpenGL pour Gazebo sous WSL 2.",
    "Cause 2 (Réseau) : Gazebo tentait de contacter models.gazebosim.org à chaque lancement, causant un timeout bloquant de 60 s.",
    "Conclusion : Le système s'interrompait avant même de charger l'URDF du robot."
]
for i, b in enumerate(bullets_rca2):
    p = tf_rca2.paragraphs[0] if i == 0 else tf_rca2.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_SLATE_DARK
    p.space_before = Pt(8)

tf_rca3 = add_card(s7, Inches(8.8), Inches(1.9), Inches(3.7), Inches(4.5), title="3. Solutions Implémentées", border_color=C_GREEN_VAL)
bullets_rca3 = [
    "Solution GPU : Forçage du rendu logiciel robuste LLVMpipe via export LIBGL_ALWAYS_SOFTWARE=1.",
    "Solution Modèles : Mise en cache locale des modèles (~/.gazebo/models) et coupure de l'accès distant via GAZEBO_MODEL_DATABASE_URI=\"\".",
    "Automatisation : Variables injectées directement dans launch.py et bashrc."
]
for i, b in enumerate(bullets_rca3):
    p = tf_rca3.paragraphs[0] if i == 0 else tf_rca3.add_paragraph()
    p.text = "• " + b
    p.font.size = Pt(10.5)
    p.font.color.rgb = C_SLATE_DARK
    p.space_before = Pt(8)

# Bilan Jalon 1
tf_j1_end = add_card(s7, Inches(0.8), Inches(6.6), Inches(11.7), Inches(0.65), border_color=C_GREEN_VAL, bg_color=RGBColor(240, 253, 244))
p = tf_j1_end.paragraphs[0]
p.text = "RÉSULTAT DU JALON 1 : VALIDÉ À 100% — Lancement fluide via sim.launch.py, pilotage téléopéré /cmd_vel, arbre TF odom->base_footprint parfait et nuage laser actif dans RViz 2."
p.font.size = Pt(11)
p.font.bold = True
p.font.color.rgb = RGBColor(22, 101, 52)

# ── SLIDE 8 : JALON 2 — FIN DU FILOGUIDAGE : CARTOGRAPHIE SLAM 2D ──────
s8 = prs.slides.add_slide(blank_layout)
set_slide_background(s8, C_PAGE_BG)
add_header(s8, "Jalon 2 : Cartographie Laser (Rapport SLAM & Nav2)", "Fin du Filoguidage : Cartographie SLAM 2D avec slam_toolbox", "Création de la carte d'occupation de l'usine FUBA par balayage laser 360° sans repère physique au sol")

# Colonne gauche : Principe & Paramètres
tf_slam = add_card(s8, Inches(0.8), Inches(1.9), Inches(5.8), Inches(5.1), title="Calibration & Procédure SLAM")
slam_points = [
    ("Package Retenu", "slam_toolbox (mode en-ligne asynchrone) : Idéal pour les ateliers industriels, gère les fermetures de boucle (loop closure) et la pose-graph optimization."),
    ("Résolution Spatiale Métrique", "resolution = 0.05 m (5 cm par pixel) : Permet de distinguer nettement les pieds de tables, rayonnages et passages étroits."),
    ("Portée Utile LiDAR", "min_laser_range = 0.12 m, max_laser_range = 12.00 m : Rejet des échos parasites proches et portée suffisante pour traverser l'atelier."),
    ("Procédure de Génération", "L'AMR a été téléopéré à basse vitesse (0.2 m/s) à travers l'atelier virtuel. Les scans LiDAR ont été fusionnés avec l'odométrie pour construire la grille."),
    ("Livrables de Sortie", "raia_factory_map.pgm (image matrice) et raia_factory_map.yaml (métadonnées d'origine [-5.05, -4.93, 0] et seuils d'occupation 0.65 / 0.25).")
]
for title_sl, text_sl in slam_points:
    p = tf_slam.add_paragraph()
    p.text = title_sl + " :"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_before = Pt(4)
    p = tf_slam.add_paragraph()
    p.text = text_sl
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_SLATE_DARK

# Colonne droite : Image de la Carte Générée
tf_map_img = add_card(s8, Inches(6.8), Inches(1.9), Inches(5.7), Inches(5.1), title="Carte OGM Réelle Générée (raia_factory_map)")
if os.path.exists("scratch/raia_factory_map_hires.png"):
    s8.shapes.add_picture("scratch/raia_factory_map_hires.png", Inches(7.5), Inches(2.5), width=Inches(4.3))
p = tf_map_img.add_paragraph()
p.space_before = Pt(245)
p.text = "Grille d'occupation 2D (OGM) : Zones noires = cloisons et obstacles fixes. Zones blanches = allées de circulation libres. Le robot n'a plus besoin d'aucun ruban au sol !"
p.font.size = Pt(10)
p.font.color.rgb = C_SLATE_MUTED

# ── SLIDE 9 : JALON 2 — ARCHITECTURE DE LA STACK Nav2 ──────────────────
s9 = prs.slides.add_slide(blank_layout)
set_slide_background(s9, C_PAGE_BG)
add_header(s9, "Jalon 2 : Navigation Autonome (Rapport SLAM & Nav2)", "Architecture de la Stack de Navigation Nav2", "Les 5 briques logicielles fondamentales assurant l'autonomie totale et l'évitement d'obstacles")

cards_nav2 = [
    ("1. Localisation AMCL", "Adaptive Monte Carlo Localization : Estime en temps réel la position (x, y, θ) du robot par filtre particulaire en confrontant le LiDAR à la carte OGM. Publie sur /amcl_pose.", C_BLUE_TECH),
    ("2. Costmaps 2D (Cartes de Coût)", "Génère deux cartes de coût dynamiques (globale et locale). Intègre les obstacles détectés par laser et applique une marge d'inflation de sécurité de 0.55 m autour du robot.", C_BLUE_TECH),
    ("3. Planificateur Global (NavFn)", "Algorithme Dijkstra / A* : Calcule en moins de 500 ms le chemin optimal reliant la position courante à la destination demandée en évitant les zones d'inflation.", C_BLUE_TECH),
    ("4. Contrôleur Local (DWB)", "Dynamic Window Approach : Échantillonne l'espace des vitesses à 20 Hz et génère les commandes /cmd_vel réelles en respectant les limites physiques (v_max = 0.5 m/s, a_max = 2.0 m/s²).", C_ORANGE_IND),
    ("5. Navigateur BT & Comportements de Secours", "Behavior Tree Navigator : Supervise l'exécution des missions. En cas de blocage, déclenche automatiquement des comportements de secours : Spin (rotation 360°), BackUp (recul 0.5 m), Wait (5 s).", C_GREEN_VAL)
]
for i, (c_title, c_text, border_c) in enumerate(cards_nav2):
    row = i // 3
    col = i % 3
    left = Inches(0.8 + col * 3.95)
    top = Inches(1.9 + row * 2.55)
    w = Inches(3.8)
    h = Inches(2.35)
    tf_c = add_card(s9, left, top, w, h, title=c_title, border_color=border_c)
    p = tf_c.paragraphs[0]
    p.text = c_text
    p.font.size = Pt(10)
    p.font.color.rgb = C_SLATE_DARK

# 6ème boîte : Schéma flux TF
tf_tf = add_card(s9, Inches(8.7), Inches(4.45), Inches(3.8), Inches(2.35), title="Arbre TF Complet de Navigation", border_color=C_NAVY_DARK, bg_color=RGBColor(241, 245, 249))
p = tf_tf.paragraphs[0]
p.text = "Chaîne cinématique active :\nmap  ──(AMCL)──>  odom  ──(Diff Drive)──>  base_footprint  ──>  base_link  ──>  laser_frame"
p.font.size = Pt(10)
p.font.bold = True
p.font.color.rgb = C_NAVY_DARK
p2 = tf_tf.add_paragraph()
p2.text = "Garantit que chaque point LiDAR est positionné avec une précision centimétrique dans le référentiel de l'usine."
p2.font.size = Pt(9.5)
p2.font.color.rgb = C_SLATE_MUTED
p2.space_before = Pt(6)

# ── SLIDE 10 : JALON 2 — CALIBRATION PHYSIQUE NAV2 & URDF ──────────────
s10 = prs.slides.add_slide(blank_layout)
set_slide_background(s10, C_PAGE_BG)
add_header(s10, "Paramétrage Dynamique (nav2_params.yaml)", "Calibration Nav2 Déduite de la Physique du Robot", "Concordance mathématique stricte entre le modèle URDF réel et les paramètres de contrôle")

# Table de correspondance Nav2
table_shape = s10.shapes.add_table(8, 3, Inches(0.8), Inches(1.9), Inches(11.7), Inches(4.5))
table = table_shape.table
table.columns[0].width = Inches(2.8)
table.columns[1].width = Inches(2.2)
table.columns[2].width = Inches(6.7)

headers = ["Paramètre Nav2", "Valeur Calibrée", "Justification Physique / Source URDF"]
for col_idx, h_text in enumerate(headers):
    cell = table.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = C_NAVY_DARK
    p = cell.text_frame.paragraphs[0]
    p.text = h_text
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

table_data = [
    ("max_vel_x (DWB)", "0.50 m/s", "Cohérent avec le couple moteur 25 Nm et la sécurité des opérateurs en atelier."),
    ("max_vel_theta (DWB)", "1.00 rad/s", "Stabilité gyroscopique du châssis de 8.5 kg lors des pivots sur place."),
    ("acc_lim_x (DWB)", "2.00 m/s²", "Identique à max_wheel_acceleration défini dans gazebo_control.xacro."),
    ("wheel_separation (DWB)", "0.35 m", "Entraxe géométrique exact des roues motrices dans robot_core.xacro."),
    ("robot_radius (Costmaps)", "0.22 m", "Demi-largeur du robot (0.32/2 = 0.16 m) augmentée d'une marge de sécurité de 0.06 m."),
    ("inflation_radius (Costmaps)", "0.55 m", "Zone tampon empêchant l'AMR de frôler les rayonnages ou les postes de travail."),
    ("xy_goal_tolerance", "0.25 m", "Précision requise pour l'arrêt automatique devant le convoyeur d'inspection PCB.")
]
for row_idx, row_items in enumerate(table_data):
    for col_idx, item in enumerate(row_items):
        cell = table.cell(row_idx + 1, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(255, 255, 255) if row_idx % 2 == 0 else RGBColor(248, 250, 252)
        p = cell.text_frame.paragraphs[0]
        p.text = item
        p.font.size = Pt(10)
        p.font.color.rgb = C_NAVY_DARK if col_idx < 2 else C_SLATE_DARK
        if col_idx == 1:
            p.font.bold = True

tf_foot = add_card(s10, Inches(0.8), Inches(6.6), Inches(11.7), Inches(0.6), border_color=C_BLUE_TECH, bg_color=RGBColor(240, 249, 255))
p = tf_foot.paragraphs[0]
p.text = "RÉSULTAT : Zéro décalage entre la théorie cinématique et le comportement réel en simulation."
p.font.size = Pt(10.5)
p.font.bold = True
p.font.color.rgb = C_BLUE_TECH

# ── SLIDE 11 : SCÉNARIO INDUSTRIEL — LA TOURNÉE MULTI-WAYPOINTS ────────
s11 = prs.slides.add_slide(blank_layout)
set_slide_background(s11, C_PAGE_BG)
add_header(s11, "Validation Opérationnelle (Rapport SLAM & Nav2)", "Scénario Industriel Validé : La Tournée d'Atelier FUBA", "Simulation complète de la boucle de manutention autonome des PCB entre les postes de production")

waypoints = [
    ("1. Station A : Chargement PCB", "x = 1.5 m, y = 0.5 m, θ = 0°", "Prise en charge des paniers de circuits imprimés bruts en sortie de gravure. Positionnement précis devant le convoyeur.", C_BLUE_TECH),
    ("2. Station B : Contrôle Qualité", "x = 5.0 m, y = 2.0 m, θ = 90°", "Poste d'inspection optique automatisée. L'AMR s'immobilise pour permettre à la caméra et à YOLOv8 d'analyser les PCB.", C_ORANGE_IND),
    ("3. Station C : Déchargement", "x = 5.0 m, y = -2.0 m, θ = 180°", "Acheminement des cartes validées conformes vers la zone de conditionnement et d'expédition finale.", C_GREEN_VAL),
    ("4. Base Dock : Recharge & Attente", "x = 0.0 m, y = 0.0 m, θ = 0°", "Retour automatique à la station de stationnement pour recharge de la batterie en attendant le prochain ordre de mission.", C_NAVY_DARK)
]
for i, (title_w, coord_w, desc_w, border_w) in enumerate(waypoints):
    col = i % 2
    row = i // 2
    left = Inches(0.8 + col * 5.9)
    top = Inches(1.9 + row * 2.5)
    w = Inches(5.7)
    h = Inches(2.3)
    tf_w = add_card(s11, left, top, w, h, title=title_w, border_color=border_w)
    p = tf_w.paragraphs[0]
    p.text = "Coordonnées de l'objectif : " + coord_w
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = border_w
    p2 = tf_w.add_paragraph()
    p2.text = desc_w
    p2.font.size = Pt(9.5)
    p2.font.color.rgb = C_SLATE_DARK
    p2.space_before = Pt(4)
    p3 = tf_w.add_paragraph()
    p3.text = "Évitement d'obstacle : En cas d'obstacle sur le trajet, Nav2 recalcule une déviation en < 1 seconde."
    p3.font.size = Pt(9)
    p3.font.color.rgb = C_SLATE_MUTED
    p3.space_before = Pt(4)

# ── SLIDE 12 : RÉSULTATS CHIFFRÉS & KPI DE VALIDATION ──────────────────
s12 = prs.slides.add_slide(blank_layout)
set_slide_background(s12, C_PAGE_BG)
add_header(s12, "Métriques de Performance (Rapport SLAM & Nav2)", "Résultats Quantitatifs et Métriques de Validation", "Preuves expérimentales de la précision, de la stabilité et de la réactivité du système de navigation")

kpis = [
    ("< 30 s", "Convergence AMCL", "Nuage de particules stabilisé dès les premiers mètres parcourus."),
    ("< 0.10 m", "Précision de Localisation", "Écart moyen entre la pose estimée par AMCL et la vérité terrain Gazebo."),
    ("< 500 ms", "Temps de Planification", "Calcul complet du chemin NavFn pour une trajectoire de 8 m à travers l'usine."),
    ("< 0.20 m", "Écart Suivi de Trajectoire", "Déviation maximale du contrôleur DWB par rapport au plan global idéal."),
    ("< 1.0 s", "Évitement Dynamique", "Temps de détection et replanification face à un obstacle inattendu."),
    ("100%", "Succès de la Tournée", "Mission A → B → C → Dock accomplie sans blocage ni intervention humaine.")
]
for i, (val, title_kpi, desc_kpi) in enumerate(kpis):
    col = i % 3
    row = i // 3
    left = Inches(0.8 + col * 3.95)
    top = Inches(1.9 + row * 2.5)
    w = Inches(3.8)
    h = Inches(2.3)
    tf_k = add_card(s12, left, top, w, h, border_color=C_BLUE_TECH)
    p = tf_k.paragraphs[0]
    p.text = val
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_TECH
    p2 = tf_k.add_paragraph()
    p2.text = title_kpi
    p2.font.size = Pt(12)
    p2.font.bold = True
    p2.font.color.rgb = C_NAVY_DARK
    p2.space_before = Pt(2)
    p3 = tf_k.add_paragraph()
    p3.text = desc_kpi
    p3.font.size = Pt(9.5)
    p3.font.color.rgb = C_SLATE_MUTED
    p3.space_before = Pt(4)

# ── SLIDE 13 : CONVERGENCE GLOBALE : AMR NAV2 & VISION IA YOLOV8 ───────
s13 = prs.slides.add_slide(blank_layout)
set_slide_background(s13, C_PAGE_BG)
add_header(s13, "Synergie Globale (Liaison Présentation 1)", "Convergence des Deux Cerveaux : Navigation Nav2 & IA YOLOv8", "Comment l'AMR autonome s'interface avec le module de détection de défauts présenté en Phase 1")

# Carte gauche : Le Cerveau Navigation
tf_nav = add_card(s13, Inches(0.8), Inches(1.9), Inches(5.8), Inches(5.1), title="1. Cerveau Logistique : ROS 2 & Nav2")
nav_points = [
    ("Mission Autonome", "Acheminement automatique des paniers de circuits imprimés d'une station à une autre sans dépendre d'un tracé physique."),
    ("Arrêt de Précision", "Accostage à ± 0.25 m devant le banc d'inspection optique (Station B), garantissant que le PCB entre parfaitement dans le cône de vision de la caméra."),
    ("Communication Inter-Systèmes", "Dès l'arrivée à destination, Nav2 notifie la réussite du jalon (/navigate_to_pose action succeeded), déclenchant l'analyse qualité.")
]
for title_np, desc_np in nav_points:
    p = tf_nav.add_paragraph()
    p.text = title_np + " :"
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_TECH
    p.space_before = Pt(6)
    p = tf_nav.add_paragraph()
    p.text = desc_np
    p.font.size = Pt(9.5)
    p.font.color.rgb = C_SLATE_DARK

# Carte droite : Le Cerveau IA + Image Défauts
tf_ai = add_card(s13, Inches(6.8), Inches(1.9), Inches(5.7), Inches(5.1), title="2. Cerveau Qualité : YOLOv8 & Supervision")
ai_points = [
    ("Détection Temps Réel (30 FPS)", "Modèle YOLOv8 INT8 optimisé analysant la surface du PCB en 33 ms pour 3 anomalies critiques :"),
    ("  • Défaut 503", "Salissures et décolorations des vias de conduction."),
    ("  • Défaut 521", "Ponts de soudure indésirables (risques de court-circuit)."),
    ("  • Défaut 522", "Composants CMS endommagés, manquants ou désalignés."),
    ("Traçabilité Unitaire Flask", "Enregistrement SQL : ID carte, statut (Conforme/Non-Conforme), date/heure et position exacte dans l'usine.")
]
for title_a, desc_a in ai_points:
    p = tf_ai.add_paragraph()
    p.text = title_a + ("" if title_a.startswith(" ") else " :")
    p.font.size = Pt(10)
    p.font.bold = not title_a.startswith(" ")
    p.font.color.rgb = C_ORANGE_IND if title_a.startswith(" ") else C_NAVY_DARK
    p.space_before = Pt(4)
    if desc_a:
        p2 = tf_ai.add_paragraph()
        p2.text = desc_a
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = C_SLATE_DARK

# ── SLIDE 14 : MATRICE COMPARATIVE AVANT / APRÈS ───────────────────────
s14 = prs.slides.add_slide(blank_layout)
set_slide_background(s14, C_PAGE_BG)
add_header(s14, "Synthèse de l'Évolution (Présentation 1 vs Présentation 2)", "Matrice Comparative : L'Évolution Majeure du Projet", "Bilan exhaustif du saut technologique accompli entre le prototype initial et le standard industriel")

# Table comparative
table2_shape = s14.shapes.add_table(7, 3, Inches(0.8), Inches(1.9), Inches(11.7), Inches(4.6))
table2 = table2_shape.table
table2.columns[0].width = Inches(2.6)
table2.columns[1].width = Inches(4.5)
table2.columns[2].width = Inches(4.6)

headers2 = ["Critère de Comparaison", "AGV Initial (Présentation 1 / PFE)", "AMR Réalisé (Présentation 2 / Jalon 2)"]
for col_idx, h_text in enumerate(headers2):
    cell = table2.cell(0, col_idx)
    cell.fill.solid()
    cell.fill.fore_color.rgb = C_NAVY_DARK if col_idx != 2 else C_BLUE_TECH
    p = cell.text_frame.paragraphs[0]
    p.text = h_text
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = RGBColor(255, 255, 255)

comp_data = [
    ("Mode de Guidage", "Filoguidage rigide par ligne adhésive au sol (TCRT5000 IR).", "Cartographie laser SLAM 2D + Navigation autonome Nav2 (Zéro infra)."),
    ("Architecture Calcul", "Arduino Uno 8-bit, 2 Ko RAM, boucle bloquante mono-tâche.", "ROS 2 Humble, nœuds asynchrones multi-threads, jumeau numérique."),
    ("Comportement Obstacles", "Arrêt complet et passif (blocage de la ligne de production).", "Détection laser 360° et re-planification active de trajectoire (< 1 s)."),
    ("Flexibilité d'Atelier", "Modifier le tracé exige de stopper l'usine et recoller les bandes.", "Reconfiguration logicielle immédiate par simple envoi de waypoints."),
    ("Mécanique & Masse", "Châssis maquette léger sans validation inertielle formelle.", "Châssis 8.5 kg, roues motrices 25 Nm, physique ODE réaliste simulée."),
    ("Maturité Système", "Prototype d'expérimentation de laboratoire.", "Système AMR au standard Industrie 4.0 prêt pour déploiement physique.")
]
for row_idx, row_items in enumerate(comp_data):
    for col_idx, item in enumerate(row_items):
        cell = table2.cell(row_idx + 1, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(255, 255, 255) if row_idx % 2 == 0 else RGBColor(248, 250, 252)
        p = cell.text_frame.paragraphs[0]
        p.text = item
        p.font.size = Pt(9.5)
        p.font.color.rgb = C_NAVY_DARK if col_idx == 0 else (C_RED_ALERT if col_idx == 1 else C_GREEN_VAL)
        if col_idx == 0:
            p.font.bold = True

tf_foot2 = add_card(s14, Inches(0.8), Inches(6.6), Inches(11.7), Inches(0.6), border_color=C_GREEN_VAL, bg_color=RGBColor(240, 253, 244))
p = tf_foot2.paragraphs[0]
p.text = "CONCLUSION COMPARATIVE : Transition réussie d'un suiveur de ligne scolaire vers un véritable AMR industriel."
p.font.size = Pt(10.5)
p.font.bold = True
p.font.color.rgb = RGBColor(22, 101, 52)

# ── SLIDE 15 : PERSPECTIVES — VERS LE ROBOT PHYSIQUE (JALON 3) ─────────
s15 = prs.slides.add_slide(blank_layout)
set_slide_background(s15, C_PAGE_BG)
add_header(s15, "Feuille de Route Finale (Rapport SLAM/Nav2)", "Perspectives : Déploiement Physique & Intégration Industrielle", "Jalon 3 : Les étapes planifiées pour porter les algorithmes validés en simulation sur le robot physique")

persp_cards = [
    ("1. Architecture ESP32 & micro-ROS", "Remplacement de l'Arduino par le microcontrôleur ESP32 double-cœur (240 MHz). Déploiement de FreeRTOS : Cœur 0 dédié à l'asservissement PID des moteurs, Cœur 1 dédié au pont micro-ROS Wi-Fi communicant avec ROS 2.", C_BLUE_TECH),
    ("2. Intégration du LiDAR Physique", "Montage d'un capteur télémètre laser 2D (ex: RPLiDAR A1 ou A2) sur le dessus du robot, connecté en USB au Raspberry Pi 4 pour publier directement sur le topic /scan.", C_BLUE_TECH),
    ("3. Supervision Web Intégrée", "Couplage de l'IHM Flask avec les actions Nav2 : L'opérateur peut sélectionner une commande sur l'écran web, le robot part chercher le panier et les résultats YOLOv8 s'affichent en temps réel.", C_ORANGE_IND),
    ("4. Essais en Conditions Réelles (FUBA)", "Tests de validation sur le plancher de l'usine FUBA : Déplacement au milieu du personnel, gestion des perturbations lumineuses et liaison continue avec l'ERP d'atelier.", C_GREEN_VAL)
]
for i, (title_p, desc_p, border_p) in enumerate(persp_cards):
    col = i % 2
    row = i // 2
    left = Inches(0.8 + col * 5.9)
    top = Inches(1.9 + row * 2.5)
    w = Inches(5.7)
    h = Inches(2.3)
    tf_p = add_card(s15, left, top, w, h, title=title_p, border_color=border_p)
    p = tf_p.paragraphs[0]
    p.text = desc_p
    p.font.size = Pt(10)
    p.font.color.rgb = C_SLATE_DARK

# ── SLIDE 16 : CONCLUSION GÉNÉRALE & CLÔTURE (DARK THEME) ──────────────
s16 = prs.slides.add_slide(blank_layout)
set_slide_background(s16, C_NAVY_DARK)

b16 = s16.shapes.add_textbox(Inches(1.0), Inches(1.0), Inches(11.3), Inches(0.5))
tf16_b = b16.text_frame
p = tf16_b.paragraphs[0]
p.text = "SYNTHÈSE DE LA DÉMARCHE D'INGÉNIEUR"
p.font.size = Pt(12)
p.font.bold = True
p.font.color.rgb = C_BLUE_TECH

t16 = s16.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(11.3), Inches(1.0))
tf16_t = t16.text_frame
p = tf16_t.paragraphs[0]
p.text = "Conclusion : Un Saut Technologique Concrétisé"
p.font.size = Pt(30)
p.font.bold = True
p.font.color.rgb = RGBColor(255, 255, 255)

# 3 Cartes de bilan final
tf_end1 = add_card(s16, Inches(1.0), Inches(2.8), Inches(3.6), Inches(3.4), title="1. Promesse Tenue", border_color=C_GREEN_VAL, bg_color=C_NAVY_MED)
p = tf_end1.paragraphs[0]
p.text = "Tous les verrous soulevés en Présentation 1 (rigidité du filoguidage, limites 8-bit de l'Arduino) ont trouvé une réponse technique concrète, simulée et validée sous ROS 2."
p.font.size = Pt(11)
p.font.color.rgb = RGBColor(226, 232, 240)

tf_end2 = add_card(s16, Inches(4.9), Inches(2.8), Inches(3.6), Inches(3.4), title="2. Rigueur & Économie", border_color=C_BLUE_TECH, bg_color=C_NAVY_MED)
p = tf_end2.paragraphs[0]
p.text = "Grâce au Jumeau Numérique Gazebo / WSL 2, l'ensemble de la pile SLAM et Nav2 a été calibré avec des tolérances millimétriques sans risquer de budget matériel initial."
p.font.size = Pt(11)
p.font.color.rgb = RGBColor(226, 232, 240)

tf_end3 = add_card(s16, Inches(8.8), Inches(2.8), Inches(3.6), Inches(3.4), title="3. Prêt pour l'Industrie 4.0", border_color=C_ORANGE_IND, bg_color=C_NAVY_MED)
p = tf_end3.paragraphs[0]
p.text = "L'alliance de la navigation autonome Nav2, de l'inspection optique par IA (YOLOv8) et de la traçabilité unitaire place l'AMR RAIA au niveau des standards industriels les plus exigeants."
p.font.size = Pt(11)
p.font.color.rgb = RGBColor(226, 232, 240)

# Message de fin
end_box = s16.shapes.add_textbox(Inches(1.0), Inches(6.4), Inches(11.3), Inches(0.6))
tf_eb = end_box.text_frame
p = tf_eb.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
p.text = "Merci pour votre attention — Place aux échanges et questions."
p.font.size = Pt(15)
p.font.bold = True
p.font.color.rgb = RGBColor(255, 255, 255)

out_file = "PRESENTATION_2_AMELIORATION_AMR_ROS2.pptx"
prs.save(out_file)
print(f"Presentation saved successfully as '{out_file}' with {len(prs.slides)} slides.")
