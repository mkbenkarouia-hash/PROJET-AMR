#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  TABLEAU DE BORD DE SUPERVISION EN TEMPS RÉEL — RAIA AMR
  Atelier Industriel 4.0 | factory_workshop.world
  Surveillance télémétrique temps réel de la navigation et de la sécurité AMR
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import math
from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import Twist, PoseWithCovarianceStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import String, Bool
import tf2_ros

from station_manager import StationManager, Station


def yaw_from_quaternion(x, y, z, w):
    t3 = 2.0 * (w * z + x * y)
    t4 = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(t3, t4)


class SupervisionDashboard(Node):
    """
    Console de supervision télémétrique temps réel de l'AMR RAIA.
    Affiche l'état de localisation, la vitesse, la station la plus proche,
    la cible en cours, le mode de commande et la sécurité.
    """

    def __init__(self):
        super().__init__(
            "raia_supervision_dashboard",
            parameter_overrides=[
                Parameter("use_sim_time", Parameter.Type.BOOL, True)
            ]
        )

        self.station_mgr = StationManager()

        # ── Données télémétriques
        self.x: float = 0.0
        self.y: float = 0.0
        self.yaw: float = 0.0
        self.lin_vel: float = 0.0
        self.ang_vel: float = 0.0
        self.amcl_cov: float = 0.0
        self.control_mode: str = "AUTONOMOUS_NAV2"
        self.mission_status: str = "EN ATTENTE"
        self.target_name: str = "Aucune"
        self.distance_to_target: float = 0.0
        self.nearest_station: Optional[Station] = None
        self.nearest_dist: float = 0.0
        self.estop_active: bool = False
        self.tf_connected: bool = False

        # ── TF2
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # ── Souscriptions
        self.sub_odom = self.create_subscription(Odometry, "/odom", self._odom_cb, 10)
        self.sub_amcl = self.create_subscription(PoseWithCovarianceStamped, "/amcl_pose", self._amcl_cb, 10)
        self.sub_mode = self.create_subscription(String, "/control_mode", self._mode_cb, 10)
        self.sub_estop = self.create_subscription(Bool, "/emergency_stop", self._estop_cb, 10)

        # ── Rafraîchissement console à 5 Hz
        self.timer = self.create_timer(0.20, self._render_display)

    def _odom_cb(self, msg: Odometry):
        self.lin_vel = msg.twist.twist.linear.x
        self.ang_vel = msg.twist.twist.angular.z

    def _amcl_cb(self, msg: PoseWithCovarianceStamped):
        cov = msg.pose.covariance
        # Trace de covariance de position (xx + yy)
        self.amcl_cov = cov[0] + cov[7]

    def _mode_cb(self, msg: String):
        self.control_mode = msg.data

    def _estop_cb(self, msg: Bool):
        self.estop_active = msg.data

    def update_pose_from_tf(self):
        try:
            trans = self.tf_buffer.lookup_transform("map", "base_footprint", rclpy.time.Time())
            self.x = trans.transform.translation.x
            self.y = trans.transform.translation.y
            q = trans.transform.rotation
            self.yaw = yaw_from_quaternion(q.x, q.y, q.z, q.w)
            self.tf_connected = True
            self.nearest_station, self.nearest_dist = self.station_mgr.get_nearest_station(self.x, self.y)
        except Exception:
            self.tf_connected = False

    def _render_display(self):
        self.update_pose_from_tf()

        # Effacer l'écran (ANSI)
        sys.stdout.write("\033[2J\033[H")

        status_color = "\033[92m" if self.tf_connected else "\033[91m"
        mode_color = "\033[93m" if "MANUAL" in self.control_mode else "\033[92m"
        if self.estop_active:
            mode_color = "\033[91m\033[1m"

        print("╔══════════════════════════════════════════════════════════════════════════════════╗")
        print("║          TABLEAU DE BORD DE SUPERVISION INDUSTRIELLE — AMR RAIA 4.0             ║")
        print("╠══════════════════════════════════════════════════════════════════════════════════╣")
        print(f"║  ÉTAT LOCALISATION TF : {status_color}{'OPÉRATIONNEL (Connecté)' if self.tf_connected else 'SYNCHRONISATION EN COURS'}\033[0m                      ║")
        print(f"║  MODE DE COMMANDE     : {mode_color}{self.control_mode:<30}\033[0m                        ║")
        print(f"║  ARRÊT D'URGENCE      : {'\033[91mACTIF (MOTEURS COUPÉS)\033[0m' if self.estop_active else '\033[92mSÉCURISÉ (Normal)\033[0m':<40}       ║")
        print("╠══════════════════════════════════════════════════════════════════════════════════╣")
        print("║  1. POSITION & CINÉMATIQUE DU ROBOT                                              ║")
        print(f"║     • Coordonnées X, Y : X = {self.x:6.2f} m  |  Y = {self.y:6.2f} m                          ║")
        print(f"║     • Orientation Cap  : θ = {math.degrees(self.yaw):6.1f}° ({self.yaw:5.2f} rad)                              ║")
        print(f"║     • Vitesse Linéaire : v = {self.lin_vel:5.2f} m/s  (max: 0.50 m/s)                            ║")
        print(f"║     • Vitesse Angulaire: ω = {self.ang_vel:5.2f} rad/s (max: 1.00 rad/s)                         ║")
        print(f"║     • Précision AMCL   : σ² = {self.amcl_cov:6.4f} m²                                     ║")
        print("╠══════════════════════════════════════════════════════════════════════════════════╣")
        print("║  2. CONTEXTE INDUSTRIEL & STATIONS DE PRODUCTION                                 ║")
        if self.nearest_station:
            nst = f"[{self.nearest_station.id}] {self.nearest_station.name} ({self.nearest_dist:.2f} m)"
            print(f"║     • Station la plus proche : {nst:<49} ║")
        else:
            print("║     • Station la plus proche : Aucune                                            ║")
        print(f"║     • Station cible mission  : {self.target_name:<49} ║")
        print("╠══════════════════════════════════════════════════════════════════════════════════╣")
        print("║  3. STATIONS DE PRODUCTION CONFIGURÉES DANS L'ATELIER (stations.yaml)            ║")
        for st in self.station_mgr.list_stations():
            is_here = " (ICI)" if self.nearest_station and self.nearest_station.id == st.id and self.nearest_dist < 0.35 else ""
            line_st = f"[{st.id}] {st.name} ({st.x:.1f}, {st.y:.1f}){is_here}"
            print(f"║     • {line_st:<73} ║")
        print("╚══════════════════════════════════════════════════════════════════════════════════╝")
        print(" Appuyez sur Ctrl+C pour quitter la supervision.")
        sys.stdout.flush()


def main():
    rclpy.init()
    dash = SupervisionDashboard()
    try:
        rclpy.spin(dash)
    except KeyboardInterrupt:
        pass
    finally:
        dash.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
