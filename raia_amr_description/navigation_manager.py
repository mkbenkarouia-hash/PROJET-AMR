#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  MODULE GESTIONNAIRE DE NAVIGATION AUTONOME — RAIA AMR
  Atelier Industriel 4.0 | factory_workshop.world
  Orchestre les missions de navigation Nav2 vers les stations de l'atelier
═══════════════════════════════════════════════════════════════════════════════
"""

import time
import math
import os
import signal
import subprocess
from typing import Optional, List, Tuple, Dict, Any, Callable
from enum import Enum

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.action import ActionClient
from rclpy.time import Time
from rclpy.duration import Duration
import tf2_ros
from geometry_msgs.msg import PoseStamped, Twist, PoseWithCovarianceStamped
from std_msgs.msg import String, Bool
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from nav2_msgs.action import NavigateToPose, NavigateThroughPoses

from station_manager import StationManager, Station


class NavState(Enum):
    IDLE = "IDLE"
    PREPARING = "PREPARING"
    PLANNING = "PLANNING"
    NAVIGATING = "NAVIGATING"
    DWELLING = "DWELLING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


def yaw_to_quaternion(yaw: float) -> Tuple[float, float, float, float]:
    """Convertit un angle de lacet (yaw en radians) en quaternion (x, y, z, w)."""
    return (0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0))


def yaw_from_quaternion(x: float, y: float, z: float, w: float) -> float:
    """Convertit un quaternion (x, y, z, w) en angle de lacet (yaw en radians)."""
    t3 = 2.0 * (w * z + x * y)
    t4 = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(t3, t4)


class NavigationManager(Node):
    """
    Contrôleur de navigation autonome haute fiabilité pour l'AMR RAIA.
    Gère la localisation TF2, les préconditions de sécurité, l'envoi de buts Nav2,
    le suivi temps réel et le chaînage multi-stations.
    """

    def __init__(self, node_name: str = "raia_navigation_manager"):
        super().__init__(
            node_name,
            parameter_overrides=[
                Parameter("use_sim_time", Parameter.Type.BOOL, True)
            ]
        )

        # ── Gestionnaire des stations
        self.station_mgr = StationManager()

        # ── Clients d'action Nav2
        self._nav_to_pose_client = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self._nav_through_poses_client = ActionClient(self, NavigateThroughPoses, "navigate_through_poses")

        # ── Suivi TF2 (map -> base_footprint)
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        # ── Souscriptions
        self.sub_odom = self.create_subscription(Odometry, "/odom", self._odom_callback, 10)
        self.sub_amcl = self.create_subscription(PoseWithCovarianceStamped, "/amcl_pose", self._amcl_callback, 10)

        # ── Signaux opérateur & supervision atelier
        self.sub_operator_call = self.create_subscription(
            String, "/operator_call", self._operator_call_cb, 10
        )
        self.sub_line_button = self.create_subscription(
            Bool, "/line_call_button", self._line_button_cb, 10
        )
        self.pub_mission_state = self.create_publisher(String, "/mission_state", 10)
        self.pub_initialpose = self.create_publisher(PoseWithCovarianceStamped, "/initialpose", 10)

        # ── Avertisseur sonore et sécurité dynamique d'évitement (Norme ISO 3691-4)
        self.sub_scan = self.create_subscription(LaserScan, "/scan", self._scan_callback, 10)
        self.pub_cmd_vel = self.create_publisher(Twist, "/cmd_vel", 10)

        self.safety_obstacle_detected: bool = False
        self.safety_obstacle_dist: float = 999.0
        self.is_safety_stopped: bool = False
        self._obstacle_clear_counter: int = 0
        self.sound_process: Optional[subprocess.Popen] = None

        self.sound_wav_path: str = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "sounds",
            "amr_safety_melody.wav"
        )

        self.operator_call_received: bool = False
        self.operator_call_source: str = "Bouton d'appel Ligne 1 (Sérigraphie MPM)"
        self.operator_call_payload: str = "Demande d'enlèvement d'une carte PCB terminée"

        # ── Variables d'état
        self.state: NavState = NavState.IDLE
        self.current_x: float = 0.0
        self.current_y: float = 0.0
        self.current_yaw: float = 0.0
        self.current_lin_vel: float = 0.0
        self.current_ang_vel: float = 0.0
        self.has_pose: bool = False
        self.current_target: Optional[Station] = None
        self.distance_remaining: float = 0.0
        self.last_status_text: str = "Prêt"

        # Callbacks d'événement externes (UI / Supervision)
        self.on_state_change: Optional[Callable[[NavState, str], None]] = None
        self.on_progress: Optional[Callable[[float, float, float, float], None]] = None

        self._active_goal_handle = None

    def _set_state(self, state: NavState, msg: str = ""):
        self.state = state
        self.last_status_text = msg
        if self.on_state_change:
            try:
                self.on_state_change(state, msg)
            except Exception:
                pass

    def _odom_callback(self, msg: Odometry):
        self.current_lin_vel = msg.twist.twist.linear.x
        self.current_ang_vel = msg.twist.twist.angular.z

    def _amcl_callback(self, msg: PoseWithCovarianceStamped):
        """Mise à jour directe depuis le filtre de particules AMCL."""
        self.current_x = msg.pose.pose.position.x
        self.current_y = msg.pose.pose.position.y
        q = msg.pose.pose.orientation
        self.current_yaw = yaw_from_quaternion(q.x, q.y, q.z, q.w)
        self.has_pose = True

    def _operator_call_cb(self, msg: String):
        self.operator_call_received = True
        self.operator_call_payload = msg.data
        self.get_logger().info(f"[SIGNAL OPÉRATEUR] Appel reçu sur /operator_call : '{msg.data}'")

    def _line_button_cb(self, msg: Bool):
        if msg.data:
            self.operator_call_received = True
            self.get_logger().info("[SIGNAL OPÉRATEUR] Bouton physique d'appel enfoncé (/line_call_button) !")

    def publish_mission_state(self, state_text: str):
        msg = String()
        msg.data = state_text
        self.pub_mission_state.publish(msg)

    def _scan_callback(self, msg: LaserScan):
        """
        Surveillance temps réel du champ de sécurité frontal (LiDAR 2D Hokuyo).
        Définit un gabarit de sécurité dynamique (Protection Field) :
        x dans [0.18, 1.05] m et |y| <= 0.28 m.
        Actif uniquement en cours de transit (distance restante à la station > 1.25 m).
        """
        # Exclure les phases de repos ou d'approche terminale aux stations de production
        if self.state != NavState.NAVIGATING or self.distance_remaining < 1.25:
            self.safety_obstacle_detected = False
            self.safety_obstacle_dist = 999.0
            return

        min_d = 999.0
        detected = False

        angle = msg.angle_min
        for r in msg.ranges:
            if msg.range_min < r < msg.range_max and not math.isinf(r) and not math.isnan(r):
                # Projection cartésienne dans le repère base_link
                x_rel = r * math.cos(angle)
                y_rel = r * math.sin(angle)

                # Couloir direct de déplacement frontal de l'AMR (largeur robot + marge)
                if 0.18 < x_rel < 1.05 and abs(y_rel) < 0.28:
                    detected = True
                    if x_rel < min_d:
                        min_d = x_rel
            angle += msg.angle_increment

        if detected:
            self.safety_obstacle_detected = True
            self.safety_obstacle_dist = min_d
            self._obstacle_clear_counter = 0
        else:
            self._obstacle_clear_counter += 1
            if self._obstacle_clear_counter >= 5:
                self.safety_obstacle_detected = False
                self.safety_obstacle_dist = 999.0

    def _start_safety_melody(self):
        """Déclenche la mélodie d'avertissement sonore en boucle asynchrone."""
        if self.sound_process is not None and self.sound_process.poll() is None:
            return

        env = dict(os.environ)
        if os.path.exists("/mnt/wslg/PulseServer"):
            env["PULSE_SERVER"] = "/mnt/wslg/PulseServer"

        cmd = (
            f"while true; do "
            f"paplay '{self.sound_wav_path}' 2>/dev/null || "
            f"aplay -q '{self.sound_wav_path}' 2>/dev/null || "
            f"sleep 1; sleep 0.2; done"
        )
        try:
            self.sound_process = subprocess.Popen(
                cmd, shell=True, env=env, preexec_fn=os.setsid
            )
        except Exception as e:
            self.get_logger().warn(f"[AVERTISSEUR] Erreur lancement audio : {e}")

    def _stop_safety_melody(self):
        """Interrompt immédiatement la mélodie dès dégagement du passage."""
        if self.sound_process is not None:
            try:
                os.killpg(os.getpgid(self.sound_process.pid), signal.SIGTERM)
            except Exception:
                try:
                    self.sound_process.kill()
                except Exception:
                    pass
            self.sound_process = None

    def update_robot_pose(self) -> bool:
        """Met à jour la pose exacte du robot dans le repère 'map' via TF2."""
        try:
            trans = self.tf_buffer.lookup_transform(
                "map",
                "base_footprint",
                rclpy.time.Time()
            )
            self.current_x = trans.transform.translation.x
            self.current_y = trans.transform.translation.y
            q = trans.transform.rotation
            self.current_yaw = yaw_from_quaternion(q.x, q.y, q.z, q.w)
            self.has_pose = True
            return True
        except Exception:
            return False

    def set_initial_pose_amcl(
        self,
        x: float = 0.0,
        y: float = -3.80,
        theta: float = 1.5708,
        retries: int = 6
    ) -> bool:
        """
        Initialise et amorce le filtre particulaire AMCL en publiant sur /initialpose.
        Garantit la synchronisation temporelle sim_time sous WSL2 et la continuité TF map -> odom.
        """
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = "map"
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.pose.position.x = x
        msg.pose.pose.position.y = y
        msg.pose.pose.position.z = 0.0

        qx, qy, qz, qw = yaw_to_quaternion(theta)
        msg.pose.pose.orientation.x = qx
        msg.pose.pose.orientation.y = qy
        msg.pose.pose.orientation.z = qz
        msg.pose.pose.orientation.w = qw

        msg.pose.covariance[0] = 0.05
        msg.pose.covariance[7] = 0.05
        msg.pose.covariance[35] = 0.05

        self.get_logger().info(
            f"[AMCL] Amorçage initialpose à ({x:.2f}, {y:.2f}, {math.degrees(theta):.1f}°)..."
        )

        for attempt in range(retries):
            msg.header.stamp = self.get_clock().now().to_msg()
            self.pub_initialpose.publish(msg)
            for _ in range(4):
                rclpy.spin_once(self, timeout_sec=0.1)
            if self.update_robot_pose():
                self.get_logger().info(
                    f"[AMCL] ✓ Arbre TF 'map' -> 'base_footprint' vérifié et actif ! Pose : ({self.current_x:.2f}, {self.current_y:.2f})"
                )
                return True
            time.sleep(0.2)

        return self.update_robot_pose()

    def verify_preconditions(self, target: Station, timeout_sec: float = 15.0) -> Tuple[bool, str]:
        """
        Valide l'ensemble des préconditions techniques avant tout lancement :
        1. Serveur d'action Nav2 accessible
        2. Arbre TF 'map' -> 'base_footprint' synchronisé ou pose AMCL active
        3. Coordonnées de la station dans le périmètre de travail de l'atelier
        """
        self._set_state(NavState.PREPARING, "Vérification des préconditions de sécurité...")

        # 1. Action server
        if not self._nav_to_pose_client.wait_for_server(timeout_sec=timeout_sec):
            err = "Échec : Le serveur d'action Nav2 'navigate_to_pose' est indisponible !"
            self._set_state(NavState.FAILED, err)
            return False, err

        # 2. Localisation (TF connectée et synchronisée)
        start_wait = time.time()
        loc_ok = False
        while (time.time() - start_wait) < 5.0:
            rclpy.spin_once(self, timeout_sec=0.2)
            if self.update_robot_pose():
                loc_ok = True
                break

        if not loc_ok:
            # Auto-réparation TF / AMCL via amorçage initialpose
            self.get_logger().warn("[SÉCURITÉ] Arbre TF map->base_footprint non détecté, amorçage automatique AMCL...")
            if self.set_initial_pose_amcl(0.0, -3.80, 1.5708):
                loc_ok = True

        if not loc_ok:
            err = "Échec : Localisation 'map' -> 'base_footprint' introuvable. AMCL n'a pas encore fourni de pose !"
            self._set_state(NavState.FAILED, err)
            return False, err

        # 3. Limites de l'atelier (factory_workshop.world est un rectangle de 10x10 m, soit x,y dans [-4.8, 4.8])
        if abs(target.x) > 4.6 or abs(target.y) > 4.6:
            err = f"Échec : Coordonnées de la cible ({target.x}, {target.y}) hors limites de sécurité !"
            self._set_state(NavState.FAILED, err)
            return False, err

        return True, "Toutes les préconditions sont validées avec succès."

    def navigate_to_station(
        self,
        station_id_or_name: str,
        timeout_sec: float = 90.0,
        dwell_time_sec: float = 2.0,
        dwell_action_desc: str = ""
    ) -> bool:
        """
        Exécute la navigation complète et sécurisée vers une station cible.
        """
        station = self.station_mgr.get_station(station_id_or_name)
        if not station:
            self.get_logger().error(f"Station inconnue : '{station_id_or_name}'")
            return False

        self.current_target = station
        ok, msg = self.verify_preconditions(station)
        if not ok:
            self.get_logger().error(msg)
            return False

        self.get_logger().info(
            f"[MISSION] Lancement navigation vers [{station.id}] '{station.name}' "
            f"à ({station.x:.2f}, {station.y:.2f}, {station.theta_deg:.1f}°)"
        )

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = "map"
        # Time(0) ordonne à TF2 d'utiliser la transformation la plus récente dans le buffer
        goal_msg.pose.header.stamp = rclpy.time.Time().to_msg()
        goal_msg.pose.pose.position.x = station.x
        goal_msg.pose.pose.position.y = station.y
        goal_msg.pose.pose.position.z = 0.0

        qx, qy, qz, qw = yaw_to_quaternion(station.theta)
        goal_msg.pose.pose.orientation.x = qx
        goal_msg.pose.pose.orientation.y = qy
        goal_msg.pose.pose.orientation.z = qz
        goal_msg.pose.pose.orientation.w = qw

        self._set_state(NavState.PLANNING, f"Calcul du plan vers {station.id}...")
        send_future = self._nav_to_pose_client.send_goal_async(
            goal_msg,
            feedback_callback=self._nav_feedback_cb
        )
        rclpy.spin_until_future_complete(self, send_future)

        goal_handle = send_future.result()
        if not goal_handle.accepted:
            err = f"Nav2 a rejeté l'objectif vers [{station.id}] !"
            self.get_logger().error(err)
            self._set_state(NavState.FAILED, err)
            return False

        self.is_safety_stopped = False
        self.safety_obstacle_detected = False
        self._obstacle_clear_counter = 5
        self._stop_safety_melody()

        self._active_goal_handle = goal_handle
        self._set_state(NavState.NAVIGATING, f"Déplacement en cours vers [{station.id}] {station.name}")

        result_future = goal_handle.get_result_async()
        start_time = time.time()
        last_log = time.time()

        while not result_future.done():
            rclpy.spin_once(self, timeout_sec=0.05)
            self.update_robot_pose()

            # Distance réelle calculée via TF
            real_dist = math.hypot(station.x - self.current_x, station.y - self.current_y)
            self.distance_remaining = real_dist

            # Surveillance et réaction immédiate sur détection d'obstacle mobile frontal
            if self.safety_obstacle_detected and self.distance_remaining >= 1.25:
                if not self.is_safety_stopped:
                    self.is_safety_stopped = True
                    self._start_safety_melody()
                    self.publish_mission_state("OBSTACLE_MOBILE_DETECTED_STOP")
                    print("\n" + "═" * 70)
                    print(f" ⚠️  [SÉCURITÉ AMR] OBSTACLE MOBILE DÉTECTÉ DANS LE COULOIR !")
                    print(f"    -> Distance mesurée par LiDAR : {self.safety_obstacle_dist:.2f} m")
                    print(f"    -> ACTION : Arrêt immédiat de sécurité (cmd_vel = 0)")
                    print(f"    -> AVERTISSEUR SONORE ACTIF : Diffusion mélodie d'alerte (amr_safety_melody.wav)...")
                    print("═" * 70 + "\n")

                # Maintien de l'arrêt complet du robot
                stop_twist = Twist()
                self.pub_cmd_vel.publish(stop_twist)
                time.sleep(0.04)
                continue

            elif self.is_safety_stopped and (not self.safety_obstacle_detected or self.distance_remaining < 1.25):
                self.is_safety_stopped = False
                self._stop_safety_melody()
                self.publish_mission_state("OBSTACLE_CLEARED_RESUMING")
                print("\n" + "═" * 70)
                print(f" ✓  [SÉCURITÉ AMR] COULOIR DE CIRCULATION DÉGAGÉ !")
                print(f"    -> L'opérateur piéton s'est éloigné de l'allée.")
                print(f"    -> Extinction de l'avertisseur sonore.")
                print(f"    -> Reprise autonome de la marche vers [{station.id}] {station.name}...")
                print("═" * 70 + "\n")

            if time.time() - last_log > 2.0:
                last_log = time.time()
                self.get_logger().info(
                    f" -> Position: ({self.current_x:5.2f}, {self.current_y:5.2f}) | "
                    f"Cap: {math.degrees(self.current_yaw):6.1f}° | "
                    f"Vitesse: {self.current_lin_vel:4.2f} m/s | "
                    f"Dist. restante: {real_dist:4.2f} m"
                )
                if self.on_progress:
                    try:
                        self.on_progress(self.current_x, self.current_y, self.current_yaw, real_dist)
                    except Exception:
                        pass

            if (time.time() - start_time) > timeout_sec:
                self.get_logger().warn(f"Timeout de mission dépassé ({timeout_sec}s) !")
                self.cancel_active_goal()
                self._set_state(NavState.FAILED, "Timeout de navigation dépassé")
                return False

        res = result_future.result()
        status = res.status  # 4 = SUCCEEDED, 5 = CANCELED, 6 = ABORTED
        self._active_goal_handle = None

        self.update_robot_pose()
        final_err_pos = math.hypot(station.x - self.current_x, station.y - self.current_y)
        final_err_yaw = abs(math.atan2(math.sin(station.theta - self.current_yaw), math.cos(station.theta - self.current_yaw)))

        # Validation stricte : statut Nav2 SUCCEEDED et erreur physique < tolérance
        arrival_ok = (status == 4) and (final_err_pos <= 0.35)

        if arrival_ok:
            self.get_logger().info(
                f"[SUCCÈS] Arrivée confirmée à [{station.id}] '{station.name}' | "
                f"Écart position : {final_err_pos*100:.1f} cm, Écart cap : {math.degrees(final_err_yaw):.1f}°"
            )
            if dwell_time_sec > 0:
                action_text = dwell_action_desc or f"Arrêt opérationnel à la station ({dwell_time_sec}s)..."
                self._set_state(NavState.DWELLING, action_text)
                self.get_logger().info(f" -> [OPÉRATION EN COURS] {action_text}")
                dwell_end = time.time() + dwell_time_sec
                while time.time() < dwell_end:
                    rclpy.spin_once(self, timeout_sec=0.1)

            self._set_state(NavState.SUCCEEDED, f"Station [{station.id}] atteinte avec succès")
            return True
        else:
            self.get_logger().error(
                f"[ÉCHEC] Navigation non complétée | Statut Nav2: {status}, "
                f"Écart position: {final_err_pos:.2f} m (max toléré: 0.35 m)"
            )
            self._set_state(NavState.FAILED, f"Échec d'atteinte de la station (écart {final_err_pos:.2f}m)")
            return False

    def execute_multi_station_route(
        self,
        station_id_sequence: List[str],
        dwell_time_per_station: float = 3.0
    ) -> Dict[str, Any]:
        """
        Étape 8 : Exécution d'un circuit de production multi-stations enchaînées.
        Par exemple : ['ST0', 'ST1', 'ST3', 'ST4', 'ST0']
        """
        route_summary = {
            "total_stations": len(station_id_sequence),
            "completed": [],
            "failed": None,
            "success": False
        }

        self.get_logger().info("═══════════════════════════════════════════════════════════════")
        self.get_logger().info(f" DÉBUT DE LA ROUTE DE PRODUCTION MULTI-STATIONS : {' -> '.join(station_id_sequence)}")
        self.get_logger().info("═══════════════════════════════════════════════════════════════")

        for idx, st_id in enumerate(station_id_sequence, start=1):
            self.get_logger().info(f"\n>>> [ÉTAPE {idx}/{len(station_id_sequence)}] Vers la station {st_id}")
            ok = self.navigate_to_station(st_id, dwell_time_sec=dwell_time_per_station)
            if ok:
                route_summary["completed"].append(st_id)
            else:
                route_summary["failed"] = st_id
                self.get_logger().error(f"Interruption de la route sur échec à la station {st_id}")
                return route_summary

        route_summary["success"] = True
        self.get_logger().info("\n═══════════════════════════════════════════════════════════════")
        self.get_logger().info(" [MISSION COMPLÈTE] Cycle industriel de production 100% VALIDÉ !")
        self.get_logger().info("═══════════════════════════════════════════════════════════════")
        return route_summary

    def cancel_active_goal(self):
        """Annule l'objectif actif de manière immédiate et sécurisée."""
        if self._active_goal_handle:
            self.get_logger().warn("[URGENCE] Demande d'annulation du but actif...")
            cancel_future = self._active_goal_handle.cancel_goal_async()
            rclpy.spin_until_future_complete(self, cancel_future)
            self._set_state(NavState.CANCELLED, "Mission annulée par l'opérateur")
            self._active_goal_handle = None

    def _nav_feedback_cb(self, feedback_msg):
        fb = feedback_msg.feedback
        self.distance_remaining = fb.distance_remaining

    def destroy_node(self):
        self._stop_safety_melody()
        super().destroy_node()


def main():
    rclpy.init()
    nav_mgr = NavigationManager()

    print("\n[NAVIGATION MANAGER] Initialisation et synchronisation TF en cours...")
    start_sync = time.time()
    while (time.time() - start_sync) < 12.0:
        rclpy.spin_once(nav_mgr, timeout_sec=0.2)
        if nav_mgr.update_robot_pose():
            print(f" -> Pose initiale AMR détectée : ({nav_mgr.current_x:.2f}, {nav_mgr.current_y:.2f}), Cap: {math.degrees(nav_mgr.current_yaw):.1f}°")
            break

    # Test : Navigation vers ST1 (Sérigraphie)
    success = nav_mgr.navigate_to_station("ST1", dwell_time_sec=2.0)
    print(f"\n═══════════════════════════════════════════════════════")
    print(f" Résultat navigation ST1 : {'SUCCÈS' if success else 'ÉCHEC'}")
    print(f"═══════════════════════════════════════════════════════")

    nav_mgr.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
