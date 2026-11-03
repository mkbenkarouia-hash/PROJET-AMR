from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

# --- Palette ---
PRIMARY = RGBColor(0, 51, 102)
SECONDARY = RGBColor(0, 102, 178)
ACCENT = RGBColor(31, 120, 180)
DARK = RGBColor(35, 35, 35)
LIGHT = RGBColor(245, 247, 250)
MUTED = RGBColor(96, 96, 96)
SUCCESS = RGBColor(0, 128, 96)
WARNING = RGBColor(191, 120, 0)
WHITE = RGBColor(255, 255, 255)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Common helpers

def set_background(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_title(slide, text, subtitle=None):
    title_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.35), Inches(11.5), Inches(0.7))
    tf = title_box.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(24)
    run.font.bold = True
    run.font.color.rgb = PRIMARY
    if subtitle:
        sub_box = slide.shapes.add_textbox(Inches(0.6), Inches(0.95), Inches(12.0), Inches(0.45))
        tf2 = sub_box.text_frame
        p2 = tf2.paragraphs[0]
        r2 = p2.add_run()
        r2.text = subtitle
        r2.font.size = Pt(11)
        r2.font.bold = True
        r2.font.color.rgb = SECONDARY


def add_footer(slide, text='PRESENTATION 1 — suite / amélioration du projet AMR'):
    box = slide.shapes.add_textbox(Inches(0.6), Inches(7.05), Inches(12.0), Inches(0.25))
    tf = box.text_frame
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = text
    run.font.size = Pt(8)
    run.font.color.rgb = MUTED


def add_bullets(slide, bullets, left, top, width, height, font_size=18, color=DARK):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = 0
    tf.margin_right = 0
    tf.margin_top = 0
    tf.margin_bottom = 0
    for i, item in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item
        p.level = 0
        p.bullet = True
        p.space_after = Pt(10)
        p.alignment = PP_ALIGN.LEFT
        for r in p.runs:
            r.font.size = Pt(font_size)
            r.font.color.rgb = color


def add_box(slide, left, top, width, height, color, title=None, title_color=WHITE):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.color.rgb = color
    if title:
        textbox = slide.shapes.add_textbox(left + Inches(0.15), top + Inches(0.12), width - Inches(0.3), Inches(0.4))
        tf = textbox.text_frame
        p = tf.paragraphs[0]
        run = p.add_run()
        run.text = title
        run.font.bold = True
        run.font.size = Pt(14)
        run.font.color.rgb = title_color
    return shape

# Slide 1
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_background(slide, LIGHT)
# header bar
bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(0.55))
bar.fill.solid(); bar.fill.fore_color.rgb = PRIMARY; bar.line.color.rgb = PRIMARY
# title text
box = slide.shapes.add_textbox(Inches(0.7), Inches(0.9), Inches(11.0), Inches(1.5))
tf = box.text_frame
p = tf.paragraphs[0]
r = p.add_run()
r.text = 'AMÉLIORATION DU PROJET AMR'
r.font.size = Pt(28)
r.font.bold = True
r.font.color.rgb = PRIMARY
p = tf.add_paragraph(); p.space_after = Pt(2)
r2 = p.add_run()
r2.text = 'Suite de PRESENTATION 1 : de l’AGV guidé vers un AMR autonome sous ROS 2 / Gazebo / Nav2'
r2.font.size = Pt(16)
r2.font.bold = True
r2.font.color.rgb = SECONDARY
# three key badges
for i, text in enumerate(['WSL2 + Ubuntu 22.04', 'ROS 2 Humble', 'SLAM + Nav2']):
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 3.9), Inches(2.5), Inches(3.2), Inches(0.8))
    badge.fill.solid(); badge.fill.fore_color.rgb = SECONDARY; badge.line.color.rgb = SECONDARY
    tb = slide.shapes.add_textbox(Inches(0.95 + i * 3.9), Inches(2.7), Inches(2.9), Inches(0.35))
    tfb = tb.text_frame; p = tfb.paragraphs[0]; r = p.add_run(); r.text = text; r.font.size = Pt(17); r.font.bold = True; r.font.color.rgb = WHITE
# right side summary box
box2 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), Inches(1.8), Inches(3.6), Inches(2.9))
box2.fill.solid(); box2.fill.fore_color.rgb = RGBColor(230, 240, 250); box2.line.color.rgb = SECONDARY
textbox = slide.shapes.add_textbox(Inches(9.0), Inches(2.0), Inches(3.2), Inches(2.4))
tf2 = textbox.text_frame
tf2.word_wrap = True
p = tf2.paragraphs[0]; r = p.add_run(); r.text = 'Objectif principal'; r.font.bold = True; r.font.size = Pt(16); r.font.color.rgb = PRIMARY
p = tf2.add_paragraph(); r = p.add_run(); r.text = 'Transformer un AGV de manutention en AMR capable de cartographier, localiser et naviguer de manière autonome dans un environnement industriel.'; r.font.size = Pt(12); r.font.color.rgb = DARK
# bottom strip
strip = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(6.7), prs.slide_width, Inches(0.8))
strip.fill.solid(); strip.fill.fore_color.rgb = PRIMARY; strip.line.color.rgb = PRIMARY
footer = slide.shapes.add_textbox(Inches(0.8), Inches(6.9), Inches(10.5), Inches(0.3))
tf3 = footer.text_frame; p = tf3.paragraphs[0]; r = p.add_run(); r.text = 'Projet RAIA • ISET Bizerte • Master Professionnel • 2026'; r.font.size = Pt(10); r.font.bold = True; r.font.color.rgb = WHITE
add_footer(slide, 'PRESENTATION 1 → suite du projet AMR')

# Slide 2 - Problème initial et évolution
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_background(slide, LIGHT)
add_title(slide, '1. Évolution du projet : AGV vers AMR', 'Suite logique de PRESENTATION 1')
add_box(slide, Inches(0.7), Inches(1.5), Inches(3.5), Inches(4.3), RGBColor(240, 247, 252), 'AGV initial', WHITE)
add_box(slide, Inches(4.7), Inches(1.5), Inches(3.5), Inches(4.3), RGBColor(230, 242, 237), 'AMR amélioré', WHITE)
add_box(slide, Inches(8.7), Inches(1.5), Inches(3.7), Inches(4.3), RGBColor(255, 246, 232), 'Valeur ajoutée', WHITE)
# AGV list
agv = slide.shapes.add_textbox(Inches(0.95), Inches(1.9), Inches(3.0), Inches(3.5)); tf = agv.text_frame; tf.word_wrap = True
for i, item in enumerate([
    'Guidage par ligne optique au sol',
    'Capteurs IR et Arduino Uno',
    'Trajectoire fixe et rigide',
    'Peu de flexibilité',
    'Dépendant de repères physiques',
]):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.text = '• ' + item; p.bullet = False; p.level = 0; p.space_after = Pt(8)
    for r in p.runs: r.font.size = Pt(15); r.font.color.rgb = DARK
# AMR list
amr = slide.shapes.add_textbox(Inches(4.95), Inches(1.9), Inches(3.0), Inches(3.5)); tf = amr.text_frame; tf.word_wrap = True
for i, item in enumerate([
    'Cartographie LiDAR 2D',
    'SLAM en temps réel',
    'Localisation and odométrie',
    'Navigation autonome Nav2',
    'Aucune ligne au sol requise',
]):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.text = '• ' + item; p.bullet = False; p.level = 0; p.space_after = Pt(8)
    for r in p.runs: r.font.size = Pt(15); r.font.color.rgb = DARK
# Value
val = slide.shapes.add_textbox(Inches(9.0), Inches(1.9), Inches(3.0), Inches(3.5)); tf = val.text_frame; tf.word_wrap = True
for i, item in enumerate([
    'Flexibilité d’exploitation industrielle',
    'Réduction de la dépendance aux repères',
    'Navigation dynamique et évitement',
    'Mieux adapté à l’usine de production',
    'Base pour un système robotique évolutif',
]):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.text = '• ' + item; p.bullet = False; p.level = 0; p.space_after = Pt(8)
    for r in p.runs: r.font.size = Pt(15); r.font.color.rgb = DARK
add_footer(slide)

# Slide 3 - Architecture and environment choice
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_background(slide, LIGHT)
add_title(slide, '2. Choix technologique : WSL2 / Ubuntu / ROS 2', 'Pourquoi ce choix pour le projet ?')
add_box(slide, Inches(0.7), Inches(1.5), Inches(4.0), Inches(4.9), RGBColor(235, 243, 250), 'WSL2 + Ubuntu 22.04', WHITE)
add_box(slide, Inches(4.9), Inches(1.5), Inches(3.8), Inches(4.9), RGBColor(230, 242, 237), 'ROS 2 Humble', WHITE)
add_box(slide, Inches(8.9), Inches(1.5), Inches(3.7), Inches(4.9), RGBColor(255, 246, 232), 'Gazebo / RViz2', WHITE)
# Lists
for x, items in [(0.95, ['Interopérabilité Windows + Linux', 'Accès direct aux fichiers /mnt/c', 'Meilleur rendu graphique que VirtualBox', 'Stabilité du développement ROS 2']),
                 (5.15, ['ROS 2 Humble pour l’architecture robotique', 'Topics / services / actions', 'Intégration avec Nav2', 'Traçabilité des nœuds et paramètres']),
                 (9.2, ['Simulation 3D du monde industriel', 'Visualisation LiDAR / tf / odométrie', 'Validation avant déploiement réel', 'Contrôle de scène et tests itératifs'])]:
    box = slide.shapes.add_textbox(Inches(x), Inches(2.0), Inches(2.9), Inches(3.6))
    tf = box.text_frame; tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.text = '• ' + item; p.space_after = Pt(8)
        for r in p.runs: r.font.size = Pt(14); r.font.color.rgb = DARK
add_footer(slide)

# Slide 4 - Validation Gazebo experience
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_background(slide, LIGHT)
add_title(slide, '3. Validation fonctionnelle de la simulation', 'Résultats clés du Jalon 1 / validation')
# left large box
add_box(slide, Inches(0.7), Inches(1.6), Inches(6.3), Inches(4.6), RGBColor(240, 247, 252), 'Problèmes identifiés et corrigés', WHITE)
text = slide.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.6), Inches(3.7)); tf = text.text_frame; tf.word_wrap = True
for item in [
    'Blocage de téléchargement des modèles Gazebo depuis models.gazebosim.org',
    'Écran noir dans Gazebo sous WSLg / rendu 3D instable',
    'Configuration de la cache locale des modèles (~/.gazebo/models)',
    'Utilisation de GALLIUM_DRIVER=llvmpipe pour stabiliser le rendu OpenGL',
    'Résultat : simulation du monde factory_workshop opérationnelle et exploitable',
]:
    p = tf.paragraphs[0] if item == text.text_frame.paragraphs[0].text else tf.add_paragraph()
    p.text = '• ' + item; p.space_after = Pt(9)
    for r in p.runs: r.font.size = Pt(15); r.font.color.rgb = DARK
# right box
add_box(slide, Inches(7.4), Inches(2.0), Inches(5.1), Inches(3.8), RGBColor(232, 245, 239), 'Validation', WHITE)
inside = slide.shapes.add_textbox(Inches(7.7), Inches(2.5), Inches(4.5), Inches(2.2)); tf = inside.text_frame
for i, item in enumerate(['Gazebo 11 démarré', 'RViz2 opérationnel', 'robot_state_publisher actif', 'Téléopération /cmd_vel fonctionnelle']):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.text = '✓ ' + item; p.space_after = Pt(10)
    for r in p.runs: r.font.size = Pt(16); r.font.color.rgb = SUCCESS
add_footer(slide)

# Slide 5 - SLAM
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_background(slide, LIGHT)
add_title(slide, '4. Cartographie SLAM : génération de la carte de l’atelier', 'Composant clé de l’amélioration du projet')
add_box(slide, Inches(0.7), Inches(1.5), Inches(5.7), Inches(4.6), RGBColor(235, 243, 250), 'Workflow SLAM', WHITE)
text = slide.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(5.0), Inches(3.7)); tf = text.text_frame
for item in [
    'Le robot explore le monde Gazebo en utilisant le LiDAR 2D (/scan)',
    'slam_toolbox construit une carte d’occupation 2D en temps réel',
    'Les données de localisation et d’odométrie sont fusionnées dans la carte',
    'La carte finale est exportée en .yaml et .pgm pour un usage Nav2',
    'Résultat : cartographie de l’usine compatible avec navigation autonome',
]:
    p = tf.paragraphs[0] if item == text.text_frame.paragraphs[0].text else tf.add_paragraph(); p.text = '• ' + item; p.space_after = Pt(9)
    for r in p.runs: r.font.size = Pt(15); r.font.color.rgb = DARK
add_box(slide, Inches(6.8), Inches(1.8), Inches(5.6), Inches(3.8), RGBColor(232, 245, 239), 'Livrables du SLAM', WHITE)
inside = slide.shapes.add_textbox(Inches(7.1), Inches(2.3), Inches(4.8), Inches(2.8)); tf = inside.text_frame
for item in ['slam.launch.py', 'slam_params.yaml', 'Carte OGM générée', 'Map → nav2.launch.py']:
    p = tf.paragraphs[0] if item == inside.text_frame.paragraphs[0].text else tf.add_paragraph(); p.text = '✓ ' + item; p.space_after = Pt(10)
    for r in p.runs: r.font.size = Pt(15); r.font.color.rgb = SUCCESS
add_footer(slide)

# Slide 6 - Nav2
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_background(slide, LIGHT)
add_title(slide, '5. Navigation autonome Nav2', 'Stack complète pour la planification et l’évitement d’obstacles')
add_box(slide, Inches(0.7), Inches(1.6), Inches(3.8), Inches(4.7), RGBColor(240, 247, 252), 'Architecture Nav2', WHITE)
text = slide.shapes.add_textbox(Inches(0.95), Inches(2.1), Inches(3.2), Inches(3.5)); tf = text.text_frame
for item in ['Localisation : AMCL / TF', 'Coût de carte : costmaps', 'Planification globale : NavFn', 'Contrôleur local : DWB', 'Recovery behaviors']: 
    p = tf.paragraphs[0] if item == text.text_frame.paragraphs[0].text else tf.add_paragraph(); p.text = '• ' + item; p.space_after = Pt(8)
    for r in p.runs: r.font.size = Pt(15); r.font.color.rgb = DARK
add_box(slide, Inches(4.9), Inches(1.6), Inches(3.3), Inches(4.7), RGBColor(230, 242, 237), 'Paramétrage', WHITE)
text2 = slide.shapes.add_textbox(Inches(5.2), Inches(2.1), Inches(2.8), Inches(3.2)); tf = text2.text_frame
for item in ['xy_goal_tolerance', 'inflation_radius', 'max_vel_x', 'robot_radius', 'resolution costmap']:
    p = tf.paragraphs[0] if item == text2.text_frame.paragraphs[0].text else tf.add_paragraph(); p.text = '• ' + item; p.space_after = Pt(8)
    for r in p.runs: r.font.size = Pt(15); r.font.color.rgb = DARK
add_box(slide, Inches(8.6), Inches(1.8), Inches(4.1), Inches(4.0), RGBColor(255, 246, 232), 'Résultat', WHITE)
text3 = slide.shapes.add_textbox(Inches(8.9), Inches(2.3), Inches(3.5), Inches(2.8)); tf = text3.text_frame
for item in ['Objectif 2D Nav Goal', 'Chemin calculé', 'Navigation autonome dans l’atelier', 'Réduction de la dépendance humaine']:
    p = tf.paragraphs[0] if item == text3.text_frame.paragraphs[0].text else tf.add_paragraph(); p.text = '✓ ' + item; p.space_after = Pt(9)
    for r in p.runs: r.font.size = Pt(16); r.font.color.rgb = SUCCESS
add_footer(slide)

# Slide 7 - project improvement summary
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_background(slide, LIGHT)
add_title(slide, '6. Bilan des améliorations du projet', 'Ce qui a changé par rapport à PRESENTATION 1')
# 4 summary metrics boxes
metrics = [
    ('Avant', 'AGV guidé par ligne', 'Repères physiques fixes'),
    ('Maintenant', 'AMR autonome', 'Cartographie + navigation'),
    ('Environnement', 'WSL2 + Ubuntu', 'Simulation stable et reproductible'),
    ('Livrables', 'slam.launch.py / nav2.launch.py', 'Paramètres et cartes validés'),
]
for idx, (title, v1, v2) in enumerate(metrics):
    x = Inches(0.7 + idx * 3.1)
    box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.7), Inches(2.7), Inches(4.0))
    box.fill.solid(); box.fill.fore_color.rgb = [RGBColor(235,243,250), RGBColor(230,242,237), RGBColor(255,246,232), RGBColor(243,245,250)][idx]; box.line.color.rgb = SECONDARY
    tb = slide.shapes.add_textbox(x + Inches(0.18), Inches(2.0), Inches(2.3), Inches(0.5)); tf = tb.text_frame; p = tf.paragraphs[0]; r = p.add_run(); r.text = title; r.font.bold = True; r.font.size = Pt(16); r.font.color.rgb = PRIMARY
    tb2 = slide.shapes.add_textbox(x + Inches(0.18), Inches(2.7), Inches(2.3), Inches(1.2)); tf2 = tb2.text_frame; p2 = tf2.paragraphs[0]; r2 = p2.add_run(); r2.text = v1; r2.font.size = Pt(13); r2.font.bold = True; r2.font.color.rgb = DARK
    tb3 = slide.shapes.add_textbox(x + Inches(0.18), Inches(3.8), Inches(2.3), Inches(0.8)); tf3 = tb3.text_frame; p3 = tf3.paragraphs[0]; r3 = p3.add_run(); r3.text = v2; r3.font.size = Pt(12); r3.font.color.rgb = MUTED
add_footer(slide)

# Slide 8 - conclusion
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_background(slide, LIGHT)
add_title(slide, '7. Conclusion et perspectives', 'Le projet est maintenant orienté vers un AMR fonctionnel')
add_box(slide, Inches(0.8), Inches(1.7), Inches(5.7), Inches(4.5), RGBColor(240,247,252), 'Conclusion', WHITE)
text = slide.shapes.add_textbox(Inches(1.1), Inches(2.2), Inches(5.0), Inches(3.2)); tf = text.text_frame
for item in [
    'Le projet a évolué d’un AGV guide par ligne vers un AMR autonome capable de perception et de navigation.',
    'La combinaison WSL2 + ROS 2 + Gazebo + Nav2 offre un cadre stable, reproductible et adapté à l’enseignement et au prototypage.',
    'La cartographie SLAM et la navigation autonome sont maintenant les piliers de la deuxième génération du robot.',
    'Les prochaines étapes : optimisation des paramètres, intégration de tâches d’industrialisation et validation sur robot réel.',
]:
    p = tf.paragraphs[0] if item == text.text_frame.paragraphs[0].text else tf.add_paragraph(); p.text = '• ' + item; p.space_after = Pt(10)
    for r in p.runs: r.font.size = Pt(17); r.font.color.rgb = DARK
add_box(slide, Inches(7.2), Inches(2.0), Inches(4.9), Inches(3.3), RGBColor(232,245,239), 'Perspectives', WHITE)
inside = slide.shapes.add_textbox(Inches(7.5), Inches(2.5), Inches(4.2), Inches(2.2)); tf = inside.text_frame
for item in ['Planification de missions multi-points', 'Optimisation de la trajectoire', 'Intégration du robot réel', 'Industrialisation du système']:
    p = tf.paragraphs[0] if item == inside.text_frame.paragraphs[0].text else tf.add_paragraph(); p.text = '✓ ' + item; p.space_after = Pt(9)
    for r in p.runs: r.font.size = Pt(16); r.font.color.rgb = SUCCESS
add_footer(slide)

output = r'c:\Users\khalil\Desktop\STUDY\Bizerte\2eme\PROJET HMIDA\PRESENTATION_Amelioration_Projet_AMR.pptx'
prs.save(output)
print(f'Created: {output}')
