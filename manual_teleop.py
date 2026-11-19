#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  PILOTAGE MANUEL & CARTOGRAPHIE SLAM INTERACTIVE — RAIA AMR (Projet 01.26)
  Permet de piloter manuellement l'AMR pour construire la carte dès le début,
  avec rampe d'accélération fluide, télémétrie temps réel et raccourci 'M'
  pour sauvegarder automatiquement la carte générée par SLAM Toolbox !
═══════════════════════════════════════════════════════════════════════════════
"""

import sys
import os
import tty
import termios
import select
import time
import math
import subprocess
import threading
from typing import Optional

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry, OccupancyGrid


class ManualTeleopNode(Node):
    """Nœud ROS 2 de téléopération et monitoring de cartographie SLAM."""

    def __init__(self):
        super().__init__(
            "raia_manual_teleop",
            parameter_overrides=[Parameter("use_sim_time", Parameter.Type.BOOL, True)]
        )

        self.pub_cmd_vel = self.create_publisher(Twist, "/cmd_vel", 10)
        self.sub_odom = self.create_subscription(Odometry, "/odom", self._odom_cb, 10)
        self.sub_map = self.create_subscription(OccupancyGrid, "/map", self._map_cb, 10)

        # Cibles de vitesse
        self.target_linear: float = 0.0
        self.target_angular: float = 0.0
        self.current_linear: float = 0.0
        self.current_angular: float = 0.0

        # Paramètres ajustables
        self.max_linear: float = 0.35   # m/s
        self.max_angular: float = 0.80  # rad/s
        self.accel_linear: float = 0.60 # m/s²
        self.accel_angular: float = 1.20# rad/s²

        # Télémétrie
        self.pose_x: float = 0.0
        self.pose_y: float = 0.0
        self.pose_yaw: float = 0.0
        self.distance_traveled: float = 0.0
        self._last_odom_x: Optional[float] = None
        self._last_odom_y: Optional[float] = None

        # Infos carte SLAM
        self.map_received: bool = False
        self.map_width: int = 0
        self.map_height: int = 0
        self.map_resolution: float = 0.05
        self.map_explored_pct: float = 0.0

        # Statut sauvegarde
        self.save_status: str = "Prêt (Appuyez sur 'M' pour sauvegarder la carte)"
        self.save_in_progress: bool = False

        # Boucle de contrôle à 20 Hz
        self.dt: float = 0.05
        self.timer = self.create_timer(self.dt, self._control_loop)

    def _odom_cb(self, msg: Odometry):
        p = msg.pose.pose.position
        self.pose_x = p.x
        self.pose_y = p.y
        q = msg.pose.pose.orientation
        # Calcul yaw
        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
        self.pose_yaw = math.atan2(siny_cosp, cosy_cosp)

        if self._last_odom_x is not None and self._last_odom_y is not None:
            ds = math.hypot(p.x - self._last_odom_x, p.y - self._last_odom_y)
            if ds < 1.0:  # filtre saut de repère
                self.distance_traveled += ds
        self._last_odom_x = p.x
        self._last_odom_y = p.y

    def _map_cb(self, msg: OccupancyGrid):
        self.map_received = True
        self.map_width = msg.info.width
        self.map_height = msg.info.height
        self.map_resolution = msg.info.resolution
        
        # Calcul des cellules explorées (valeur >= 0)
        data = msg.data
        if data:
            known_cells = sum(1 for v in data if v >= 0)
            self.map_explored_pct = round(100.0 * known_cells / len(data), 1)

    def _control_loop(self):
        """Rampe d'accélération progressive pour éviter tout patinage ou saccade."""
        # Rampe linéaire
        delta_v = self.accel_linear * self.dt
        if self.current_linear < self.target_linear:
            self.current_linear = min(self.target_linear, self.current_linear + delta_v)
        elif self.current_linear > self.target_linear:
            self.current_linear = max(self.target_linear, self.current_linear - delta_v)

        # Rampe angulaire
        delta_w = self.accel_angular * self.dt
        if self.current_angular < self.target_angular:
            self.current_angular = min(self.target_angular, self.current_angular + delta_w)
        elif self.current_angular > self.target_angular:
            self.current_angular = max(self.target_angular, self.current_angular - delta_w)

        # Publication Twist
        tw = Twist()
        tw.linear.x = float(self.current_linear)
        tw.angular.z = float(self.current_angular)
        self.pub_cmd_vel.publish(tw)

    def stop_robot(self):
        self.target_linear = 0.0
        self.target_angular = 0.0
        self.current_linear = 0.0
        self.current_angular = 0.0
        tw = Twist()
        self.pub_cmd_vel.publish(tw)

    def save_map(self):
        """Sauvegarde de la carte SLAM via nav2_map_server."""
        if self.save_in_progress:
            return
        
        def _save_worker():
            self.save_in_progress = True
            self.save_status = "Sauvegarde en cours dans maps/raia_factory_map..."
            
            pkg_dir = os.path.dirname(os.path.abspath(__file__))
            maps_dir = os.path.join(pkg_dir, "maps")
            os.makedirs(maps_dir, exist_ok=True)
            target_prefix = os.path.join(maps_dir, "raia_factory_map")
            
            cmd = [
                "ros2", "run", "nav2_map_server", "map_saver_cli",
                "-f", target_prefix,
                "--ros-args", "-p", "use_sim_time:=true"
            ]
            try:
                p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=25)
                if p.returncode == 0:
                    # Copier également vers baseline pour conservation
                    pgm_src = target_prefix + ".pgm"
                    pgm_baseline = os.path.join(maps_dir, "raia_factory_map_baseline.pgm")
                    if os.path.exists(pgm_src):
                        import shutil
                        shutil.copyfile(pgm_src, pgm_baseline)
                    self.save_status = f"✓ CARTE SAUVEGARDÉE AVEC SUCCÈS ({time.strftime('%H:%M:%S')}) !"
                else:
                    self.save_status = f"Erreur code {p.returncode}: {p.stderr[:60]}"
            except Exception as e:
                self.save_status = f"Erreur exception: {str(e)[:60]}"
            finally:
                self.save_in_progress = False

        t = threading.Thread(target=_save_worker, daemon=True)
        t.start()

    def apply_keepout_and_obstacles(self):
        """Applique l'obstacle fixe et les zones d'exclusion sur la carte."""
        pkg_dir = os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(pkg_dir, "apply_fixed_obstacles_and_keepout.py")
        if os.path.exists(script):
            self.save_status = "Inscription des obstacles et zones interdites..."
            try:
                res = subprocess.run([sys.executable, script], capture_output=True, text=True, timeout=10)
                if res.returncode == 0:
                    self.save_status = "✓ Obstacles fixes et Keep-Out Zones appliqués !"
                else:
                    self.save_status = "Erreur lors de l'application des obstacles."
            except Exception as e:
                self.save_status = f"Erreur: {e}"


def get_key(settings, timeout=0.1) -> str:
    """Lecture non-bloquante d'une touche au clavier."""
    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    if rlist:
        ch = sys.stdin.read(1)
        # Gestion des séquences ANSI flèches
        if ch == '\x1b':
            seq = sys.stdin.read(2)
            if seq == '[A': return 'UP'
            if seq == '[B': return 'DOWN'
            if seq == '[C': return 'RIGHT'
            if seq == '[D': return 'LEFT'
        return ch
    return ''


def draw_hud(node: ManualTeleopNode):
    """Affiche un tableau de bord textuel dynamique et ergonomique."""
    # Effacer et repositionner curseur
    sys.stdout.write("\033[H\033[J")
    
    linear_bar = "█" * int(abs(node.current_linear) / 0.03)
    angular_bar = "█" * int(abs(node.current_angular) / 0.08)

    print("╔═══════════════════════════════════════════════════════════════════════╗")
    print("║        RAIA AMR — PILOTAGE MANUEL ET CARTOGRAPHIE SLAM (01.26)        ║")
    print("╚═══════════════════════════════════════════════════════════════════════╝")
    
    print("\n  \033[1;36m[COMMANDES DE DÉPLACEMENT]\033[0m")
    print("    \033[1;32mZ\033[0m ou \033[1;32mFlèche Haut\033[0m   : Avancer              \033[1;33m+\033[0m / \033[1;33m-\033[0m : Ajuster vit. linéaire (±0.05)")
    print("    \033[1;32mS\033[0m ou \033[1;32mFlèche Bas\033[0m    : Reculer              \033[1;33m*\033[0m / \033[1;33m/\033[0m : Ajuster vit. angulaire (±0.10)")
    print("    \033[1;32mQ\033[0m ou \033[1;32mFlèche Gauche\033[0m : Rotation Gauche      \033[1;35mESPACE\033[0m : Arrêt d'urgence immédiat")
    print("    \033[1;32mD\033[0m ou \033[1;32mFlèche Droite\033[0m : Rotation Droite      \033[1;31mCtrl+C\033[0m : Quitter")
    print("    \033[1;34mM\033[0m                 : \033[1;34mSAUVEGARDER LA CARTE (map_saver_cli)\033[0m")
    print("    \033[1;34mK\033[0m                 : Appliquer Obstacles Fixes + Zones Interdites")

    print("\n  \033[1;36m[TÉLÉMÉTRIE VÉHICULE & DYNAMIQUE]\033[0m")
    print(f"    Vitesse Linéaire  : \033[1;32m{node.current_linear:+5.2f} m/s\033[0m  (max: {node.max_linear:.2f} m/s)  [{linear_bar:<15}]")
    print(f"    Vitesse Angulaire : \033[1;33m{node.current_angular:+5.2f} rad/s\033[0m(max: {node.max_angular:.2f} rad/s) [{angular_bar:<15}]")
    yaw_deg = math.degrees(node.pose_yaw)
    print(f"    Position Robot    : X={node.pose_x:+5.2f} m | Y={node.pose_y:+5.2f} m | Cap={yaw_deg:+6.1f}°")
    print(f"    Distance parcourue: {node.distance_traveled:.2f} m")

    print("\n  \033[1;36m[ÉTAT DE LA CARTOGRAPHIE SLAM]\033[0m")
    if node.map_received:
        print(f"    Grille de Coût    : \033[1;32m{node.map_width} × {node.map_height} cellules\033[0m (résolution: {node.map_resolution:.2f} m/px)")
        print(f"    Zone Découverte   : \033[1;32m{node.map_explored_pct}%\033[0m de la surface de l'atelier")
    else:
        print("    Grille de Coût    : \033[1;33mEn attente du topic /map (SLAM Toolbox)... \033[0m")

    print(f"\n  \033[1;33m[NOTIFICATION]\033[0m {node.save_status}")
    print("═══════════════════════════════════════════════════════════════════════")
    sys.stdout.flush()


def main(args=None):
    rclpy.init(args=args)
    node = ManualTeleopNode()

    # Exécution de ROS 2 dans un thread d'arrière-plan
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()

    # Configuration terminal en mode non canonique (raw)
    old_settings = termios.tcgetattr(sys.stdin)
    tty.setcbreak(sys.stdin.fileno())

    last_hud_update = 0.0

    try:
        while rclpy.ok():
            key = get_key(old_settings, timeout=0.08)

            if key in ['z', 'Z', 'w', 'W', 'UP']:
                node.target_linear = node.max_linear
                node.target_angular = 0.0
            elif key in ['s', 'S', 'DOWN']:
                node.target_linear = -node.max_linear
                node.target_angular = 0.0
            elif key in ['q', 'Q', 'a', 'A', 'LEFT']:
                node.target_angular = node.max_angular
            elif key in ['d', 'D', 'RIGHT']:
                node.target_angular = -node.max_angular
            elif key == ' ':
                node.stop_robot()
            elif key in ['+', '=']:
                node.max_linear = min(0.70, round(node.max_linear + 0.05, 2))
            elif key in ['-', '_']:
                node.max_linear = max(0.10, round(node.max_linear - 0.05, 2))
            elif key == '*':
                node.max_angular = min(1.50, round(node.max_angular + 0.10, 2))
            elif key == '/':
                node.max_angular = max(0.20, round(node.max_angular - 0.10, 2))
            elif key in ['m', 'M']:
                node.save_map()
            elif key in ['k', 'K']:
                node.apply_keepout_and_obstacles()
            elif key == '\x03':  # Ctrl+C
                break
            else:
                # Si aucune touche n'est pressée pendant 0.25s, décélération automatique vers 0
                node.target_linear = 0.0
                node.target_angular = 0.0

            # Rafraîchissement HUD à ~5 Hz
            now = time.time()
            if now - last_hud_update > 0.18:
                draw_hud(node)
                last_hud_update = now

    except KeyboardInterrupt:
        pass
    finally:
        node.stop_robot()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        print("\nArrêt du pilotage manuel. Robot immobilisé.")
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
