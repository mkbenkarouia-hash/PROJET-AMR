#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  MODULE MULTIPLEXEUR DE COMMANDE SÉCURISÉ — RAIA AMR
  Atelier Industriel 4.0 | factory_workshop.world
  Gère la coexistence prioritaire entre téléopération manuelle et navigation Nav2
═══════════════════════════════════════════════════════════════════════════════
"""

import time
from enum import Enum
from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import Twist
from std_msgs.msg import String, Bool


class ControlMode(Enum):
    AUTO = "AUTONOMOUS_NAV2"
    MANUAL = "MANUAL_TELEOP"
    EMERGENCY_STOP = "EMERGENCY_STOP"


class CmdVelMux(Node):
    """
    Multiplexeur sécurisé pour le topic moteur /cmd_vel.
    Priorité absolue à la commande manuelle (sécurité opérateur) :
    Dès qu'une consigne /cmd_vel_teleop est détectée, la commande manuelle prend
    immédiatement le contrôle exclusif de la base mobile.
    Dès que la téléopération s'arrête (> timeout_sec), le contrôle repasse en Nav2.
    """

    def __init__(self):
        super().__init__(
            "raia_cmd_vel_mux",
            parameter_overrides=[
                Parameter("use_sim_time", Parameter.Type.BOOL, True)
            ]
        )

        # ── Paramètres
        self.teleop_timeout: float = 0.6  # secondes sans message teleop avant retour auto
        self.mode: ControlMode = ControlMode.AUTO

        # ── Horodatage
        self.last_teleop_time: float = 0.0

        # ── Souscriptions
        # 1. Navigation autonome Nav2 (publiée par velocity_smoother)
        self.sub_auto = self.create_subscription(
            Twist, "/cmd_vel_nav", self._auto_cmd_cb, 10
        )
        # 2. Téléopération manuelle (clavier / joystick / dashboard)
        self.sub_teleop = self.create_subscription(
            Twist, "/cmd_vel_teleop", self._teleop_cmd_cb, 10
        )
        # 3. Arrêt d'urgence
        self.sub_estop = self.create_subscription(
            Bool, "/emergency_stop", self._estop_cb, 10
        )

        # ── Publications
        # Topic final vers Gazebo diff_drive
        self.pub_cmd_vel = self.create_publisher(Twist, "/cmd_vel", 10)
        # Notification de statut de commande
        self.pub_mode = self.create_publisher(String, "/control_mode", 10)

        # ── Timer de vérification et heartbeat (20 Hz)
        self.timer = self.create_timer(0.05, self._timer_callback)

        self.last_auto_msg: Optional[Twist] = None
        self.last_teleop_msg: Optional[Twist] = None
        self.estop_active: bool = False

        self.get_logger().info("[CMD_VEL_MUX] Multiplexeur de commande démarré en mode AUTO.")

    def _auto_cmd_cb(self, msg: Twist):
        self.last_auto_msg = msg

    def _teleop_cmd_cb(self, msg: Twist):
        # Détection d'activité téléopération (vitesse linéaire ou angulaire non nulle)
        is_active = (abs(msg.linear.x) > 0.001) or (abs(msg.angular.z) > 0.001)
        if is_active:
            self.last_teleop_time = time.time()
            self.last_teleop_msg = msg
            if self.mode != ControlMode.MANUAL and not self.estop_active:
                self.mode = ControlMode.MANUAL
                self.get_logger().warn("[SÉCURITÉ] Téléopération manuelle engagée ! Priorité manuelle active.")

    def _estop_cb(self, msg: Bool):
        self.estop_active = msg.data
        if self.estop_active:
            self.mode = ControlMode.EMERGENCY_STOP
            self.get_logger().error("[ARRÊT D'URGENCE] Signal E-STOP activé ! Moteurs coupés.")
        else:
            self.mode = ControlMode.AUTO
            self.get_logger().info("[ARRÊT D'URGENCE] E-STOP désactivé. Retour au mode AUTO.")

    def _timer_callback(self):
        now = time.time()

        # 1. Gestion E-STOP
        if self.estop_active:
            self._publish_stop()
            self._publish_mode()
            return

        # 2. Gestion de l'expiration du timeout Téléopération
        if self.mode == ControlMode.MANUAL:
            if (now - self.last_teleop_time) > self.teleop_timeout:
                self.mode = ControlMode.AUTO
                self.get_logger().info("[CONTRÔLE] Téléopération inactive. Rétrocession du contrôle à Nav2.")
                self.last_teleop_msg = None

        # 3. Routage du flux de commande prioritaire vers /cmd_vel
        out_msg = Twist()
        if self.mode == ControlMode.MANUAL and self.last_teleop_msg:
            out_msg = self.last_teleop_msg
        elif self.mode == ControlMode.AUTO and self.last_auto_msg:
            out_msg = self.last_auto_msg

        self.pub_cmd_vel.publish(out_msg)
        self._publish_mode()

    def _publish_stop(self):
        stop_msg = Twist()
        self.pub_cmd_vel.publish(stop_msg)

    def _publish_mode(self):
        msg = String()
        msg.data = self.mode.value
        self.pub_mode.publish(msg)


def main():
    rclpy.init()
    node = CmdVelMux()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
