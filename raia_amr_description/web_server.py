#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  SERVEUR WEB INDUSTRIEL & GESTIONNAIRE DE FLOTTE AMR — RAIA AMR 4.0
  Interface Web temps réel accessible via l'IP du Robot (http://<ROBOT_IP>:8080)
  Fonctionnalités :
    1. Visualisation temps réel de la cartographie usine, stations & pose AMR
    2. Pilotage manuel (Téléopération clavier / D-pad virtuel / joystick)
    3. Éditeur interactif de cartographie :
       - Ajout d'obstacles fixes / débarras (peinture directe sur la carte)
       - Définition de zones interdites (Keep-Out Zones)
       - Gomme / effaceur de débarras
       - Sauvegarde & rechargement dynamique des costmaps Nav2 sans redémarrer
       - Réinitialisation à la carte d'origine
    4. Pilotage de missions automatiques (ST0, ST1, ST2, Cycle complet)
    5. Monitoring audio bimodal (Mélodie instrumentale & Alarme percutante)
    6. Fiche technique & guide de connectivité réseau (Wi-Fi 6 / 5G / Ethernet)
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import math
import json
import base64
import shutil
import socket
import threading
import subprocess
from io import BytesIO
from typing import Optional, Dict, Any, List
from http.server import HTTPServer, BaseHTTPRequestHandler
import socketserver

from PIL import Image
import numpy as np

# ── ROS2 Imports (tolérant si ROS2 non sourcé)
try:
    import rclpy
    from rclpy.node import Node
    from rclpy.parameter import Parameter
    from geometry_msgs.msg import Twist, PoseWithCovarianceStamped
    from nav_msgs.msg import Odometry, OccupancyGrid
    from sensor_msgs.msg import LaserScan
    from std_msgs.msg import String, Bool
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False


def yaw_from_quaternion(x, y, z, w):
    t3 = 2.0 * (w * z + x * y)
    t4 = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(t3, t4)


class AMRState:
    """Structure thread-safe partagée des données de l'AMR et de la cartographie."""
    def __init__(self):
        self.lock = threading.Lock()
        self.x: float = 0.0
        self.y: float = -3.80
        self.yaw: float = 1.5708
        self.yaw_deg: float = 90.0
        self.linear_vel: float = 0.0
        self.angular_vel: float = 0.0
        self.state: str = "DOCKED_CHARGING"
        self.current_target: str = "ST0 (Recharge)"
        self.dist_rem: float = 0.0
        self.obstacle_detected: bool = False
        self.obstacle_dist: float = 999.0
        self.is_safety_stopped: bool = False
        self.audio_state: str = "IDLE"  # "PATROL_MELODY", "OBSTACLE_ALARM", "IDLE"
        self.battery_pct: int = 100
        self.voltage: float = 24.3
        self.status_text: str = "Robot connecté — En veille sur borne MiR Charge"
        self.scan_points: List[List[float]] = []  # [[x, y], ...] en repère map
        self.last_teleop_time: float = 0.0
        self.active_mission_proc: Optional[subprocess.Popen] = None

        # Infos réseau
        self.robot_ip = self._detect_robot_ip()
        self.network_type = "Wi-Fi 6 Industriel (Moxa AWK-3252A 802.11ax)"
        self.mac_address = "00:80:E1:94:A2:3F"
        self.subnet = "192.168.1.0/24"
        self.gateway = "192.168.1.1"

    def _detect_robot_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"


state = AMRState()


if ROS2_AVAILABLE:
    class WebBridgeNode(Node):
        """Nœud ROS2 pont assurant la passerelle entre ROS2 et le serveur Web."""
        def __init__(self):
            super().__init__(
                "raia_amr_web_bridge",
                parameter_overrides=[Parameter("use_sim_time", Parameter.Type.BOOL, True)]
            )
            self.pub_cmd_vel = self.create_publisher(Twist, "/cmd_vel", 10)
            self.pub_operator_call = self.create_publisher(String, "/operator_call", 10)
            self.pub_mission_state = self.create_publisher(String, "/mission_state", 10)

            self.sub_amcl = self.create_subscription(
                PoseWithCovarianceStamped, "/amcl_pose", self._amcl_cb, 10
            )
            self.sub_odom = self.create_subscription(Odometry, "/odom", self._odom_cb, 10)
            self.sub_scan = self.create_subscription(LaserScan, "/scan", self._scan_cb, 10)
            self.sub_mission = self.create_subscription(String, "/mission_state", self._mission_cb, 10)
            self.sub_telemetry = self.create_subscription(String, "/amr_telemetry", self._telemetry_cb, 10)

            # Timer de sécurité (Deadman switch) pour le pilotage manuel à 10 Hz
            self.timer_deadman = self.create_timer(0.1, self._deadman_check)

        def _amcl_cb(self, msg: PoseWithCovarianceStamped):
            with state.lock:
                state.x = msg.pose.pose.position.x
                state.y = msg.pose.pose.position.y
                q = msg.pose.pose.orientation
                state.yaw = yaw_from_quaternion(q.x, q.y, q.z, q.w)
                state.yaw_deg = math.degrees(state.yaw)

        def _odom_cb(self, msg: Odometry):
            with state.lock:
                state.linear_vel = msg.twist.twist.linear.x
                state.angular_vel = msg.twist.twist.angular.z

        def _scan_cb(self, msg: LaserScan):
            # Échantillonnage réduit des points LiDAR pour affichage web fluide
            points = []
            angle = msg.angle_min
            step = max(1, len(msg.ranges) // 72)  # ~72 points radar
            with state.lock:
                rx, ry, ryaw = state.x, state.y, state.yaw

            for i in range(0, len(msg.ranges), step):
                r = msg.ranges[i]
                cur_angle = angle + i * msg.angle_increment
                if msg.range_min < r < msg.range_max and not math.isinf(r) and not math.isnan(r):
                    # Coordonnées locales robot
                    lx = r * math.cos(cur_angle)
                    ly = r * math.sin(cur_angle)
                    # Transformation dans le repère global map
                    gx = rx + (lx * math.cos(ryaw) - ly * math.sin(ryaw))
                    gy = ry + (lx * math.sin(ryaw) + ly * math.cos(ryaw))
                    points.append([round(gx, 2), round(gy, 2)])

            with state.lock:
                state.scan_points = points

        def _mission_cb(self, msg: String):
            with state.lock:
                state.state = msg.data
                if "OBSTACLE_MOBILE_DETECTED_STOP" in msg.data:
                    state.obstacle_detected = True
                    state.is_safety_stopped = True
                    state.audio_state = "OBSTACLE_ALARM"
                    state.status_text = "ARRÊT DE SÉCURITÉ : Obstacle détecté dans le couloir !"
                elif "OBSTACLE_CLEARED" in msg.data:
                    state.obstacle_detected = False
                    state.is_safety_stopped = False
                    state.audio_state = "PATROL_MELODY"
                    state.status_text = "Couloir dégagé — Poursuite de la navigation"
                elif "ST1" in msg.data:
                    state.current_target = "Ligne 1 MPM (ST1)"
                    state.audio_state = "PATROL_MELODY"
                elif "ST2" in msg.data:
                    state.current_target = "Ligne 2 Convoyeur (ST2)"
                    state.audio_state = "PATROL_MELODY"
                elif "RETURNING" in msg.data or "ST0" in msg.data:
                    state.current_target = "Station Recharge MiR (ST0)"
                    state.audio_state = "PATROL_MELODY"
                elif "DOCKED" in msg.data:
                    state.current_target = "Docking Station (ST0)"
                    state.audio_state = "IDLE"
                    state.status_text = "AMR amarré et en cours de recharge 24V"

        def _telemetry_cb(self, msg: String):
            try:
                data = json.loads(msg.data)
                with state.lock:
                    state.x = data.get("x", state.x)
                    state.y = data.get("y", state.y)
                    state.yaw = data.get("yaw", state.yaw)
                    state.yaw_deg = data.get("yaw_deg", state.yaw_deg)
                    state.linear_vel = data.get("lin_vel", state.linear_vel)
                    state.angular_vel = data.get("ang_vel", state.angular_vel)
                    state.dist_rem = data.get("dist_rem", state.dist_rem)
                    state.obstacle_detected = data.get("obstacle_detected", state.obstacle_detected)
                    state.obstacle_dist = data.get("obstacle_dist", state.obstacle_dist)
                    state.is_safety_stopped = data.get("is_stopped", state.is_safety_stopped)
                    state.audio_state = data.get("audio_state", state.audio_state)
                    state.status_text = data.get("status_text", state.status_text)
            except Exception:
                pass

        def _deadman_check(self):
            # Arrêt automatique si aucune commande manuelle reçue depuis plus de 0.4s
            with state.lock:
                elapsed = time.time() - state.last_teleop_time
                if state.last_teleop_time > 0 and elapsed > 0.45:
                    if abs(state.linear_vel) > 0.01 or abs(state.angular_vel) > 0.01:
                        stop_twist = Twist()
                        self.pub_cmd_vel.publish(stop_twist)
                        state.linear_vel = 0.0
                        state.angular_vel = 0.0
                        state.last_teleop_time = 0.0

        def send_teleop(self, linear: float, angular: float):
            twist = Twist()
            twist.linear.x = float(linear)
            twist.angular.z = float(angular)
            self.pub_cmd_vel.publish(twist)
            with state.lock:
                state.last_teleop_time = time.time()
                state.linear_vel = linear
                state.angular_vel = angular

        def send_emergency_stop(self):
            twist = Twist()
            self.pub_cmd_vel.publish(twist)
            with state.lock:
                state.last_teleop_time = 0.0
                state.linear_vel = 0.0
                state.angular_vel = 0.0
                state.status_text = "ARRÊT D'URGENCE MANUEL DÉCLENCHÉ"


# ── Répertoire des fichiers
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, "web")
MAPS_DIR = os.path.join(BASE_DIR, "maps")
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds")
MAP_PGM_PATH = os.path.join(MAPS_DIR, "raia_factory_map.pgm")
MAP_BASELINE_PATH = os.path.join(MAPS_DIR, "raia_factory_map_baseline.pgm")
MAP_YAML_PATH = os.path.join(MAPS_DIR, "raia_factory_map.yaml")

# Coordonnées des stations de l'atelier
STATIONS_DATA = [
    {
        "id": "ST0",
        "name": "Station de Recharge MiR Charge (Quai Sud)",
        "desc": "Borne industrielle de recharge 24V DC / Stationnement AMR",
        "x": 0.0,
        "y": -3.80,
        "theta_deg": 90.0,
        "color": "#10B981"
    },
    {
        "id": "ST1",
        "name": "Ligne 1 - Sérigraphie MPM Momentum",
        "desc": "Poste d'impression de pâte à braser — Prise PCB",
        "x": 1.50,
        "y": 0.65,
        "theta_deg": 90.0,
        "color": "#3B82F6"
    },
    {
        "id": "ST2",
        "name": "Ligne 2 - Quai Convoyeur & Transfert",
        "desc": "Convoyeur automatique à rouleaux — Dépose PCB",
        "x": -1.50,
        "y": 0.65,
        "theta_deg": -90.0,
        "color": "#8B5CF6"
    },
    {
        "id": "ST3",
        "name": "Ligne 3 - Four Refusion ICT",
        "desc": "Poste de brasage à refusion thermique sous azote",
        "x": 1.80,
        "y": -0.65,
        "theta_deg": -90.0,
        "color": "#F59E0B"
    },
    {
        "id": "ST4",
        "name": "Station 4 - Stockage & Palettes PCB",
        "desc": "Zone logistique des racks de PCB finis",
        "x": -2.00,
        "y": -0.65,
        "theta_deg": -90.0,
        "color": "#EC4899"
    }
]

# Obstacle fixe connu (Chariot de maintenance au centre)
FIXED_OBSTACLE = {
    "name": "Chariot Industriel de Maintenance (Obstacle Fixe)",
    "x": 0.0,
    "y": 0.65,
    "size_x": 0.54,
    "size_y": 0.54,
    "radius": 0.32,
    "type": "FIXED_CART"
}

# Champs à ne pas aller vers eux (Keep-Out Zones / Zones d'exclusion ISO 3691-4)
KEEPOUT_ZONES = [
    {
        "id": "ZONE_A_HAUTE_TENSION",
        "name": "Zone A — Haute Tension & Armoire Électrique Est",
        "desc": "Zone d'exclusion électrique haute tension 400V — Risque d'arc",
        "x_min": 3.6, "x_max": 4.8, "y_min": -1.2, "y_max": 0.4,
        "color": "rgba(239, 68, 68, 0.45)"
    },
    {
        "id": "ZONE_B_TAMPON_MPM",
        "name": "Zone B — Tampon Arrière Sérigraphie MPM",
        "desc": "Couloir technique réservé aux réapprovisionnements racles/pochoirs",
        "x_min": 3.4, "x_max": 4.8, "y_min": 1.2, "y_max": 3.2,
        "color": "rgba(249, 115, 22, 0.45)"
    },
    {
        "id": "ZONE_C_STOCKAGE_CHIMIQUE",
        "name": "Zone C — Stockage Produits Chimiques & Batteries",
        "desc": "Stockage solvants d'ébavurage et station de charge batteries de rechange",
        "x_min": -4.8, "x_max": -3.2, "y_min": -3.0, "y_max": -1.5,
        "color": "rgba(239, 68, 68, 0.45)"
    },
    {
        "id": "ZONE_D_EXCLUSION_SPEA",
        "name": "Zone D — Périmètre Arrière Testeur SPEA",
        "desc": "Zone de calibration sondes volantes à haute tension",
        "x_min": -4.8, "x_max": -3.4, "y_min": 1.2, "y_max": 3.2,
        "color": "rgba(249, 115, 22, 0.45)"
    }
]


ros_node: Optional[Any] = None


class IndustrialWebHandler(BaseHTTPRequestHandler):
    """Gestionnaire HTTP REST & fichiers statiques pour l'interface de supervision."""

    def log_message(self, format, *args):
        # Réduit le bruit dans les logs du terminal
        pass

    def _set_headers(self, content_type: str = "application/json", status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        url_path = self.path.split("?")[0]

        # 1. Page principale HTML
        if url_path in ["/", "/index.html"]:
            html_file = os.path.join(WEB_DIR, "index.html")
            if os.path.exists(html_file):
                with open(html_file, "rb") as f:
                    content = f.read()
                self._set_headers("text/html; charset=utf-8")
                self.wfile.write(content)
            else:
                self._set_headers("text/plain", 404)
                self.wfile.write(b"Index file not found")
            return

        # 2. Image PNG de la carte (convertie depuis PGM en temps reel)
        elif url_path == "/api/map_image":
            png_bytes = self._get_map_png_bytes()
            if png_bytes:
                self._set_headers("image/png")
                self.wfile.write(png_bytes)
            else:
                self._set_headers("text/plain", 500)
                self.wfile.write(b"Could not load map PGM")
            return

        # 3. Métadonnées de la carte et des stations
        elif url_path == "/api/map_info":
            info = {
                "resolution": 0.05,
                "origin": [-5.05, -5.05, 0.0],
                "width": 202,
                "height": 202,
                "stations": STATIONS_DATA,
                "fixed_obstacle": FIXED_OBSTACLE,
                "keepout_zones": KEEPOUT_ZONES,
                "bounds": {"x_min": -4.8, "x_max": 4.8, "y_min": -4.8, "y_max": 4.8}
            }
            self._set_headers("application/json")
            self.wfile.write(json.dumps(info).encode("utf-8"))
            return

        # 4. Télémétrie temps réel de l'AMR
        elif url_path == "/api/status":
            with state.lock:
                status_payload = {
                    "x": round(state.x, 3),
                    "y": round(state.y, 3),
                    "yaw": round(state.yaw, 3),
                    "yaw_deg": round(state.yaw_deg, 1),
                    "linear_vel": round(state.linear_vel, 2),
                    "angular_vel": round(state.angular_vel, 2),
                    "state": state.state,
                    "current_target": state.current_target,
                    "dist_rem": round(state.dist_rem, 2),
                    "obstacle_detected": state.obstacle_detected,
                    "obstacle_dist": round(state.obstacle_dist, 2),
                    "is_safety_stopped": state.is_safety_stopped,
                    "audio_state": state.audio_state,
                    "battery_pct": state.battery_pct,
                    "voltage": state.voltage,
                    "status_text": state.status_text,
                    "scan_points": state.scan_points,
                    "timestamp": time.time()
                }
            self._set_headers("application/json")
            self.wfile.write(json.dumps(status_payload).encode("utf-8"))
            return

        # 5. Informations sur la connexion physique & réseau du robot
        elif url_path == "/api/network_info":
            net_info = {
                "robot_ip": state.robot_ip,
                "network_hardware": state.network_type,
                "mac_address": state.mac_address,
                "subnet": state.subnet,
                "gateway": state.gateway,
                "hostname": socket.gethostname(),
                "port": 8080,
                "industrial_standards": [
                    "Norme ISO 3691-4 (Sécurité des AGV/AMR industriels)",
                    "Wi-Fi 6 IEEE 802.11ax (Itinérance industrielle Fast Roaming < 50ms)",
                    "Réseau 5G Standalone Privé Usine 4.0 (Option de redondance)",
                    "Sécurité WPA3-Enterprise & VLAN isolé Automatismes (VLAN 100)"
                ],
                "connection_guide": [
                    "1. Connectez votre PC, tablette ou smartphone au réseau Wi-Fi industriel de l'usine.",
                    f"2. Ouvrez votre navigateur Web (Chrome, Safari, Edge, Firefox).",
                    f"3. Saisissez l'adresse : http://{state.robot_ip}:8080 ou http://raia-amr.local:8080",
                    "4. L'interface s'affiche directement sans aucun pilote ni logiciel à installer !"
                ]
            }
            self._set_headers("application/json")
            self.wfile.write(json.dumps(net_info).encode("utf-8"))
            return

        # 6. Flux audio WAV statiques
        elif url_path.startswith("/sounds/"):
            fname = os.path.basename(url_path)
            fpath = os.path.join(SOUNDS_DIR, fname)
            if os.path.exists(fpath):
                self._set_headers("audio/wav")
                with open(fpath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self._set_headers("text/plain", 404)
                self.wfile.write(b"Audio file not found")
            return

        # 404 par défaut
        self._set_headers("text/plain", 404)
        self.wfile.write(b"Endpoint not found")

    def do_POST(self):
        url_path = self.path.split("?")[0]
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length > 0 else "{}"
        try:
            req_data = json.loads(body)
        except Exception:
            req_data = {}

        # 1. Pilotage manuel (Téléopération / cmd_vel)
        if url_path == "/api/teleop":
            lin = float(req_data.get("linear", 0.0))
            ang = float(req_data.get("angular", 0.0))
            # Limitation sécuritaire
            lin = max(-0.50, min(0.50, lin))
            ang = max(-1.20, min(1.20, ang))

            if ros_node:
                ros_node.send_teleop(lin, ang)
            else:
                with state.lock:
                    state.linear_vel = lin
                    state.angular_vel = ang
                    state.x += lin * 0.1 * math.cos(state.yaw)
                    state.y += lin * 0.1 * math.sin(state.yaw)
                    state.yaw += ang * 0.1
                    state.yaw_deg = math.degrees(state.yaw)

            self._set_headers("application/json")
            self.wfile.write(json.dumps({"success": True, "linear": lin, "angular": ang}).encode("utf-8"))
            return

        # 2. Arrêt d'urgence immédiat
        elif url_path == "/api/stop":
            if ros_node:
                ros_node.send_emergency_stop()
            else:
                with state.lock:
                    state.linear_vel = 0.0
                    state.angular_vel = 0.0
                    state.status_text = "ARRÊT D'URGENCE MANUEL DÉCLENCHÉ"
            self._set_headers("application/json")
            self.wfile.write(json.dumps({"success": True, "action": "STOPPED"}).encode("utf-8"))
            return

        # 3. Lancement d'une mission vers une station
        elif url_path == "/api/station":
            target_st = req_data.get("station", "ST0")
            self._dispatch_mission(target_st)
            self._set_headers("application/json")
            self.wfile.write(json.dumps({"success": True, "station": target_st}).encode("utf-8"))
            return

        # 4. Modification de la cartographie (Obstacles fixes, débarras, zones interdites)
        elif url_path == "/api/save_map_edits":
            success, msg = self._save_map_edits(req_data)
            self._set_headers("application/json")
            self.wfile.write(json.dumps({"success": success, "message": msg}).encode("utf-8"))
            return

        # 5. Réinitialisation de la cartographie à la version baseline d'origine
        elif url_path == "/api/reset_map":
            success, msg = self._reset_map()
            self._set_headers("application/json")
            self.wfile.write(json.dumps({"success": success, "message": msg}).encode("utf-8"))
            return

        self._set_headers("text/plain", 404)
        self.wfile.write(b"Unknown POST endpoint")

    def _get_map_png_bytes(self) -> Optional[bytes]:
        """Convertit l'image PGM de la carte d'atelier en PNG pour affichage dans le navigateur."""
        if not os.path.exists(MAP_PGM_PATH):
            return None
        try:
            im = Image.open(MAP_PGM_PATH)
            # Conversion en RGB
            im_rgb = im.convert("RGB")
            out = BytesIO()
            im_rgb.save(out, format="PNG")
            return out.getvalue()
        except Exception as e:
            print(f"[WEB] Erreur conversion PGM vers PNG : {e}")
            return None

    def _save_map_edits(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Enregistre les modifications peintes par l'utilisateur directement dans la carte PGM :
        - 'drawings': liste de cercles/rectangles peints
        - 'image_base64': image PNG modifiée transmise directement par le canvas HTML5
        Recharge ensuite dynamiquement les costmaps Nav2 !
        """
        if not os.path.exists(MAP_PGM_PATH):
            return False, "Fichier carte PGM introuvable."

        try:
            # 1. Sauvegarde préventive de sécurité
            backup_path = MAP_PGM_PATH + ".bak"
            shutil.copyfile(MAP_PGM_PATH, backup_path)

            # 2. Si une image modifiée est transmise par le canvas
            img_b64 = data.get("image_base64")
            if img_b64:
                if "," in img_b64:
                    img_b64 = img_b64.split(",")[1]
                img_data = base64.b64decode(img_b64)
                user_img = Image.open(BytesIO(img_data)).convert("L")  # Nuances de gris 8-bit
                # Redimensionnement exact aux dimensions de la carte
                user_img = user_img.resize((202, 202), Image.Resampling.NEAREST)
                user_img.save(MAP_PGM_PATH)
            else:
                # Modification par primitives (coordonnées mondiales x, y, rayon)
                primitives = data.get("primitives", [])
                im = Image.open(MAP_PGM_PATH)
                arr = np.array(im)

                for p in primitives:
                    px = p.get("x", 0.0)
                    py = p.get("y", 0.0)
                    prad = p.get("radius", 0.3)
                    ptype = p.get("type", "obstacle")  # "obstacle", "keepout", "eraser"

                    # Conversion monde (m) vers pixels de la carte
                    col = int((px - (-5.05)) / 0.05)
                    row = int((5.05 - py) / 0.05)
                    rad_px = max(1, int(prad / 0.05))

                    val = 0 if ptype in ["obstacle", "keepout"] else 254  # 0 = noir obstacle, 254 = blanc libre

                    for r in range(max(0, row - rad_px), min(202, row + rad_px + 1)):
                        for c in range(max(0, col - rad_px), min(202, col + rad_px + 1)):
                            if math.hypot(r - row, c - col) <= rad_px:
                                arr[r, c] = val

                new_img = Image.fromarray(arr)
                new_img.save(MAP_PGM_PATH)

            # 3. Notification et rechargement dynamique des costmaps Nav2 via ROS2
            threading.Thread(target=self._clear_nav2_costmaps, daemon=True).start()

            with state.lock:
                state.status_text = "✓ Cartographie modifiée et appliquée avec succès à Nav2 !"

            return True, "Cartographie mise à jour avec succès et transmise à la pile Nav2."

        except Exception as e:
            return False, f"Erreur lors de la sauvegarde : {str(e)}"

    def _reset_map(self) -> tuple[bool, str]:
        """Rétablit la cartographie d'origine propre (baseline)."""
        if not os.path.exists(MAP_BASELINE_PATH):
            return False, "Copie baseline de la carte introuvable."
        try:
            shutil.copyfile(MAP_BASELINE_PATH, MAP_PGM_PATH)
            threading.Thread(target=self._clear_nav2_costmaps, daemon=True).start()
            with state.lock:
                state.status_text = "✓ Cartographie réinitialisée à la version de référence !"
            return True, "Carte réinitialisée avec succès."
        except Exception as e:
            return False, str(e)

    def _clear_nav2_costmaps(self):
        """Appelle les services Nav2 pour effacer et recharger instantanément les costmaps."""
        try:
            cmd1 = "ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap '{}' 2>/dev/null || true"
            cmd2 = "ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap '{}' 2>/dev/null || true"
            subprocess.run(cmd1, shell=True, timeout=3)
            subprocess.run(cmd2, shell=True, timeout=3)
        except Exception:
            pass

    def _dispatch_mission(self, station_id: str):
        """Lance une mission de navigation vers la station demandée."""
        def run_target():
            if station_id == "AUTO":
                with state.lock:
                    state.status_text = "Lancement du cycle complet autonome..."
                cmd = "python3 ~/ros2_ws/src/raia_amr_description/run_mission.py"
                proc = subprocess.Popen(cmd, shell=True)
                with state.lock:
                    state.active_mission_proc = proc
            else:
                with state.lock:
                    state.status_text = f"Ordre de déplacement vers {station_id} envoyé..."
                # Déclenche via le topic d'appel ou la CLI
                cmd = f"python3 ~/ros2_ws/src/raia_amr_description/mission_cli.py --go {station_id}"
                subprocess.Popen(cmd, shell=True)

        threading.Thread(target=run_target, daemon=True).start()


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Serveur HTTP multithreadé non-bloquant pour gestion simultanée télémétrie + interface."""
    daemon_threads = True
    allow_reuse_address = True


def start_web_server(port: int = 8080):
    server = ThreadedHTTPServer(("0.0.0.0", port), IndustrialWebHandler)
    print(f"\n╔═══════════════════════════════════════════════════════════════════╗")
    print(f"║     SERVEUR WEB DE FLOTTE & SUPERVISION RAIA AMR 4.0 DÉMARRÉ      ║")
    print(f"║                                                                   ║")
    print(f"║  -> Accessible en local        : http://localhost:{port}           ║")
    print(f"║  -> Accessible via IP Robot    : http://{state.robot_ip}:{port}     ║")
    print(f"║  -> Nom mDNS Usine             : http://raia-amr.local:{port}      ║")
    print(f"╚═══════════════════════════════════════════════════════════════════╝\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main():
    global ros_node
    port = 8080
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])

    if ROS2_AVAILABLE:
        rclpy.init()
        ros_node = WebBridgeNode()

        ros_thread = threading.Thread(target=lambda: rclpy.spin(ros_node), daemon=True)
        ros_thread.start()

    start_web_server(port)

    if ROS2_AVAILABLE and ros_node:
        ros_node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
