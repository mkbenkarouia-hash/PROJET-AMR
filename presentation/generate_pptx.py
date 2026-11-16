#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  GÉNÉRATEUR DE PRÉSENTATION PROFESSIONNELLE (PPTX) — PROJET AMR RAIA 4.0
  ISET Bizerte — Mastère Professionnel / 2ème Année — Projet HMIDA
  Format 16:9 HD avec diapositives illustrées et notes orateur complètes
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_dir = os.path.join(base_dir, "images")

    # ── Palette de couleurs Industrielle Haute Fidélité
    COLOR_NAVY_DARK = RGBColor(15, 23, 42)      # #0F172A - Fond titre et bandeaux
    COLOR_PRIMARY_BLUE = RGBColor(30, 58, 138)  # #1E3A8A - Bleu industriel
    COLOR_AMBER = RGBColor(217, 119, 6)         # #D97706 - Accent orange/ambre
    COLOR_GOLD = RGBColor(245, 158, 11)         # #F59E0B - Gold
    COLOR_BG_LIGHT = RGBColor(248, 250, 252)    # #F8FAFC - Fond diapositive clair
    COLOR_CARD_BG = RGBColor(255, 255, 255)     # #FFFFFF - Fond carte
    COLOR_TEXT_MAIN = RGBColor(30, 41, 59)      # #1E293B - Titre carte
    COLOR_TEXT_MUTED = RGBColor(71, 85, 105)    # #475569 - Texte secondaire
    COLOR_BORDER = RGBColor(226, 232, 240)      # #E2E8F0 - Bordure carte
    COLOR_ACCENT_BG = RGBColor(238, 242, 255)   # #EEF2FF - Fond bleu doux

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category_text="PROJET AMR RAIA 4.0 — ATELIER CMS"):
        # Header banner
        header_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.15)
        )
        header_shape.fill.solid()
        header_shape.fill.fore_color.rgb = COLOR_NAVY_DARK
        header_shape.line.fill.background()

        # Accent line under header
        line_shape = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.15), Inches(13.333), Inches(0.06)
        )
        line_shape.fill.solid()
        line_shape.fill.fore_color.rgb = COLOR_AMBER
        line_shape.line.fill.background()

        # Header text frame
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(11.5), Inches(0.95))
        tf = tx_box.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0)
        tf.margin_bottom = Inches(0)
        tf.margin_left = Inches(0)

        p_cat = tf.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.name = "Arial"
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_GOLD

        p_title = tf.add_paragraph()
        p_title.text = title_text
        p_title.font.name = "Arial"
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = RGBColor(255, 255, 255)

    def add_footer(slide, current_idx, total_idx=10):
        tx_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.1), Inches(11.733), Inches(0.35))
        tf = tx_box.text_frame
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = f"ISET Bizerte — Mastère Professionnel / Projet HMIDA  |  Avancement AMR RAIA  |  {current_idx} / {total_idx}"
        p.font.name = "Arial"
        p.font.size = Pt(9)
        p.font.color.rgb = COLOR_TEXT_MUTED

    # ═════════════════════════════════════════════════════════════════════════
    #  SLIDE 1 : COUVERTURE & TITRE
    # ═════════════════════════════════════════════════════════════════════════
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = COLOR_NAVY_DARK
    bg1.line.fill.background()

    # Left color strip
    strip = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(0.4), Inches(7.5))
    strip.fill.solid()
    strip.fill.fore_color.rgb = COLOR_AMBER
    strip.line.fill.background()

    # Title box
    tbox = slide1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(7.5), Inches(4.5))
    tf1 = tbox.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "ISET BIZERTE — MASTÈRE PROFESSIONNEL EN INGÉNIERIE"
    p0.font.name = "Arial"
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = COLOR_GOLD

    p1 = tf1.add_paragraph()
    p1.text = "Projet AMR RAIA 4.0\nRobot Mobile Autonome Industriel"
    p1.font.name = "Arial"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(255, 255, 255)
    p1.space_before = Pt(12)

    p2 = tf1.add_paragraph()
    p2.text = "Rapport d'Avancement Technique : Navigation Autonome Inter-Lignes, Sécurité Active & Amarrage Précis"
    p2.font.name = "Arial"
    p2.font.size = Pt(15)
    p2.font.color.rgb = RGBColor(203, 213, 225)
    p2.space_before = Pt(12)

    # Info card box
    ibox = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(5.0), Inches(6.8), Inches(1.8))
    ibox.fill.solid()
    ibox.fill.fore_color.rgb = RGBColor(30, 41, 59)
    ibox.line.color.rgb = COLOR_AMBER
    ibox.line.width = Pt(1.5)
    itf = ibox.text_frame
    itf.margin_left = Inches(0.3)
    itf.margin_top = Inches(0.2)
    ip1 = itf.paragraphs[0]
    ip1.text = "👤  Réalisé par : Khalil Ben Karouia (2ème Année Mastère)"
    ip1.font.name = "Arial"
    ip1.font.size = Pt(12)
    ip1.font.bold = True
    ip1.font.color.rgb = RGBColor(255, 255, 255)

    ip2 = itf.add_paragraph()
    ip2.text = "🎯  Encadrant : M. Hmida  |  Projet Industriel RAIA 01.26"
    ip2.font.name = "Arial"
    ip2.font.size = Pt(12)
    ip2.font.color.rgb = COLOR_GOLD
    ip2.space_before = Pt(4)

    ip3 = itf.add_paragraph()
    ip3.text = "📅  Date : Novembre 2026  |  Environnement : ROS 2 Humble & Gazebo 11"
    ip3.font.name = "Arial"
    ip3.font.size = Pt(11)
    ip3.font.color.rgb = RGBColor(148, 163, 184)
    ip3.space_before = Pt(4)

    # Image on right
    img1_path = os.path.join(img_dir, "amr_3d_view.png")
    if os.path.exists(img1_path):
        slide1.shapes.add_picture(img1_path, Inches(8.3), Inches(1.3), Inches(4.5), Inches(5.4))

    # Notes orateur
    slide1.notes_slide.notes_text_frame.text = (
        "Bonjour à tous et bienvenue à cette soutenance d'avancement technique sur le projet AMR RAIA 4.0.\n\n"
        "Je m'appelle Khalil Ben Karouia, étudiant en 2ème année mastère à l'ISET de Bizerte sous la direction de M. Hmida.\n\n"
        "L'objectif de cette présentation est de vous exposer l'ensemble des travaux réalisés : depuis l'architecture logicielle "
        "sous ROS 2 Humble et le simulateur Gazebo 11, jusqu'à la validation complète en vidéo du cycle logistique inter-lignes "
        "dans un atelier CMS industriel (évitement d'obstacles, sécurité piéton sonore et amarrage de recharge automatique)."
    )

    # ═════════════════════════════════════════════════════════════════════════
    #  SLIDE 2 : CONTEXTE & OBJECTIFS DU PROJET
    # ═════════════════════════════════════════════════════════════════════════
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Contexte Industriel & Cahier des Charges (Rapport RAIA 01.26)")
    add_footer(slide2, 2)

    # Left content: 3 cards
    cards_data = [
        ("🏭 Transition Usine 4.0", "Automatisation du transit inter-lignes de cartes électroniques (PCB) au sein d'un atelier CMS moderne, en remplacement des transferts manuels lents et accidentogènes."),
        ("🔄 Cycle Logistique Autonome", "Prise en charge automatique : Départ de la borne MiR Charge (ST0) -> Récupération du PCB à la sérigraphie MPM (ST1) -> Dépose sur convoyeur (ST2) -> Retour amarrage ST0."),
        ("🛡️ Norme de Sécurité ISO 3691-4", "Cohabitation totale avec les opérateurs d'usine : arrêt d'urgence immédiat sur obstacle mobile, avertisseur sonore, et contournement dynamique des obstacles fixes.")
    ]

    top_y = 1.45
    for title, desc in cards_data:
        box = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top_y), Inches(6.8), Inches(1.6))
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_CARD_BG
        box.line.color.rgb = COLOR_BORDER
        box.line.width = Pt(1.2)
        btf = box.text_frame
        btf.margin_left = Inches(0.25)
        btf.margin_top = Inches(0.18)
        bp1 = btf.paragraphs[0]
        bp1.text = title
        bp1.font.name = "Arial"
        bp1.font.size = Pt(14)
        bp1.font.bold = True
        bp1.font.color.rgb = COLOR_PRIMARY_BLUE
        bp2 = btf.add_paragraph()
        bp2.text = desc
        bp2.font.name = "Arial"
        bp2.font.size = Pt(11)
        bp2.font.color.rgb = COLOR_TEXT_MUTED
        bp2.space_before = Pt(6)
        top_y += 1.8

    # Right image
    img2_path = os.path.join(img_dir, "slide0_factory_workshop_overview.png")
    if os.path.exists(img2_path):
        slide2.shapes.add_picture(img2_path, Inches(8.0), Inches(1.45), Inches(4.8), Inches(5.2))

    slide2.notes_slide.notes_text_frame.text = (
        "Sur cette diapositive, nous posons le contexte industriel du projet.\n\n"
        "Dans l'industrie électronique actuelle, les lignes de fabrication de composants montés en surface (CMS) "
        "produisent des cartes PCB à très haute cadence. Le goulot d'étranglement réside souvent dans la logistique interne.\n\n"
        "Le cahier des charges RAIA 01.26 impose donc de concevoir un robot mobile capable de desservir de façon autonome "
        "deux machines de production clés (la sérigraphie et le convoyeur d'inspection) tout en respectant scrupuleusement "
        "la norme ISO 3691-4 régissant la sécurité des véhicules autoguidés en présence d'humains."
    )

    # ═════════════════════════════════════════════════════════════════════════
    #  SLIDE 3 : ARCHITECTURE LOGICIELLE & STACK ROS 2
    # ═════════════════════════════════════════════════════════════════════════
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Architecture Système & Pile Logicielle ROS 2 Humble")
    add_footer(slide3, 3)

    stack_cards = [
        ("ROS 2 Humble & Fast-DDS", "Middleware temps réel sous Ubuntu 22.04 LTS (WSL2 / Windows 11). Communication nodale robuste et découplée."),
        ("Simulateur Gazebo 11 (ODE)", "Moteur physique haute fidélité réglé à 250 Hz pour un comportement dynamique et odométrique sans dérive."),
        ("Navigation Nav2 & RPPC", "Contrôleur industriel Regulated Pure Pursuit (RPPC) : suivi de trajectoire fluide, gestion des virages et vitesse modulée."),
        ("Localisation AMCL & Costmaps", "Filtre particulaire Monte-Carlo adaptatif couplé aux cartes de coût locale et globale pour l'évitement d'obstacles.")
    ]

    top_y = 1.45
    for title, desc in stack_cards:
        box = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top_y), Inches(6.8), Inches(1.22))
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_CARD_BG
        box.line.color.rgb = COLOR_BORDER
        box.line.width = Pt(1.2)
        btf = box.text_frame
        btf.margin_left = Inches(0.25)
        btf.margin_top = Inches(0.12)
        bp1 = btf.paragraphs[0]
        bp1.text = title
        bp1.font.name = "Arial"
        bp1.font.size = Pt(13)
        bp1.font.bold = True
        bp1.font.color.rgb = COLOR_PRIMARY_BLUE
        bp2 = btf.add_paragraph()
        bp2.text = desc
        bp2.font.name = "Arial"
        bp2.font.size = Pt(10)
        bp2.font.color.rgb = COLOR_TEXT_MUTED
        bp2.space_before = Pt(4)
        top_y += 1.4

    img3_path = os.path.join(img_dir, "amr_3d_view.png")
    if os.path.exists(img3_path):
        slide3.shapes.add_picture(img3_path, Inches(8.0), Inches(1.45), Inches(4.8), Inches(5.2))

    slide3.notes_slide.notes_text_frame.text = (
        "Passons maintenant à l'architecture technologique que nous avons mise en place.\n\n"
        "Nous avons choisi ROS 2 Humble Hawksbill, qui constitue le standard industriel le plus stable et pérenne.\n"
        "La simulation repose sur Gazebo 11 avec le solveur ODE configuré à 250 Hz, ce qui assure une excellente répétabilité odométrique.\n\n"
        "Au niveau navigation, Nav2 utilise l'algorithme Regulated Pure Pursuit (RPPC). Contrairement aux régulateurs classiques "
        "qui peuvent provoquer des saccades ou des oscillations, le RPPC régule la vitesse linéaire en fonction de la courbure "
        "et de la proximité des obstacles, garantissant un déplacement souple et sécurisé."
    )

    # ═════════════════════════════════════════════════════════════════════════
    #  SLIDE 4 : MODÉLISATION DE L'ATELIER CMS 4.0
    # ═════════════════════════════════════════════════════════════════════════
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Modélisation de l'Atelier CMS & Cartographie (factory_workshop.world)")
    add_footer(slide4, 4)

    workshop_cards = [
        ("📐 Atelier 10m x 10m (100 m²)", "Modélisation exacte des murs périmétriques de 2.6m de haut, piliers porteurs et couloirs de circulation normalisés."),
        ("🔌 ST0 : Borne MiR Charge (Sud)", "Positionnée à (0.0, -3.80). Station de recharge industrielle 24V DC pour l'attente et le maintien de charge."),
        ("🖨️ ST1 : Sérigraphie MPM (Est)", "Positionnée à (1.80, 0.65). Ligne 1 de dépose de pâte à braser où l'AMR prend en charge le PCB terminé."),
        ("📦 ST2 : Convoyeur Inspection (Ouest)", "Positionnée à (-1.80, 0.65). Ligne 2 équipée de rouleaux de convoyage pour l'inspection optique automatisée.")
    ]

    top_y = 1.45
    for title, desc in workshop_cards:
        box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top_y), Inches(6.8), Inches(1.22))
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_CARD_BG
        box.line.color.rgb = COLOR_BORDER
        box.line.width = Pt(1.2)
        btf = box.text_frame
        btf.margin_left = Inches(0.25)
        btf.margin_top = Inches(0.12)
        bp1 = btf.paragraphs[0]
        bp1.text = title
        bp1.font.name = "Arial"
        bp1.font.size = Pt(13)
        bp1.font.bold = True
        bp1.font.color.rgb = COLOR_PRIMARY_BLUE
        bp2 = btf.add_paragraph()
        bp2.text = desc
        bp2.font.name = "Arial"
        bp2.font.size = Pt(10)
        bp2.font.color.rgb = COLOR_TEXT_MUTED
        bp2.space_before = Pt(4)
        top_y += 1.4

    img4_path = os.path.join(img_dir, "slide0_factory_workshop_overview.png")
    if os.path.exists(img4_path):
        slide4.shapes.add_picture(img4_path, Inches(8.0), Inches(1.45), Inches(4.8), Inches(5.2))

    slide4.notes_slide.notes_text_frame.text = (
        "Ici, vous observez la vue de dessus complète de notre monde de simulation factory_workshop.world.\n\n"
        "L'atelier fait 10 mètres par 10 mètres. Nous y avons disposé :\n"
        "1. Au Sud : La borne de recharge industrielle MiR Charge (ST0) avec ses marquages jaunes au sol.\n"
        "2. À l'Est : La machine de sérigraphie MPM Momentum (ST1) où les cartes reçoivent la pâte à braser.\n"
        "3. À l'Ouest : Le quai convoyeur d'inspection (ST2) pour le contrôle qualité.\n"
        "4. Au centre : Les lignes directrices au sol et l'allée transversale piétonne.\n\n"
        "Toutes ces géométries ont été cartographiées sous forme de grille d'occupation 2D (occupancy grid map) "
        "pour permettre à la pile Nav2 de localiser le robot et planifier les trajectoires."
    )

    # ═════════════════════════════════════════════════════════════════════════
    #  SLIDE 5 : SÉCURITÉ ACTIVE PIÉTON & AVERTISSEUR SONORE
    # ═════════════════════════════════════════════════════════════════════════
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Sécurité Active ISO 3691-4 : Détection Piéton & Alerte Sonore")
    add_footer(slide5, 5)

    safety_cards = [
        ("🚶 Détection d'Obstacle Mobile", "L'opérateur piéton (human_worker_pedestrian) traverse l'allée centrale à y = -1.60m. Le LiDAR 2D Hokuyo le détecte à d = 1.01m."),
        ("🛑 Arrêt d'Urgence Instantané", "Dès franchissement du gabarit de sécurité (Protection Field), la commande moteur est coupée immédiatement (cmd_vel = 0) en moins de 100 ms."),
        ("🔊 Diffusion de l'Avertisseur Sonore", "Déclenchement automatique de la mélodie industrielle d'avertissement (amr_safety_melody.wav) via le haut-parleur robot pour alerter l'humain."),
        ("▶️ Reprise Autonome sans Reset", "Dès que l'opérateur a achevé sa traversée et dégagé le gabarit, l'alarme s'arrête et l'AMR reprend sa trajectoire vers ST1 sans intervention humaine.")
    ]

    top_y = 1.45
    for title, desc in safety_cards:
        box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top_y), Inches(6.8), Inches(1.22))
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_CARD_BG
        box.line.color.rgb = COLOR_BORDER
        box.line.width = Pt(1.2)
        btf = box.text_frame
        btf.margin_left = Inches(0.25)
        btf.margin_top = Inches(0.12)
        bp1 = btf.paragraphs[0]
        bp1.text = title
        bp1.font.name = "Arial"
        bp1.font.size = Pt(13)
        bp1.font.bold = True
        bp1.font.color.rgb = COLOR_PRIMARY_BLUE
        bp2 = btf.add_paragraph()
        bp2.text = desc
        bp2.font.name = "Arial"
        bp2.font.size = Pt(10)
        bp2.font.color.rgb = COLOR_TEXT_MUTED
        bp2.space_before = Pt(4)
        top_y += 1.4

    img5_path = os.path.join(img_dir, "slide2_worker_detection_stop.png")
    if os.path.exists(img5_path):
        slide5.shapes.add_picture(img5_path, Inches(8.0), Inches(1.45), Inches(4.8), Inches(5.2))

    slide5.notes_slide.notes_text_frame.text = (
        "Cette diapositive illustre l'un des points forts de notre système : la sécurité active certifiée ISO 3691-4.\n\n"
        "Sur l'image de droite, on voit l'opérateur en gilet haute visibilité et casque jaune traverser l'allée centrale.\n"
        "Notre nœud de supervision scanne le champ frontal avec le LiDAR 2D Hokuyo.\n\n"
        "Dès que l'employé pénètre dans le polygone de sécurité (distance inférieure à 1.05m), deux actions simultanées ont lieu :\n"
        "1. Arrêt matériel d'urgence : la consigne de vitesse est immédiatement forcée à 0.\n"
        "2. Activation de la sirène/mélodie sonore amr_safety_melody.wav pour prévenir l'opérateur.\n\n"
        "Dès que l'opérateur termine sa traversée, le système détecte le dégagement, coupe la mélodie et ré-engage la navigation de manière autonome."
    )

    # ═════════════════════════════════════════════════════════════════════════
    #  SLIDE 6 : ÉVITEMENT DYNAMIQUE CHARIOT FIXE
    # ═════════════════════════════════════════════════════════════════════════
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Évitement Dynamique d'Obstacle Fixe : Contournement du Chariot")
    add_footer(slide6, 6)

    cart_cards = [
        ("🛒 Obstacle Imprévu au Carrefour", "Un chariot technique de maintenance (chariot_maintenance_fixe) est abandonné au centre du carrefour (x=0.0, y=0.65), bloquant l'axe direct ST1 -> ST2."),
        ("🌐 Détection Dynamique Costmap", "Le LiDAR intègre le chariot en direct dans la costmap locale et globale de Nav2 sous forme de zone de coût de collision interdit."),
        ("↪️ Calcul de Courbe de Déviation", "Le planificateur Navfn et le contrôleur RPPC recalculent instantanément une trajectoire d'évitement en boucle par le couloir Nord (y ≈ 1.25m)."),
        ("🛡️ Marge de Sécurité > 0.60m", "L'AMR maintient un dégagement latéral de plus de 60 cm par rapport au chariot, évitant tout contact avant d'arriver au poste ST2.")
    ]

    top_y = 1.45
    for title, desc in cart_cards:
        box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top_y), Inches(6.8), Inches(1.22))
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_CARD_BG
        box.line.color.rgb = COLOR_BORDER
        box.line.width = Pt(1.2)
        btf = box.text_frame
        btf.margin_left = Inches(0.25)
        btf.margin_top = Inches(0.12)
        bp1 = btf.paragraphs[0]
        bp1.text = title
        bp1.font.name = "Arial"
        bp1.font.size = Pt(13)
        bp1.font.bold = True
        bp1.font.color.rgb = COLOR_PRIMARY_BLUE
        bp2 = btf.add_paragraph()
        bp2.text = desc
        bp2.font.name = "Arial"
        bp2.font.size = Pt(10)
        bp2.font.color.rgb = COLOR_TEXT_MUTED
        bp2.space_before = Pt(4)
        top_y += 1.4

    img6_path = os.path.join(img_dir, "slide4_cart_avoidance_curve.png")
    if os.path.exists(img6_path):
        slide6.shapes.add_picture(img6_path, Inches(8.0), Inches(1.45), Inches(4.8), Inches(5.2))

    slide6.notes_slide.notes_text_frame.text = (
        "Voici la démonstration de la capacité d'évitement autonome d'un obstacle fixe non répertorié sur la carte d'origine.\n\n"
        "Un chariot de maintenance bleu ciel a été placé au carrefour central (x=0.0, y=0.65), en plein sur la ligne droite reliant ST1 à ST2.\n\n"
        "Un chariot AGV traditionnel à bande magnétique se serait arrêté indéfiniment en attendant l'intervention d'un technicien.\n"
        "Notre AMR RAIA 4.0, au contraire, utilise la mise à jour dynamique de ses costmaps : il identifie l'obstacle, calcule une "
        "courbe de déviation par le Nord (y=1.25m) et contourne le chariot avec plus de 60 cm de marge de sécurité, "
        "assurant ainsi la continuité ininterrompue de la chaîne de production."
    )

    # ═════════════════════════════════════════════════════════════════════════
    #  SLIDE 7 : CYCLE LOGISTIQUE INTER-LIGNES
    # ═════════════════════════════════════════════════════════════════════════
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Cycle de Production Inter-Lignes : Transfert de Cartes PCB")
    add_footer(slide7, 7)

    cycle_cards = [
        ("📥 Étape 1 : Prise PCB à ST1 (Sérigraphie)", "Arrivée de haute précision face à la sérigraphie MPM à (1.80, 0.65) avec un écart de 21 cm. Chargement automatique de la carte (temporisation 3.5s)."),
        ("📤 Étape 2 : Dépose PCB à ST2 (Convoyeur)", "Navigation vers le convoyeur d'inspection à (-1.80, 0.65) avec un écart de 15 cm. Transfert automatique sur les rouleaux d'entraînement."),
        ("📡 Supervision & Traçabilité MES", "Chaque transition d'état (chargement, transit, déchargement) est notifiée sur le topic /mission_state pour intégration directe au système MES de l'usine."),
        ("🎯 Répétabilité & Efficacité", "Cycle de mission complet réalisé en 1 min 02s avec 100% de succès opérationnel et zéro incident matériel.")
    ]

    top_y = 1.45
    for title, desc in cycle_cards:
        box = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top_y), Inches(6.8), Inches(1.22))
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_CARD_BG
        box.line.color.rgb = COLOR_BORDER
        box.line.width = Pt(1.2)
        btf = box.text_frame
        btf.margin_left = Inches(0.25)
        btf.margin_top = Inches(0.12)
        bp1 = btf.paragraphs[0]
        bp1.text = title
        bp1.font.name = "Arial"
        bp1.font.size = Pt(13)
        bp1.font.bold = True
        bp1.font.color.rgb = COLOR_PRIMARY_BLUE
        bp2 = btf.add_paragraph()
        bp2.text = desc
        bp2.font.name = "Arial"
        bp2.font.size = Pt(10)
        bp2.font.color.rgb = COLOR_TEXT_MUTED
        bp2.space_before = Pt(4)
        top_y += 1.4

    img7_path = os.path.join(img_dir, "slide3_st1_pcb_pickup.png")
    if os.path.exists(img7_path):
        slide7.shapes.add_picture(img7_path, Inches(8.0), Inches(1.45), Inches(4.8), Inches(5.2))

    slide7.notes_slide.notes_text_frame.text = (
        "Sur cette diapositive, nous détaillons le cycle logistique métier entre les deux lignes de production.\n\n"
        "À la station ST1 (sérigraphie MPM Momentum), le robot s'amarre avec une précision remarquable de 21 cm. "
        "Une temporisation de 3.5 secondes simule le transfert mécanique de la carte PCB sérigraphiée sur le plateau de l'AMR.\n\n"
        "Ensuite, après évitement de l'obstacle central, l'AMR rejoint la station ST2 (convoyeur d'inspection) avec un écart de seulement 15 cm. "
        "Le PCB est transféré sur les rouleaux pour l'inspection optique automatisée.\n\n"
        "Tous ces événements sont publiés sur le topic ROS 2 /mission_state, permettant aux systèmes de supervision MES et ERP "
        "de suivre la traçabilité de chaque lot de fabrication en temps réel."
    )

    # ═════════════════════════════════════════════════════════════════════════
    #  SLIDE 8 : BORNE DE RECHARGE MIR CHARGE 24V
    # ═════════════════════════════════════════════════════════════════════════
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Station de Recharge Industrielle MiR Charge 24V & Docking Final")
    add_footer(slide8, 8)

    dock_cards = [
        ("🔌 Modèle Industriel MiR Charge", "Inspiré de la borne réelle Mobile Industrial Robots (MiR Charge 24V/48V) avec plots de contact rétractables en façade."),
        ("🎯 Amarrage Terminal de Précision", "Retour au quai Sud à (0.0, -3.80) avec un écart de positionnement inférieur à 15 cm et un écart de cap sous 17°."),
        ("⚡ Connexion Électrique Automatique", "Couplage mécanique direct entre les récepteurs de l'AMR et les broches 24V DC pour la recharge rapide des batteries LiFePO4."),
        ("🛡️ Autonomie Totale en Atelier", "Cycle sans aucune intervention humaine de câblage : maintien en charge permanente en attendant le prochain appel de ligne.")
    ]

    top_y = 1.45
    for title, desc in dock_cards:
        box = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top_y), Inches(6.8), Inches(1.22))
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_CARD_BG
        box.line.color.rgb = COLOR_BORDER
        box.line.width = Pt(1.2)
        btf = box.text_frame
        btf.margin_left = Inches(0.25)
        btf.margin_top = Inches(0.12)
        bp1 = btf.paragraphs[0]
        bp1.text = title
        bp1.font.name = "Arial"
        bp1.font.size = Pt(13)
        bp1.font.bold = True
        bp1.font.color.rgb = COLOR_PRIMARY_BLUE
        bp2 = btf.add_paragraph()
        bp2.text = desc
        bp2.font.name = "Arial"
        bp2.font.size = Pt(10)
        bp2.font.color.rgb = COLOR_TEXT_MUTED
        bp2.space_before = Pt(4)
        top_y += 1.4

    # Top right: Hardware photo | Bottom right: Simulation docking screenshot
    img8_hw = os.path.join(img_dir, "mir_charge_hardware.png")
    img8_sim = os.path.join(img_dir, "slide6_final_docking_mir.png")
    if os.path.exists(img8_hw):
        slide8.shapes.add_picture(img8_hw, Inches(8.0), Inches(1.45), Inches(4.8), Inches(2.4))
    if os.path.exists(img8_sim):
        slide8.shapes.add_picture(img8_sim, Inches(8.0), Inches(4.1), Inches(4.8), Inches(2.6))

    slide8.notes_slide.notes_text_frame.text = (
        "L'un des défis majeurs dans la robotique mobile autonome industrielle est la gestion de l'énergie.\n\n"
        "Comme vous le voyez en haut à droite, nous nous sommes basés sur les spécifications de la borne industrielle MiR Charge.\n"
        "En bas à droite, notre simulation montre l'amarrage de précision : l'AMR effectue une manœuvre finale d'alignement de cap (90°) "
        "pour venir enficher ses plots récepteurs sur les broches 24V de la station, avec une tolérance inférieure à 15 cm.\n\n"
        "Dès l'accostage réussi, le robot bascule en mode recharge et reste en veille active jusqu'à la réception d'un nouvel ordre de mission."
    )

    # ═════════════════════════════════════════════════════════════════════════
    #  SLIDE 9 : OPTIMISATIONS TECHNIQUES & PERFORMANCE (30 FPS)
    # ═════════════════════════════════════════════════════════════════════════
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Optimisations Techniques & Performance de Simulation (30 FPS)")
    add_footer(slide9, 9)

    perf_cards = [
        ("🖥️ Résolution Écran Noir WSLg", "Mise en place d'un serveur d'affichage virtuel Xvfb dédié avec framebuffer 24-bit RGB (1366x768), éliminant l'absence de root window sous WSLg."),
        ("🚀 Allégement Rendu Graphique", "Désactivation de l'affichage des 360 rayons LiDAR dans Gazebo (visualize=false) et des ombres lourdes : division par 3 de la charge CPU/GPU."),
        ("🎞️ Normalisation 30 FPS Constants", "Encodage vidéo H.264 ultra-fluide à 30 FPS constants avec accélération de cadence : visionnage dynamique en 1 min 02s au lieu de 2 min saccadées."),
        ("⚖️ Intégrité Physique ODE 250 Hz", "Maintien de la boucle de calcul physique à 250 Hz (pas de 4 ms) pour garantir la fidélité de l'odométrie et éliminer toute dérive des roues.")
    ]

    top_y = 1.45
    for title, desc in perf_cards:
        box = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(top_y), Inches(6.8), Inches(1.22))
        box.fill.solid()
        box.fill.fore_color.rgb = COLOR_CARD_BG
        box.line.color.rgb = COLOR_BORDER
        box.line.width = Pt(1.2)
        btf = box.text_frame
        btf.margin_left = Inches(0.25)
        btf.margin_top = Inches(0.12)
        bp1 = btf.paragraphs[0]
        bp1.text = title
        bp1.font.name = "Arial"
        bp1.font.size = Pt(13)
        bp1.font.bold = True
        bp1.font.color.rgb = COLOR_PRIMARY_BLUE
        bp2 = btf.add_paragraph()
        bp2.text = desc
        bp2.font.name = "Arial"
        bp2.font.size = Pt(10)
        bp2.font.color.rgb = COLOR_TEXT_MUTED
        bp2.space_before = Pt(4)
        top_y += 1.4

    img9_path = os.path.join(img_dir, "slide1_mir_charge_dock.png")
    if os.path.exists(img9_path):
        slide9.shapes.add_picture(img9_path, Inches(8.0), Inches(1.45), Inches(4.8), Inches(5.2))

    slide9.notes_slide.notes_text_frame.text = (
        "Sur le plan technique et informatique, nous avons surmonté plusieurs défis d'optimisation notables.\n\n"
        "Premièrement, l'environnement WSL2 de Windows 11 utilise un serveur Wayland WSLg sans racine X11, ce qui provoquait initialement "
        "un écran noir lors des captures vidéo. Nous avons conçu une architecture avec serveur virtuel Xvfb 24 bits et gestionnaire Openbox.\n\n"
        "Deuxièmement, le LiDAR affichait 360 rayons volumétriques bleus qui saturaient le GPU à 3 FPS. En basculant la visualisation à false "
        "(tout en gardant le topic ROS /scan 100% opérationnel pour Nav2), et en désactivant les ombres dynamiques, nous avons considérablement fluidifié le système.\n\n"
        "Enfin, nous avons normalisé la vidéo finale à 30 FPS constants (taille réduite à 552 Ko), permettant une lecture directe et instantanée sur GitHub."
    )

    # ═════════════════════════════════════════════════════════════════════════
    #  SLIDE 10 : SYNTHÈSE DU BILAN & PERSPECTIVES
    # ═════════════════════════════════════════════════════════════════════════
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "Synthèse de l'Avancement & Prochains Jalons")
    add_footer(slide10, 10)

    # Left: Bilan des acquis
    b_box = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.45), Inches(5.6), Inches(5.2))
    b_box.fill.solid()
    b_box.fill.fore_color.rgb = COLOR_CARD_BG
    b_box.line.color.rgb = COLOR_BORDER
    b_box.line.width = Pt(1.5)
    b_tf = b_box.text_frame
    b_tf.margin_left = Inches(0.3)
    b_tf.margin_top = Inches(0.25)
    bp1 = b_tf.paragraphs[0]
    bp1.text = "✅  Bilan des Résultats Validés (100%)"
    bp1.font.name = "Arial"
    bp1.font.size = Pt(16)
    bp1.font.bold = True
    bp1.font.color.rgb = RGBColor(22, 101, 52) # Dark green

    achievements = [
        "Modélisation complète de l'atelier CMS (10m x 10m) sous Gazebo 11 ODE.",
        "Navigation autonome Nav2 inter-lignes (ST0 -> ST1 -> ST2 -> ST0).",
        "Sécurité piéton ISO 3691-4 : arrêt d'urgence + avertisseur sonore d'alerte.",
        "Évitement dynamique d'obstacle fixe avec contournement par courbe Nord.",
        "Amarrage de haute précision aux plots de recharge 24V de la borne MiR Charge.",
        "Dépôt GitHub à jour avec code source, documentation et vidéo HD 30 FPS."
    ]
    for ach in achievements:
        p = b_tf.add_paragraph()
        p.text = f"•  {ach}"
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_before = Pt(8)

    # Right: Prochains Jalons
    r_box = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.45), Inches(5.7), Inches(5.2))
    r_box.fill.solid()
    r_box.fill.fore_color.rgb = COLOR_ACCENT_BG
    r_box.line.color.rgb = COLOR_PRIMARY_BLUE
    r_box.line.width = Pt(1.5)
    r_tf = r_box.text_frame
    r_tf.margin_left = Inches(0.3)
    r_tf.margin_top = Inches(0.25)
    rp1 = r_tf.paragraphs[0]
    rp1.text = "🎯  Perspectives & Prochains Jalons"
    rp1.font.name = "Arial"
    rp1.font.size = Pt(16)
    rp1.font.bold = True
    rp1.font.color.rgb = COLOR_PRIMARY_BLUE

    perspectives = [
        "Intégration Hardware : Déploiement du stack sur plateforme matérielle réelle (châssis différentiel, LiDAR Hokuyo/RPLiDAR, STM32/ESP32 et Nvidia Jetson).",
        "Gestion Flotte & MES : Interfaçage avec le logiciel de supervision d'usine (Open-RMF, protocoles MQTT / OPC-UA / REST).",
        "Optimisation Docking LiDAR : Remplacement du docking odométrique par un asservissement visuel sur mires AprilTag / réflecteurs laser.",
        "Validation Industrielle : Essais en conditions réelles sur la ligne d'assemblage de l'ISET Bizerte."
    ]
    for per in perspectives:
        p = r_tf.add_paragraph()
        p.text = f"➔  {per}"
        p.font.name = "Arial"
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_TEXT_MAIN
        p.space_before = Pt(10)

    slide10.notes_slide.notes_text_frame.text = (
        "Pour conclure cette soutenance d'avancement, nous pouvons affirmer que 100% des objectifs fixés "
        "pour cette étape de simulation ont été atteints avec succès.\n\n"
        "L'AMR RAIA 4.0 démontre une autonomie complète, une sécurité active conforme à l'ISO 3691-4 avec signal sonore, "
        "un évitement dynamique d'obstacles et une précision d'amarrage conforme aux contraintes industrielles.\n\n"
        "La prochaine étape consistera à transposer cette pile logicielle sur le prototype physique réel, "
        "en y associant un asservissement fin par marqueurs visuels AprilTag et la communication avec le superviseur MES.\n\n"
        "Je vous remercie vivement pour votre attention et je suis désormais à votre disposition pour répondre à toutes vos questions."
    )

    out_file = os.path.join(base_dir, "Avancement_Projet_AMR_RAIA.pptx")
    prs.save(out_file)
    print(f"[OK] Presentation PowerPoint generee avec succes : {out_file}")
    return out_file

if __name__ == "__main__":
    build_presentation()
