import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

doc = docx.Document()

# Marges harmonieuses (0.65 in = 1.65 cm)
for s in doc.sections:
    s.top_margin = Inches(0.65)
    s.bottom_margin = Inches(0.65)
    s.left_margin = Inches(0.65)
    s.right_margin = Inches(0.65)

COLOR_PRIMARY = RGBColor(0, 51, 102)     # Bleu Nuit
COLOR_SECONDARY = RGBColor(0, 102, 178) # Bleu Roi
COLOR_DARK = RGBColor(34, 34, 34)       # Texte principal
COLOR_MUTED = RGBColor(100, 100, 100)   # Métadonnées gris

def set_cell_background(cell, hex_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=45, bottom=45, left=65, right=65):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_header(title, level=1):
    h = doc.add_heading(level=level)
    run = h.add_run(title)
    if level == 1:
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.color.rgb = COLOR_PRIMARY
        h.paragraph_format.space_before = Pt(8)
        h.paragraph_format.space_after = Pt(2)
    elif level == 2:
        run.font.size = Pt(11)
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
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(20, 20, 20)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def add_callout(text, title="NOTE TECHNIQUE :"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "EBF3FA")
    set_cell_margins(cell, top=45, bottom=45, left=90, right=90)
    
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="16" w:space="0" w:color="0055A5"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    r_t = p.add_run(f"{title} ")
    r_t.font.bold = True
    r_t.font.size = Pt(8.5)
    r_t.font.color.rgb = COLOR_PRIMARY
    
    r_b = p.add_run(text)
    r_b.font.size = Pt(8.5)
    r_b.font.color.rgb = COLOR_DARK
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

# ==================== TITRE DU DOCUMENT ====================
title_p = doc.add_paragraph()
title_p.paragraph_format.space_before = Pt(0)
title_p.paragraph_format.space_after = Pt(1)
title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
t_run = title_p.add_run("RAPPORT TECHNIQUE DE VALIDATION DE SIMULATION")
t_run.font.size = Pt(16)
t_run.font.bold = True
t_run.font.color.rgb = COLOR_PRIMARY

sub_p = doc.add_paragraph()
sub_p.paragraph_format.space_after = Pt(3)
sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
sub_run = sub_p.add_run("Validation du Jalon AMR : Déploiement Gazebo 11, RViz 2 et Téléopération Clavier (/cmd_vel)\nRésolution des Incidents Graphiques WSLg & Architecture des Flux de Données")
sub_run.font.size = Pt(10)
sub_run.font.bold = True
sub_run.font.color.rgb = COLOR_SECONDARY

meta_p = doc.add_paragraph()
meta_p.paragraph_format.space_after = Pt(6)
meta_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
m_run = meta_p.add_run("Master Professionnel RAIA • ISET Bizerte | Réf. Mémoire : RAIA 01.26 | Encadrement : M. Hmida Hmaied")
m_run.font.size = Pt(8.5)
m_run.font.italic = True
m_run.font.color.rgb = COLOR_MUTED

# Separator line
p_line = doc.add_paragraph()
p_line.paragraph_format.space_after = Pt(6)
p_line_border = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="1" w:color="0055A5"/></w:pBdr>')
p_line._p.get_or_add_pPr().append(p_line_border)

# ==================== 1. INTRODUCTION ET VALIDATION ====================
add_header("1. Contexte et Validation du Jalon (Milestone)", level=1)
p1 = doc.add_paragraph()
p1.paragraph_format.space_after = Pt(3)
p1.add_run("Dans le cadre du projet de Master RAIA portant sur la modernisation du robot suiveur de ligne (AGV) issu du rapport ")
p1.add_run("RAIA 01.26").font.bold = True
p1.add_run(" en un ")
p1.add_run("AMR (Autonomous Mobile Robot)").font.bold = True
p1.add_run(", une étape charnière a été franchie avec succès : la mise en œuvre, la communication et le pilotage temps-réel du jumeau numérique dans l'environnement de simulation 3D ")
p1.add_run("Gazebo").font.bold = True
p1.add_run(" couplé au visualiseur ")
p1.add_run("RViz 2").font.bold = True
p1.add_run(". Le modèle 3D conçu en Xacro intègre fidèlement la mécanique de la Fig. 26 (châssis à rebords oblongs, double rack de transport de PCB, propulsion différentielle et capteur LiDAR 2D).")

# ==================== 2. ANALYSE ET RÉSOLUTION DE L'ÉCRAN NOIR ====================
add_header("2. Analyse et Résolution de l'Incident Technique : Écran Noir Gazebo", level=1)
p2 = doc.add_paragraph()
p2.paragraph_format.space_after = Pt(3)
p2.add_run("Lors de l'exécution initiale de la simulation sous Windows 11 / WSLg, Gazebo s'ouvrait mais présentait une fenêtre 3D totalement noire sans charger l'atelier. L'audit technique a isolé deux causes simultanées :")

p2_diag = doc.add_paragraph()
p2_diag.paragraph_format.space_after = Pt(2)
p2_diag.add_run("• Blocage Réseau des Modèles SDF Distants : ").font.bold = True
p2_diag.add_run("Au premier démarrage, Gazebo tente de télécharger les modèles du soleil (sun) et du sol (ground_plane) depuis le serveur models.gazebosim.org. Ce serveur étant fréquemment inaccessible ou sujet à de fortes latences, le thread de rendu restait figé indéfiniment.\n"
           "  -> ")
p2_diag.add_run("Résolution : ").font.bold = True
p2_diag.add_run("Création et mise en cache locale des fichiers model.config et model.sdf directement dans ~/.gazebo/models/sun/ et ~/.gazebo/models/ground_plane/.\n\n")

p2_diag.add_run("• Conflit de Rendu Direct3D 12 vGPU sur Puce Intel UHD : ").font.bold = True
p2_diag.add_run("Sous WSLg, le pilote Mesa D3D12 Gallium présente une instabilité de synchronisation des buffers d'échange OpenGL avec le moteur de rendu OGRE 1.x de Gazebo Classic.\n"
           "  -> ")
p2_diag.add_run("Résolution : ").font.bold = True
p2_diag.add_run("Configuration de la variable d'environnement GALLIUM_DRIVER=llvmpipe dans ~/.bashrc, basculant le rendu OpenGL vers le rastériseur CPU multi-cœurs LLVMpipe (parfaitement conforme OpenGL 4.5 sans freeze).")

add_callout("L'application de ces deux correctifs a débloqué instantanément l'affichage : l'atelier d'usine (factory_workshop.world) et l'AMR apparaissent désormais en temps réel sans latence d'initialisation.", "RÉSULTAT DU DÉPANNAGE :")

# ==================== 3. DÉCOMPOSITION DES COMMANDES ====================
add_header("3. Décomposition et Rôle des 3 Commandes Exécutées", level=1)
p3 = doc.add_paragraph()
p3.paragraph_format.space_after = Pt(3)
p3.add_run("La chaîne de test s'articule autour de trois processus ROS 2 exécutés en parallèle dans des terminaux distincts :")

# Tableau des commandes
tbl_cmd = doc.add_table(rows=4, cols=3)
tbl_cmd.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl_cmd.autofit = False

headers = ["Commande", "Processus Lancés", "Rôle et Impact dans la Simulation"]
col_widths = [Inches(2.5), Inches(1.8), Inches(2.9)]

for col_idx, text in enumerate(headers):
    cell = tbl_cmd.cell(0, col_idx)
    cell.width = col_widths[col_idx]
    set_cell_background(cell, "003366")
    set_cell_margins(cell, top=40, bottom=40, left=50, right=50)
    p = cell.paragraphs[0]
    r = p.add_run(text)
    r.font.bold = True
    r.font.size = Pt(8)
    r.font.color.rgb = RGBColor(255, 255, 255)

cmd_data = [
    (
        "ros2 launch raia_amr_description\nsim.launch.py",
        "• gzserver\n• gzclient\n• robot_state_publisher\n• spawn_entity",
        "1. Démarre le moteur physique ODE (gravité, collisions, contacts roues/sol).\n"
        "2. Parse le modèle Xacro en URDF et publie la cinématique /robot_description.\n"
        "3. Insère le robot AMR dans l'atelier factory_workshop à la pose (0,0,0.05).\n"
        "4. Active les plugins : moteur différentiel, faisceau LiDAR et caméra."
    ),
    (
        "ros2 launch raia_amr_description\nrviz.launch.py",
        "• rviz2\n• joint_state_publisher_gui",
        "1. Ouvre l'interface de supervision et de télémétrie 3D RViz 2.\n"
        "2. Affiche l'arbre des repères géométriques (/tf : base_footprint -> laser_frame).\n"
        "3. Visualise le nuage de points LiDAR rouge (/scan) en impact sur les murs.\n"
        "4. Affiche l'odométrie et la trajectoire spatiale calculée du robot."
    ),
    (
        "ros2 run teleop_twist_keyboard\nteleop_twist_keyboard",
        "• teleop_twist_keyboard",
        "1. Intercepte les frappes clavier (touches 'i', ',', 'j', 'l', 'k').\n"
        "2. Convertit les commandes en vecteurs de vitesse (linear.x, angular.z).\n"
        "3. Publie en continu sur le topic ROS 2 /cmd_vel pour piloter l'AMR."
    )
]

for row_idx, row_data in enumerate(cmd_data, start=1):
    bg_color = "F9FAFC" if row_idx % 2 == 1 else "FFFFFF"
    for col_idx, text in enumerate(row_data):
        cell = tbl_cmd.cell(row_idx, col_idx)
        cell.width = col_widths[col_idx]
        set_cell_background(cell, bg_color)
        set_cell_margins(cell, top=35, bottom=35, left=50, right=50)
        p = cell.paragraphs[0]
        r = p.add_run(text)
        if col_idx == 0:
            r.font.name = "Consolas"
            r.font.size = Pt(7.5)
            r.font.bold = True
        else:
            r.font.size = Pt(7.5)

doc.add_paragraph().paragraph_format.space_after = Pt(2)

# ==================== 4. ARCHITECTURE DES FLUX DE DONNÉES ====================
add_header("4. Architecture des Flux et Graphe Computationnel ROS 2", level=1)
p4 = doc.add_paragraph()
p4.paragraph_format.space_after = Pt(2)
p4.add_run("Lors de la manipulation du clavier, la circulation des données suit le schéma interactif suivant :")

p4_flow = doc.add_paragraph()
p4_flow.paragraph_format.space_after = Pt(2)
p4_flow.add_run("1. Téléopération : ").font.bold = True
p4_flow.add_run("L'utilisateur presse la touche 'i' -> teleop_twist_keyboard publie geometry_msgs/Twist (linear.x = 0.5 m/s) sur /cmd_vel.\n")
p4_flow.add_run("2. Cinématique Différentielle : ").font.bold = True
p4_flow.add_run("Le plugin libgazebo_ros_diff_drive reçoit /cmd_vel et calcule les vitesses angulaires des roues motrices gauche et droite selon l'écartement d = 0.35 m et le rayon r = 0.05 m :\n")

add_code_block("Vitesse roue gauche (w_G) = (Vx - (d/2) * Wz) / r  |  Vitesse roue droite (w_D) = (Vx + (d/2) * Wz) / r")

p4_flow2 = doc.add_paragraph()
p4_flow2.paragraph_format.space_after = Pt(2)
p4_flow2.add_run("3. Simulation Physique : ").font.bold = True
p4_flow2.add_run("Gazebo applique les couples moteurs, simule le frottement au sol (mu = 1.2), déplace le châssis et met à jour l'odométrie sur /odom ainsi que la transformation tf odom -> base_footprint.\n")
p4_flow2.add_run("4. Perception LiDAR : ").font.bold = True
p4_flow2.add_run("Le capteur laser virtuel balaie l'espace à 10 Hz sur 360°, détecte les tables de PCB et murs de l'atelier, et publie les distances sur /scan.\n")
p4_flow2.add_run("5. Rendu RViz 2 : ").font.bold = True
p4_flow2.add_run("RViz reçoit /scan et /tf et affiche en temps réel le robot mobile et l'impact laser rouge sur les obstacles environnants.")

# ==================== 5. PROCHAINES ÉTAPES ====================
add_header("5. Prochaines Étapes : Cartographie SLAM et Navigation Nav2", level=1)
p5 = doc.add_paragraph()
p5.paragraph_format.space_after = Pt(2)
p5.add_run("Le jalon de simulation dynamique étant validé, la plateforme est immédiatement prête pour les deux étapes clés de l'autonomie AMR :\n")
doc.add_paragraph("• Cartographie 2D (SLAM) : Lancement du package slam_toolbox en pilotant le robot pour enregistrer la carte globale de l'usine (carte de grille d'occupation au format .yaml et .pgm).", style='List Bullet')
doc.add_paragraph("• Navigation Autonome (Nav2) : Configuration du planificateur de trajectoire global (Navfn/Smac) et du contrôleur local (DWB) pour envoyer des destinations autonomes ('2D Nav Goal') dans RViz.", style='List Bullet')

doc.save("Rapport_Validation_Simulation_AMR.docx")
print("DOCX successfully generated!")
