from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

PRIMARY = RGBColor(0, 51, 102)
SECONDARY = RGBColor(0, 102, 178)
DARK = RGBColor(34, 34, 34)
WHITE = RGBColor(255, 255, 255)
LIGHT = RGBColor(244, 246, 250)
GREEN = RGBColor(0, 128, 96)

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)


def set_bg(slide, color):
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = color


def add_title(slide, title, subtitle=''):
    box = slide.shapes.add_textbox(Inches(0.7), Inches(0.4), Inches(12.0), Inches(0.8))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    if subtitle:
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.size = Pt(12)
        p2.font.bold = True
        p2.font.color.rgb = SECONDARY


def add_footer(slide):
    box = slide.shapes.add_textbox(Inches(0.7), Inches(7.0), Inches(12.0), Inches(0.3))
    tf = box.text_frame
    p = tf.paragraphs[0]
    p.text = 'Projet AMR • évolution par rapport à PRESENTATION 1'
    p.font.size = Pt(9)
    p.font.color.rgb = RGBColor(96, 96, 96)

# Slide 1
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide, LIGHT)
add_title(slide, 'AMÉLIORATION DU PROJET AMR', 'Suite de PRESENTATION 1 : AGV guidé → AMR autonome')
bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(1.5), Inches(11.8), Inches(0.12))
bar.fill.solid(); bar.fill.fore_color.rgb = PRIMARY; bar.line.color.rgb = PRIMARY
box = slide.shapes.add_textbox(Inches(0.9), Inches(1.9), Inches(5.7), Inches(3.0))
tf = box.text_frame
for i, text in enumerate([
    'Transformation du robot suiveur de ligne vers un AMR autonome',
    'Mise en place de ROS 2 Humble + Gazebo + RViz2',
    'Validation des flux de simulation et de téléopération',
    'Cartographie 2D avec SLAM et navigation autonome Nav2',
]):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = '• ' + text
    p.font.size = Pt(20)
    p.font.color.rgb = DARK
    p.space_after = Pt(8)
card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.5), Inches(1.9), Inches(4.5), Inches(3.0))
card.fill.solid(); card.fill.fore_color.rgb = RGBColor(230, 240, 250); card.line.color.rgb = SECONDARY
text_box = slide.shapes.add_textbox(Inches(7.8), Inches(2.3), Inches(3.9), Inches(2.2))
tf2 = text_box.text_frame
for i, text in enumerate(['WSL2', 'Ubuntu 22.04', 'ROS 2 Humble', 'SLAM + Nav2']):
    p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph()
    p.text = text
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = PRIMARY
    p.alignment = 1
add_footer(slide)

# Slide 2
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide, LIGHT)
add_title(slide, '1. ÉVOLUTION DU PROJET', 'D’un AGV rigide à un AMR autonome')
left = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.7), Inches(5.3), Inches(4.3))
left.fill.solid(); left.fill.fore_color.rgb = RGBColor(240, 247, 252); left.line.color.rgb = PRIMARY
lt = slide.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(4.7), Inches(3.4))
ltf = lt.text_frame
for i, text in enumerate(['AGV initial', 'Guidage par ligne optique', 'Capteurs IR et Arduino Uno', 'Trajectoire fixe et rigide', 'Peu de flexibilité']) :
    p = ltf.paragraphs[0] if i == 0 else ltf.add_paragraph(); p.text = '• ' + text; p.font.size = Pt(18) if i == 0 else Pt(17); p.font.color.rgb = PRIMARY if i==0 else DARK
right = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.7), Inches(5.6), Inches(4.3))
right.fill.solid(); right.fill.fore_color.rgb = RGBColor(232, 245, 239); right.line.color.rgb = GREEN
rt = slide.shapes.add_textbox(Inches(7.1), Inches(2.1), Inches(5.0), Inches(3.4))
rtf = rt.text_frame
for i, text in enumerate(['AMR amélioré', 'Cartographie LiDAR 2D', 'SLAM + localisation', 'Navigation autonome Nav2', 'Sans repères au sol']) :
    p = rtf.paragraphs[0] if i == 0 else rtf.add_paragraph(); p.text = '• ' + text; p.font.size = Pt(18) if i == 0 else Pt(17); p.font.color.rgb = GREEN if i==0 else DARK
add_footer(slide)

# Slide 3
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide, LIGHT)
add_title(slide, '2. SOLUTION TECHNIQUE', 'Pourquoi WSL2 + Ubuntu + ROS 2 ?')
for x, title, items in [
    (0.8, 'WSL2', ['Interopération Windows/Linux', 'Accès direct aux dossiers Windows', 'Rendu graphique plus stable']),
    (4.7, 'ROS2 Humble', ['Architecture de nœuds', 'Topics/services/actions', 'Compatible Nav2 et Gazebo']),
    (8.6, 'Simulation', ['Gazebo 3D', 'RViz2 visuel', 'Test rapide avant robot réel'])
]:
    c = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.8), Inches(3.5), Inches(4.0))
    c.fill.solid(); c.fill.fore_color.rgb = RGBColor(250,250,250); c.line.color.rgb = SECONDARY
    tb = slide.shapes.add_textbox(Inches(x+0.2), Inches(2.1), Inches(3.1), Inches(0.5))
    tf = tb.text_frame; p = tf.paragraphs[0]; p.text = title; p.font.size=Pt(18); p.font.bold=True; p.font.color.rgb=PRIMARY
    tb2 = slide.shapes.add_textbox(Inches(x+0.2), Inches(2.7), Inches(3.1), Inches(2.6))
    tf2 = tb2.text_frame
    for i, item in enumerate(items):
        p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph(); p.text = '• ' + item; p.font.size = Pt(14); p.font.color.rgb = DARK
add_footer(slide)

# Slide 4
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide, LIGHT)
add_title(slide, '3. VALIDATION DE LA SIMULATION', 'Déploiement Gazebo + RViz2 + téléopération')
box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(6.8), Inches(4.2))
box.fill.solid(); box.fill.fore_color.rgb = RGBColor(240, 247, 252); box.line.color.rgb = PRIMARY
text = slide.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(6.1), Inches(3.5))
tf = text.text_frame
for i, item in enumerate([
    'Résolution de l’écran noir Gazebo sous WSLg : cache locale des modèles + llvmpipe',
    'Lancement de la simulation du monde factory_workshop',
    'Affichage du robot dans RViz2 avec odométrie et TF',
    'Téléopération via /cmd_vel fonctionnelle',
    'Résultat : simulation stable et exploitable pour le Jalon 1']):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.text = '• ' + item; p.font.size = Pt(18); p.font.color.rgb = DARK
box2 = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.2), Inches(2.0), Inches(4.0), Inches(3.5))
box2.fill.solid(); box2.fill.fore_color.rgb = RGBColor(232, 245, 239); box2.line.color.rgb = GREEN
inside = slide.shapes.add_textbox(Inches(8.5), Inches(2.5), Inches(3.4), Inches(2.6))
inf = inside.text_frame
for i, item in enumerate(['Gazebo OK', 'RViz2 OK', 'Téléopération OK', 'Simulation validée']):
    p = inf.paragraphs[0] if i == 0 else inf.add_paragraph(); p.text = '✓ ' + item; p.font.size = Pt(16); p.font.color.rgb = GREEN
add_footer(slide)

# Slide 5
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide, LIGHT)
add_title(slide, '4. CARTOGRAPHIE SLAM', 'Production d’une carte 2D compatible Nav2')
left = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.8), Inches(4.2))
left.fill.solid(); left.fill.fore_color.rgb = RGBColor(240, 247, 252); left.line.color.rgb = PRIMARY
text = slide.shapes.add_textbox(Inches(1.1), Inches(2.1), Inches(5.1), Inches(3.2))
tf = text.text_frame
for i, item in enumerate([
    'Le robot explore le monde industriel via le LiDAR 2D',
    'slam_toolbox construit la carte de l’atelier',
    'Les données odométriques et de localisation sont fusionnées',
    'La carte finale est exportée en .yaml et .pgm',
    'Livrable : environnement de navigation prêt pour Nav2']):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.text = '• ' + item; p.font.size = Pt(17); p.font.color.rgb = DARK
right = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.0), Inches(1.9), Inches(5.2), Inches(3.8))
right.fill.solid(); right.fill.fore_color.rgb = RGBColor(232,245,239); right.line.color.rgb = GREEN
inside = slide.shapes.add_textbox(Inches(7.4), Inches(2.4), Inches(4.4), Inches(2.5))
inf = inside.text_frame
for i, item in enumerate(['slam.launch.py', 'slam_params.yaml', 'raia_factory_map.pgm', 'raia_factory_map.yaml']):
    p = inf.paragraphs[0] if i == 0 else inf.add_paragraph(); p.text = '✓ ' + item; p.font.size = Pt(16); p.font.color.rgb = GREEN
add_footer(slide)

# Slide 6
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide, LIGHT)
add_title(slide, '5. NAVIGATION AUTONOME NAV2', 'Planification globale et contrôle local')
left = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(3.7), Inches(4.1))
left.fill.solid(); left.fill.fore_color.rgb = RGBColor(240, 247, 252); left.line.color.rgb = PRIMARY
text = slide.shapes.add_textbox(Inches(1.1), Inches(2.2), Inches(3.1), Inches(3.2))
tf = text.text_frame
for i, item in enumerate(['AMCL / localisation', 'Costmaps globales + locales', 'Planificateur global: NavFn', 'Contrôleur local: DWB', 'Recovery behaviors']):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.text = '• ' + item; p.font.size = Pt(16); p.font.color.rgb = DARK
mid = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.8), Inches(1.8), Inches(3.4), Inches(4.1))
mid.fill.solid(); mid.fill.fore_color.rgb = RGBColor(255, 246, 232); mid.line.color.rgb = RGBColor(191,120,0)
text2 = slide.shapes.add_textbox(Inches(5.1), Inches(2.2), Inches(2.8), Inches(3.0))
tf2 = text2.text_frame
for i, item in enumerate(['Paramètres calibrés', 'xy_goal_tolerance', 'inflation_radius', 'max_vel_x', 'robot_radius']):
    p = tf2.paragraphs[0] if i == 0 else tf2.add_paragraph(); p.text = '• ' + item; p.font.size = Pt(15); p.font.color.rgb = DARK
right = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.6), Inches(2.0), Inches(3.8), Inches(3.7))
right.fill.solid(); right.fill.fore_color.rgb = RGBColor(232,245,239); right.line.color.rgb = GREEN
text3 = slide.shapes.add_textbox(Inches(8.9), Inches(2.5), Inches(3.2), Inches(2.7))
tf3 = text3.text_frame
for i, item in enumerate(['2D Nav Goal', 'Trajectoire calculée', 'Navigation autonome', 'Contournement d’obstacles']):
    p = tf3.paragraphs[0] if i == 0 else tf3.add_paragraph(); p.text = '✓ ' + item; p.font.size = Pt(15); p.font.color.rgb = GREEN
add_footer(slide)

# Final slide
slide = prs.slides.add_slide(prs.slide_layouts[6])
set_bg(slide, LIGHT)
add_title(slide, 'CONCLUSION', 'Le projet a évolué vers un AMR exploitable')
box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(1.8), Inches(11.2), Inches(3.6))
box.fill.solid(); box.fill.fore_color.rgb = RGBColor(240,247,252); box.line.color.rgb = PRIMARY
text = slide.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(10.5), Inches(2.6))
tf = text.text_frame
for i, item in enumerate([
    'Le projet initial a été transformé d’un AGV guidé vers un AMR autonome.',
    'La combinaison WSL2 + ROS 2 + Gazebo + SLAM + Nav2 apporte stabilité, reproductibilité et innovation.',
    'Les livrables de la phase actuelle sont directement alignés avec la logique de PRESENTATION 1 et son évolution technique.' ]):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.text = '• ' + item; p.font.size = Pt(18); p.font.color.rgb = DARK
add_footer(slide)

out = r'c:\Users\khalil\Desktop\STUDY\Bizerte\2eme\PROJET HMIDA\PRESENTATION_Amelioration_Projet_AMR.pptx'
prs.save(out)
print('Created:', out)
