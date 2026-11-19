#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  INSCRIPTION DES OBSTACLES FIXES & ZONES INTERDITES (KEEP-OUT ZONES) — AMR RAIA
  Atelier Industriel CMS 4.0 | factory_workshop.world
  
  Inscrit directement sur la carte PGM (raia_factory_map.pgm) :
  1. L'obstacle fixe du carrefour : Chariot de maintenance technique (x=0.0, y=0.65)
  2. Les barrières et structures fixes
  3. Les 'Champs à ne pas aller vers eux' (Zones interdites / Keep-Out Zones) :
     - Zone A : Zone Haute Tension & Armoire Électrique Est [x: 3.6..4.8, y: -1.2..0.4]
     - Zone B : Zone Tampon Arrière Sérigraphie MPM Nord-Est [x: 3.4..4.8, y: 1.2..3.2]
     - Zone C : Zone Stockage Chimique & Batteries Sud-Ouest [x: -4.8..-3.2, y: -3.0..-1.5]
     - Zone D : Zone Exclusion Banc de Test SPEA Nord-Ouest [x: -4.8..-3.4, y: 1.2..3.2]
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import shutil
import math
import numpy as np
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAPS_DIR = os.path.join(BASE_DIR, "maps")
BASELINE_MAP_PATH = os.path.join(MAPS_DIR, "raia_factory_map_baseline.pgm")
TARGET_MAP_PATH = os.path.join(MAPS_DIR, "raia_factory_map.pgm")
BACKUP_MAP_PATH = os.path.join(MAPS_DIR, "raia_factory_map.pgm.bak")

# Paramètres de la grille de coût / OGM
RESOLUTION = 0.05  # m par pixel
ORIGIN_X = -5.05   # m
ORIGIN_Y = -5.05   # m
WIDTH = 202        # pixels
HEIGHT = 202       # pixels

def world_to_map(x: float, y: float) -> tuple[int, int]:
    """Convertit des coordonnées monde (mètres) en pixels (row, col)."""
    col = int(round((x - ORIGIN_X) / RESOLUTION))
    row = HEIGHT - 1 - int(round((y - ORIGIN_Y) / RESOLUTION))
    col = max(0, min(WIDTH - 1, col))
    row = max(0, min(HEIGHT - 1, row))
    return row, col

def map_to_world(row: int, col: int) -> tuple[float, float]:
    """Convertit des coordonnées pixels (row, col) en coordonnées monde (mètres)."""
    x = ORIGIN_X + col * RESOLUTION
    y = ORIGIN_Y + (HEIGHT - 1 - row) * RESOLUTION
    return x, y

def draw_circle_obstacle(arr: np.ndarray, cx: float, cy: float, radius: float, val: int = 0):
    """Dessine un obstacle circulaire plein de valeur val (0 = occupé)."""
    cr, cc = world_to_map(cx, cy)
    rad_px = int(round(radius / RESOLUTION))
    for r in range(max(0, cr - rad_px), min(HEIGHT, cr + rad_px + 1)):
        for c in range(max(0, cc - rad_px), min(WIDTH, cc + rad_px + 1)):
            if math.hypot(r - cr, c - cc) <= rad_px:
                arr[r, c] = val

def draw_rect_keepout(arr: np.ndarray, x_min: float, x_max: float, y_min: float, y_max: float, val: int = 0):
    """Dessine une zone interdite (Keep-out zone) rectangulaire pleine."""
    r_top, c_left = world_to_map(x_min, y_max)
    r_bottom, c_right = world_to_map(x_max, y_min)
    
    r_start = min(r_top, r_bottom)
    r_end = max(r_top, r_bottom)
    c_start = min(c_left, c_right)
    c_end = max(c_left, c_right)
    
    arr[r_start:r_end + 1, c_start:c_end + 1] = val

def apply_all_features():
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║   INSCRIPTION DES OBSTACLES FIXES & ZONES INTERDITES SUR CARTE   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    
    # 1. Vérification et chargement de la carte baseline
    if os.path.exists(BASELINE_MAP_PATH):
        src_path = BASELINE_MAP_PATH
        print(f"  → Chargement de la carte baseline : {src_path}")
    elif os.path.exists(TARGET_MAP_PATH):
        src_path = TARGET_MAP_PATH
        print(f"  → Carte baseline absente, utilisation de : {src_path}")
    else:
        raise FileNotFoundError(f"Aucune carte PGM trouvée dans {MAPS_DIR}")
    
    # Sauvegarde préventive
    if os.path.exists(TARGET_MAP_PATH):
        shutil.copyfile(TARGET_MAP_PATH, BACKUP_MAP_PATH)
        print(f"  ✓ Sauvegarde de sécurité créée : {BACKUP_MAP_PATH}")

    im = Image.open(src_path)
    arr = np.array(im, dtype=np.uint8)

    # 2. Inscription de l'obstacle fixe central (Chariot de maintenance technique)
    # Position monde : x = 0.0, y = 0.65, dimensions réelles : 0.54 x 0.54 m (rayon ~0.32 m)
    cart_x, cart_y, cart_radius = 0.0, 0.65, 0.32
    draw_circle_obstacle(arr, cart_x, cart_y, cart_radius, val=0)
    print(f"  ✓ [OBSTACLE FIXE] Chariot de maintenance inscrit à ({cart_x:.2f}, {cart_y:.2f}) r={cart_radius:.2f}m")

    # 3. Inscription des 'Champs à ne pas aller vers eux' (Zones d'exclusion / Keep-Out Zones ISO 3691-4)
    keepout_zones = [
        {
            "id": "ZONE_A_HAUTE_TENSION",
            "name": "Zone A — Haute Tension & Armoire Électrique Est",
            "x_min": 3.6, "x_max": 4.8, "y_min": -1.2, "y_max": 0.4
        },
        {
            "id": "ZONE_B_TAMPON_MPM",
            "name": "Zone B — Périmètre Arrière Machine Sérigraphie MPM",
            "x_min": 3.4, "x_max": 4.8, "y_min": 1.2, "y_max": 3.2
        },
        {
            "id": "ZONE_C_STOCKAGE_CHIMIQUE",
            "name": "Zone C — Stockage Produits Chimiques & Batteries Sud-Ouest",
            "x_min": -4.8, "x_max": -3.2, "y_min": -3.0, "y_max": -1.5
        },
        {
            "id": "ZONE_D_EXCLUSION_SPEA",
            "name": "Zone D — Périmètre Arrière Banc d'Inspection SPEA",
            "x_min": -4.8, "x_max": -3.4, "y_min": 1.2, "y_max": 3.2
        }
    ]

    for z in keepout_zones:
        draw_rect_keepout(arr, z["x_min"], z["x_max"], z["y_min"], z["y_max"], val=0)
        print(f"  ✓ [KEEP-OUT ZONE] {z['name']} [{z['x_min']}..{z['x_max']}, {z['y_min']}..{z['y_max']}] inscrite")

    # 4. Sauvegarde de la carte finale PGM
    out_im = Image.fromarray(arr)
    out_im.save(TARGET_MAP_PATH)
    print(f"\n  ✓ Carte mise à jour enregistrée avec succès : {TARGET_MAP_PATH}")

    # Vérification des pixels
    unique, counts = np.unique(arr, return_counts=True)
    stats = dict(zip(unique, counts))
    print(f"  → Statistiques carte : {stats.get(0, 0)} px occupés (0), {stats.get(254, 0)} px libres (254), {stats.get(205, 0)} px inconnus (205)")
    print("═══════════════════════════════════════════════════════════════════\n")

if __name__ == "__main__":
    apply_all_features()
