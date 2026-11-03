#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  INTERFACE CLI DE SÉLECTION ET CONDUITE DE MISSIONS — RAIA AMR
  Atelier Industriel 4.0 | factory_workshop.world
  Sélection, validation des préconditions et orchestration de missions AMR
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import time
import math
from typing import List

import rclpy
from station_manager import StationManager, Station
from navigation_manager import NavigationManager, NavState


def clear_screen():
    print("\033[2J\033[H", end="")


def print_banner():
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║            GESTIONNAIRE DE MISSIONS DE NAVIGATION INDUSTRIELLE               ║")
    print("║                       AMR RAIA — USINE DU FUTUR 4.0                          ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")


def display_menu(station_mgr: StationManager, current_station: str):
    print("\n[STATION ACTUELLE] : " + f"\033[92m{current_station}\033[0m")
    print("┌──────────────────────────────────────────────────────────────────────────────┐")
    print("│ ACTIONS DE NAVIGATION DISPONIBLES :                                          │")
    print("├──────────────────────────────────────────────────────────────────────────────┤")
    for s in station_mgr.list_stations():
        print(f"│  [{s.id}] {s.name:<44} (x={s.x:4.1f}, y={s.y:4.1f}) │")
    print("├──────────────────────────────────────────────────────────────────────────────┤")
    print("│  [C] CYCLE COMPLET CMS : ST0 -> ST1 -> ST3 -> ST4 -> ST0                     │")
    print("│  [R] ROUTE PERSONNALISÉE : Saisie manuelle d'une liste de stations           │")
    print("│  [V] VÉRIFICATION DES PRÉCONDITIONS TECHNIQUES (TF / Nav2 / AMCL)            │")
    print("│  [Q] QUITTER L'APPLICATION                                                   │")
    print("└──────────────────────────────────────────────────────────────────────────────┘")


def main():
    rclpy.init()
    station_mgr = StationManager()
    nav_mgr = NavigationManager("mission_cli_controller")

    print("[INITIALISATION] Connexion à l'AMR et synchronisation de la localisation...")
    start_time = time.time()
    tf_ready = False
    while (time.time() - start_time) < 10.0:
        rclpy.spin_once(nav_mgr, timeout_sec=0.2)
        if nav_mgr.update_robot_pose():
            tf_ready = True
            break

    if tf_ready:
        print(f" -> Localisation opérationnelle à ({nav_mgr.current_x:.2f}, {nav_mgr.current_y:.2f})")
    else:
        print(" -> AVERTISSEMENT : TF en cours de négociation, les vérifications valideront le lien.")

    while True:
        nav_mgr.update_robot_pose()
        nearest, d = station_mgr.get_nearest_station(nav_mgr.current_x, nav_mgr.current_y)
        current_st_str = f"[{nearest.id}] {nearest.name} (distance {d:.2f} m)" if nearest else "Inconnue"

        print_banner()
        display_menu(station_mgr, current_st_str)

        choice = input("\nChoisissez une action ou entrez l'ID d'une station (ex: ST1, C, Q) : ").strip().upper()

        if choice == "Q":
            print("\nArrêt du gestionnaire de missions. Au revoir.")
            break

        elif choice == "V":
            print("\n[DIAGNOSTIC] Vérification des préconditions globales :")
            st0 = station_mgr.get_station("ST0")
            ok, msg = nav_mgr.verify_preconditions(st0, timeout_sec=6.0)
            print(f" -> Statut : {'VALIDÉ' if ok else 'ÉCHEC'}")
            print(f" -> Détail : {msg}")
            input("\nAppuyez sur Entrée pour continuer...")

        elif choice == "C":
            # Cycle complet de fabrication
            route = ["ST0", "ST1", "ST3", "ST4", "ST0"]
            print(f"\n[CYCLE INDUSTRIEL] Lancement de la séquence de production : {' -> '.join(route)}")
            confirm = input("Confirmer le départ immédiat ? (O/n) : ").strip().lower()
            if confirm in ["", "o", "oui", "y"]:
                res = nav_mgr.execute_multi_station_route(route, dwell_time_per_station=3.0)
                print(f"\n[RÉSULTAT DU CYCLE] : {'SUCCÈS TOTAL' if res['success'] else 'ÉCHEC À ' + str(res['failed'])}")
            input("\nAppuyez sur Entrée pour continuer...")

        elif choice == "R":
            raw_input = input("\nEntrez la suite d'identifiants séparés par des virgules ou espaces (ex: ST1, ST2, ST5) : ")
            tokens = [t.strip().upper() for t in raw_input.replace(",", " ").split() if t.strip()]
            invalid = [t for t in tokens if not station_mgr.get_station(t)]
            if invalid:
                print(f"\n[ERREUR] Stations non reconnues : {', '.join(invalid)}")
            elif not tokens:
                print("\n[ERREUR] Aucune station spécifiée.")
            else:
                print(f"\n[ROUTE PERSONNALISÉE] Trajet validé : {' -> '.join(tokens)}")
                res = nav_mgr.execute_multi_station_route(tokens, dwell_time_per_station=2.5)
                print(f"\n[RÉSULTAT] : {'SUCCÈS' if res['success'] else 'ÉCHEC'}")
            input("\nAppuyez sur Entrée pour continuer...")

        else:
            station = station_mgr.get_station(choice)
            if station:
                print(f"\n>>> Mission unitaire vers [{station.id}] {station.name} à ({station.x:.2f}, {station.y:.2f})")
                ok = nav_mgr.navigate_to_station(station.id, dwell_time_sec=2.0)
                print(f"\nRésultat mission : {'SUCCÈS' if ok else 'ÉCHEC'}")
                input("\nAppuyez sur Entrée pour continuer...")
            else:
                print(f"\n[ERREUR] Option inconnue : '{choice}'")
                time.sleep(1.5)

    nav_mgr.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
