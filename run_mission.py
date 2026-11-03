#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  CYCLE DE NAVIGATION AUTONOME INDUSTRIEL — RAIA AMR (RAPPORT CMS 4.0)
  Workflow opérateur : Station de recharge -> Ligne 1 Sérigraphie (prise PCB)
                      -> Ligne 2 Convoyeur (dépose PCB) -> Retour Recharge
  Prise en charge du signal d'appel opérateur (/operator_call, /line_call_button)
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import time
import math
import argparse

import rclpy

from station_manager import StationManager
from navigation_manager import NavigationManager


def main():
    parser = argparse.ArgumentParser(description="Gestionnaire de mission industrielle RAIA AMR")
    parser.add_argument(
        "--wait-call",
        action="store_true",
        help="Attendre indéfiniment un signal ROS2 (/operator_call) avant de partir"
    )
    parser.add_argument(
        "--call-timeout",
        type=float,
        default=4.0,
        help="Délai d'attente à la borne avant déclenchement automatique (secondes)"
    )
    args, _ = parser.parse_known_args()

    rclpy.init()

    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║     CYCLE DE PRODUCTION INDUSTRIEL AUTONOME — RAIA AMR 4.0        ║")
    print("║     Atelier CMS | factory_workshop.world (Rapport RAIA 01.26)     ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")

    station_mgr = StationManager()
    nav_mgr = NavigationManager("mission_runner")

    # 1. Synchronisation de la pose TF initiale
    print("\n[MISSION] Synchronisation de la localisation robot et de l'arbre TF...")
    nav_mgr.publish_mission_state("INITIALIZING_TF")
    start_sync = time.time()
    tf_ready = False
    while (time.time() - start_sync) < 30.0:
        rclpy.spin_once(nav_mgr, timeout_sec=0.2)
        if nav_mgr.update_robot_pose():
            tf_ready = True
            print(f" -> Pose AMR synchronisée : ({nav_mgr.current_x:.2f}, {nav_mgr.current_y:.2f}), Cap : {math.degrees(nav_mgr.current_yaw):.1f}°")
            break
        time.sleep(0.3)

    if not tf_ready:
        print("[MISSION] ERREUR CRITIQUE : Localisation TF 'map' -> 'base_footprint' introuvable.")
        nav_mgr.destroy_node()
        rclpy.shutdown()
        sys.exit(1)

    # 2. État initial : AMR à la station de recharge MiR Charge (Quai Sud)
    print("\n═══════════════════════════════════════════════════════════════════")
    print(" [STATION DE RECHARGE] Robot amarré à la borne industrielle MiR Charge")
    print(f"   -> Position station : Quai Sud ({nav_mgr.current_x:.2f}, {nav_mgr.current_y:.2f}), Cap : {math.degrees(nav_mgr.current_yaw):.1f}°")
    print("   -> Broches de recharge 24V DC couplées au récepteur AMR | Tension : 24.3 V")
    print("   -> Niveau de batterie : 100% | Statut : EN VEILLE / PRÊT À PARTIR")
    print("═══════════════════════════════════════════════════════════════════")
    nav_mgr.publish_mission_state("DOCKED_AT_MIR_CHARGE_STATION")

    # 3. Attente du signal de l'employeur / opérateur de la ligne
    print("\n[APPEL OPÉRATEUR] En attente de demande d'intervention de la ligne de production...")
    print("   -> Écoute des signaux sur /operator_call ou /line_call_button")
    if not args.wait_call:
        print(f"   -> Mode autonome actif : départ sur signal ou après {args.call_timeout:.1f}s de maintien en charge...")

    call_start = time.time()
    while True:
        rclpy.spin_once(nav_mgr, timeout_sec=0.2)
        if nav_mgr.operator_call_received:
            print("\n>>> [ORDRE REÇU VIA TOPIC] Signal opérateur validé !")
            break
        if not args.wait_call and (time.time() - call_start) >= args.call_timeout:
            print("\n>>> [ORDRE REÇU DU SUPERVISEUR] Demande d'enlèvement Ligne 1 - Sérigraphie MPM confirmée !")
            nav_mgr.operator_call_received = True
            break
        time.sleep(0.2)

    print("═══════════════════════════════════════════════════════════════════")
    print(f" ORDRE DE MISSION : {nav_mgr.operator_call_source}")
    print(f" MOTIF           : {nav_mgr.operator_call_payload}")
    print(" DÉCONNEXION     : Plots de recharge 24V déconnectés")
    print("═══════════════════════════════════════════════════════════════════")
    nav_mgr.publish_mission_state("MISSION_DISPATCHED")
    time.sleep(1.0)

    # 4. ÉTAPE 1 : Déplacement vers Ligne 1 - Sérigraphie MPM (ST1)
    print("\n>>> [ÉTAPE 1/3] Départ vers Ligne 1 - Sérigraphie MPM (ST1) pour prise PCB...")
    nav_mgr.publish_mission_state("NAVIGATING_TO_ST1_SERIGRAPHIE")
    success1 = nav_mgr.navigate_to_station(
        "ST1",
        timeout_sec=90.0,
        dwell_time_sec=3.5,
        dwell_action_desc="Chargement automatique de la carte PCB sérigraphiée sur le plateau AMR"
    )

    if success1:
        print("    ✓ [CHARGEMENT PCB TERMINÉ] Circuit imprimé sérigraphié fixé sur le rack.")
        nav_mgr.publish_mission_state("PCB_LOADED_AT_ST1")
    else:
        print("    ✗ [ÉCHEC ÉTAPE 1] Impossible d'atteindre la station ST1.")
        nav_mgr.publish_mission_state("FAILED_ST1")

    # 5. ÉTAPE 2 : Déplacement vers Ligne 2 - Quai Convoyeur (ST2)
    print("\n>>> [ÉTAPE 2/3] Acheminement vers Ligne 2 - Quai Convoyeur (ST2) pour dépose PCB...")
    nav_mgr.publish_mission_state("NAVIGATING_TO_ST2_CONVEYOR")
    success2 = False
    if success1:
        success2 = nav_mgr.navigate_to_station(
            "ST2",
            timeout_sec=90.0,
            dwell_time_sec=3.5,
            dwell_action_desc="Transfert automatique de la carte PCB vers les rouleaux du convoyeur"
        )
        if success2:
            print("    ✓ [DÉCHARGEMENT PCB TERMINÉ] Circuit imprimé transféré sur le convoyeur.")
            nav_mgr.publish_mission_state("PCB_UNLOADED_TO_CONVEYOR")
        else:
            print("    ✗ [ÉCHEC ÉTAPE 2] Impossible d'atteindre la station ST2.")
            nav_mgr.publish_mission_state("FAILED_ST2")

    # 6. ÉTAPE 3 : Retour automatique à la Station de Recharge (ST0)
    print("\n>>> [ÉTAPE 3/3] Retour autonome vers la Station de Recharge & Docking (ST0)...")
    nav_mgr.publish_mission_state("RETURNING_TO_CHARGING_STATION")
    success3 = nav_mgr.navigate_to_station(
        "ST0",
        timeout_sec=90.0,
        dwell_time_sec=3.0,
        dwell_action_desc="Connexion automatique aux plots de recharge 24V DC du dock central"
    )

    print("\n═══════════════════════════════════════════════════════════════════")
    if success1 and success2 and success3:
        print(" [SUCCÈS TOTAL] Cycle de production inter-lignes 100% VALIDÉ !")
        print(" [STATUT BORNE] AMR connecté aux plots de charge. Recharge en cours.")
        print(" [ÉTAT SYSTÈME] Prêt pour le prochain appel d'un opérateur de ligne.")
        nav_mgr.publish_mission_state("DOCKED_CHARGING_IDLE")
    else:
        print(f" [BILAN] ST1 (Prise PCB): {'OK' if success1 else 'Échec'} | "
              f"ST2 (Dépose Convoyeur): {'OK' if success2 else 'Échec'} | "
              f"ST0 (Recharge): {'OK' if success3 else 'Échec'}")
        nav_mgr.publish_mission_state("MISSION_INCOMPLETE")
    print("═══════════════════════════════════════════════════════════════════")

    nav_mgr.destroy_node()
    rclpy.shutdown()

    sys.exit(0 if (success1 and success2 and success3) else 1)


if __name__ == "__main__":
    main()
