#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  SIMULATEUR DE TRAFIC PIÉTON / EMPLOYÉ D'USINE — RAIA AMR
  Atelier Industriel 4.0 | factory_workshop.world
  Anime un opérateur humain traversant l'allée centrale de transit (y = -1.60)
  pendant la navigation de l'AMR pour valider l'arrêt de sécurité et l'alarme
═══════════════════════════════════════════════════════════════════════════════
"""

import time
import math
from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from gazebo_msgs.srv import SetEntityState
from gazebo_msgs.msg import EntityState
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseWithCovarianceStamped


class WorkerPatrolNode(Node):
    """
    Contrôleur de trajectoire pour l'opérateur d'atelier 'human_worker_pedestrian'.
    Met à jour la pose dans Gazebo via /set_entity_state.
    """

    def __init__(self):
        super().__init__(
            "worker_patrol_node",
            parameter_overrides=[
                Parameter("use_sim_time", Parameter.Type.BOOL, True)
            ]
        )

        self.model_name = "human_worker_pedestrian"
        self.set_state_client = self.create_client(SetEntityState, "/set_entity_state")

        # ── Paramètres cinématiques de marche
        self.y_aisle: float = -1.60
        self.z_ground: float = 0.0
        self.x_start: float = 1.50
        self.x_end: float = -1.50
        self.current_x: float = self.x_start
        self.walk_speed: float = 0.32  # m/s (marche normale d'atelier)

        self.is_crossing: bool = False
        self.has_completed_cross: bool = False
        self.trigger_received: bool = False

        # ── Souscriptions
        self.sub_mission = self.create_subscription(
            String, "/mission_state", self._mission_state_cb, 10
        )
        self.sub_amcl = self.create_subscription(
            PoseWithCovarianceStamped, "/amcl_pose", self._amcl_cb, 10
        )

        # ── Timer d'animation à 20 Hz
        self.timer = self.create_timer(0.05, self._patrol_tick)

        self.get_logger().info(
            f"[WORKER PATROL] Prêt. Opérateur positionné en attente à x={self.x_start:.2f}, y={self.y_aisle:.2f}"
        )

    def _mission_state_cb(self, msg: String):
        # Dès que l'AMR part vers ST1, on arme la traversée
        if "NAVIGATING_TO_ST1" in msg.data or "MISSION_DISPATCHED" in msg.data:
            if not self.has_completed_cross and not self.is_crossing:
                self.trigger_received = True

    def _amcl_cb(self, msg: PoseWithCovarianceStamped):
        # Déclenchement basé sur la position exacte de l'AMR :
        # Quand l'AMR quitte ST0 (y=-3.8) et atteint y >= -2.60 m (à ~1 m du couloir du piéton)
        robot_y = msg.pose.pose.position.y
        robot_x = msg.pose.pose.position.x
        if robot_y >= -2.60 and robot_y <= -1.00 and not self.has_completed_cross and not self.is_crossing:
            self.get_logger().info(
                f"[WORKER PATROL] AMR détecté à l'approche de l'allée (y={robot_y:.2f}) -> Début de la traversée piéton !"
            )
            self.is_crossing = True

    def set_worker_pose(self, x: float, y: float, yaw: float = 3.14159):
        if not self.set_state_client.service_is_ready():
            return

        req = SetEntityState.Request()
        req.state.name = self.model_name
        req.state.pose.position.x = float(x)
        req.state.pose.position.y = float(y)
        req.state.pose.position.z = float(self.z_ground)

        # Quaternion de cap
        req.state.pose.orientation.z = math.sin(yaw / 2.0)
        req.state.pose.orientation.w = math.cos(yaw / 2.0)
        req.state.reference_frame = "world"

        self.set_state_client.call_async(req)

    def _patrol_tick(self):
        # Initialisation ou maintien à la pose de départ si pas encore déclenché
        if not self.is_crossing and not self.has_completed_cross:
            # Si le déclencheur d'état est reçu mais pas encore la position, démarrer après 4s
            if self.trigger_received:
                self.is_crossing = True
                self.get_logger().info("[WORKER PATROL] Déclenchement automatique de la traversée de l'employeur !")
            return

        if self.is_crossing:
            dt = 0.05
            dx = self.walk_speed * dt
            self.current_x -= dx

            # Animation subtile d'oscillation verticale de la tête/torso lors du pas
            step_bobbing = 0.015 * math.sin(time.time() * 8.0)
            self.z_ground = max(0.0, step_bobbing)

            self.set_worker_pose(self.current_x, self.y_aisle, yaw=3.14159)

            if self.current_x <= self.x_end:
                self.current_x = self.x_end
                self.is_crossing = False
                self.has_completed_cross = True
                self.z_ground = 0.0
                self.set_worker_pose(self.current_x, self.y_aisle, yaw=3.14159)
                self.get_logger().info(
                    f"[WORKER PATROL] ✓ Traversée achevée ! L'opérateur est en sécurité sur le quai Ouest (x={self.current_x:.2f})."
                )


def main():
    rclpy.init()
    node = WorkerPatrolNode()

    # Attente du service Gazebo
    node.get_logger().info("[WORKER PATROL] Connexion au service Gazebo /set_entity_state...")
    while not node.set_state_client.wait_for_service(timeout_sec=2.0):
        if not rclpy.ok():
            return
        node.get_logger().info("[WORKER PATROL] En attente de Gazebo /set_entity_state...")

    # Positionnement initial de l'employeur
    node.set_worker_pose(node.x_start, node.y_aisle, yaw=3.14159)
    node.get_logger().info("[WORKER PATROL] Opérateur positionné au bord Est du passage piéton.")

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
