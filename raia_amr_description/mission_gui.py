#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  INTERFACE GRAPHIQUE IHM DE MISSION & SUPERVISION — RAIA AMR
  Atelier Industriel 4.0 | factory_workshop.world
  IHM interactive avec vue 2D de l'atelier, télémesure temps réel et contrôle
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import time
import math
import threading
import tkinter as tk
from tkinter import ttk, messagebox

import rclpy
from rclpy.node import Node
from station_manager import StationManager, Station
from navigation_manager import NavigationManager, NavState


class MissionApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Supervision & Conduite de Missions AMR RAIA 4.0")
        self.root.geometry("1080x720")
        self.root.minsize(960, 640)

        # ── Gestionnaires ROS 2
        self.station_mgr = StationManager()
        self.nav_mgr: Optional[NavigationManager] = None
        self.ros_thread: Optional[threading.Thread] = None
        self.is_running = True

        self._build_ui()
        self._init_ros()

        # Rafraîchissement graphique périodique (10 Hz)
        self.root.after(100, self._ui_update_loop)

    def _init_ros(self):
        def ros_spin():
            rclpy.init()
            self.nav_mgr = NavigationManager("raia_mission_gui_node")
            while self.is_running and rclpy.ok():
                rclpy.spin_once(self.nav_mgr, timeout_sec=0.05)
            if self.nav_mgr:
                self.nav_mgr.destroy_node()
            rclpy.shutdown()

        self.ros_thread = threading.Thread(target=ros_spin, daemon=True)
        self.ros_thread.start()

    def _build_ui(self):
        # ── Style
        style = ttk.Style()
        style.theme_use("clam")

        # ── Header
        header = tk.Frame(self.root, bg="#1a252f", height=50)
        header.pack(fill=tk.X, side=tk.TOP)
        title_lbl = tk.Label(
            header,
            text="POSTE DE CONDUITE & SUPERVISION INDUSTRIELLE — AMR RAIA",
            fg="#ecf0f1", bg="#1a252f", font=("Arial", 14, "bold")
        )
        title_lbl.pack(pady=10)

        # ── Main Split (Left: Map 2D, Right: Controls & Telemetry)
        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#bdc3c7", sashwidth=4)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # ── Gauche : Carte 2D de l'atelier
        map_frame = tk.LabelFrame(main_pane, text="Cartographie Temps Réel de l'Atelier (10 × 10 m)", font=("Arial", 11, "bold"))
        main_pane.add(map_frame, minsize=520)

        self.canvas = tk.Canvas(map_frame, bg="#2c3e50", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        self.canvas.bind("<Configure>", lambda e: self._draw_factory_map())

        # ── Droite : Commandes et Données
        right_frame = tk.Frame(main_pane, bg="#f5f6fa")
        main_pane.add(right_frame, minsize=420)

        # Télémétrie en direct
        tele_frame = tk.LabelFrame(right_frame, text="Télémétrie & Localisation en Direct", font=("Arial", 10, "bold"))
        tele_frame.pack(fill=tk.X, padx=6, pady=4)

        self.lbl_pos = tk.Label(tele_frame, text="Pose : X = 0.00 m, Y = 0.00 m | Cap : 0.0°", font=("Consolas", 10), anchor="w")
        self.lbl_pos.pack(fill=tk.X, padx=8, pady=2)

        self.lbl_vel = tk.Label(tele_frame, text="Vitesse : Lin. = 0.00 m/s | Ang. = 0.00 rad/s", font=("Consolas", 10), anchor="w")
        self.lbl_vel.pack(fill=tk.X, padx=8, pady=2)

        self.lbl_state = tk.Label(tele_frame, text="État Mission : EN ATTENTE", font=("Arial", 10, "bold"), fg="#2980b9", anchor="w")
        self.lbl_state.pack(fill=tk.X, padx=8, pady=3)

        self.lbl_dist = tk.Label(tele_frame, text="Distance Restante : 0.00 m", font=("Consolas", 10), anchor="w")
        self.lbl_dist.pack(fill=tk.X, padx=8, pady=2)

        # Sélection de Mission
        mission_box = tk.LabelFrame(right_frame, text="Sélection de la Station Cible", font=("Arial", 10, "bold"))
        mission_box.pack(fill=tk.X, padx=6, pady=6)

        st_lbl = tk.Label(mission_box, text="Choisir une station industrielle :", font=("Arial", 9))
        st_lbl.pack(anchor="w", padx=8, pady=2)

        self.station_combo = ttk.Combobox(
            mission_box,
            values=[f"[{s.id}] {s.name}" for s in self.station_mgr.list_stations()],
            state="readonly",
            font=("Arial", 10)
        )
        self.station_combo.current(1)  # ST1 par défaut
        self.station_combo.pack(fill=tk.X, padx=8, pady=4)

        btn_row = tk.Frame(mission_box)
        btn_row.pack(fill=tk.X, padx=8, pady=6)

        self.btn_send = tk.Button(
            btn_row, text="Démarrer la Mission", bg="#27ae60", fg="white",
            font=("Arial", 10, "bold"), command=self._start_single_mission
        )
        self.btn_send.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.btn_cycle = tk.Button(
            btn_row, text="Cycle Complet CMS", bg="#2980b9", fg="white",
            font=("Arial", 10, "bold"), command=self._start_full_cycle
        )
        self.btn_cycle.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=2)

        # Arrêt d'urgence
        estop_frame = tk.Frame(right_frame)
        estop_frame.pack(fill=tk.X, padx=6, pady=4)
        self.btn_stop = tk.Button(
            estop_frame, text="ARRÊT D'URGENCE / STOP MISSION", bg="#c0392b", fg="white",
            font=("Arial", 11, "bold"), height=2, command=self._emergency_stop
        )
        self.btn_stop.pack(fill=tk.X)

        # Console de journalisation
        log_frame = tk.LabelFrame(right_frame, text="Journal des Événements & Sécurité", font=("Arial", 10, "bold"))
        log_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.log_text = tk.Text(log_frame, bg="#1e272e", fg="#d2dae2", font=("Consolas", 9), height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scroll = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scroll.set)

        self.log("Poste de supervision initialisé. Prêt pour les missions industrielles.")

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def _world_to_canvas(self, wx: float, wy: float, cw: int, ch: int):
        # Monde : x dans [-5, 5], y dans [-5, 5]
        # Canvas : x de 0 à cw, y inversé de 0 à ch
        margin = 30
        scale = min((cw - 2 * margin) / 10.0, (ch - 2 * margin) / 10.0)
        cx = cw / 2.0 + wx * scale
        cy = ch / 2.0 - wy * scale
        return cx, cy, scale

    def _draw_factory_map(self):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 50 or ch < 50:
            return

        self.canvas.delete("all")

        # ── Murs extérieurs (10x10 m)
        c1x, c1y, s = self._world_to_canvas(-4.9, 4.9, cw, ch)
        c2x, c2y, _ = self._world_to_canvas(4.9, -4.9, cw, ch)
        self.canvas.create_rectangle(c1x, c1y, c2x, c2y, outline="#7f8c8d", width=3, fill="#34495e")

        # ── Allée centrale de circulation
        a1x, a1y, _ = self._world_to_canvas(-4.8, 0.4, cw, ch)
        a2x, a2y, _ = self._world_to_canvas(4.8, -0.4, cw, ch)
        self.canvas.create_rectangle(a1x, a1y, a2x, a2y, fill="#2c3e50", outline="#f39c12", width=1, dash=(4, 4))

        # ── Bâtis des machines
        machines = [
            ("Ligne MPM (Sérigraphie)", 2.8, 2.2, 1.5, 1.25, "#8e44ad"),
            ("Testeur IA SPEA", -2.8, 2.2, 1.4, 1.25, "#16a085"),
            ("Four Refusion ICT", 2.8, -2.2, 1.8, 1.2, "#d35400"),
            ("Zone Palettes PCB", -2.8, -2.2, 1.4, 1.2, "#7f8c8d"),
            ("Quai Convoyeur", 4.3, 0.0, 0.8, 1.8, "#2980b9"),
        ]
        for name, mx, my, bw, bh, color in machines:
            x1, y1, _ = self._world_to_canvas(mx - bw / 2.0, my + bh / 2.0, cw, ch)
            x2, y2, _ = self._world_to_canvas(mx + bw / 2.0, my - bh / 2.0, cw, ch)
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#ecf0f1", width=1)
            self.canvas.create_text((x1 + x2) / 2.0, (y1 + y2) / 2.0, text=name, fill="white", font=("Arial", 8, "bold"))

        # ── Stations de docking (ST0 .. ST5)
        for st in self.station_mgr.list_stations():
            sx, sy, _ = self._world_to_canvas(st.x, st.y, cw, ch)
            self.canvas.create_oval(sx - 7, sy - 7, sx + 7, sy + 7, fill="#2ecc71", outline="#ffffff", width=2)
            self.canvas.create_text(sx, sy - 12, text=st.id, fill="#2ecc71", font=("Arial", 9, "bold"))

        # ── Position du Robot AMR
        rx, ry = 0.0, 0.0
        ryaw = 0.0
        if self.nav_mgr and self.nav_mgr.has_pose:
            rx, ry = self.nav_mgr.current_x, self.nav_mgr.current_y
            ryaw = self.nav_mgr.current_yaw

        rcx, rcy, scale = self._world_to_canvas(rx, ry, cw, ch)
        rw = 0.56 * scale
        rh = 0.32 * scale

        # Dessin du corps du robot orienté
        cos_t = math.cos(ryaw)
        sin_t = math.sin(ryaw)
        corners = [
            (+rw / 2, +rh / 2),
            (-rw / 2, +rh / 2),
            (-rw / 2, -rh / 2),
            (+rw / 2, -rh / 2),
        ]
        poly = []
        for dx, dy in corners:
            px = rcx + dx * cos_t + dy * sin_t
            py = rcy - (dx * sin_t - dy * cos_t)
            poly.extend([px, py])

        self.canvas.create_polygon(poly, fill="#3498db", outline="#f1c40f", width=2)
        # Pointeur de cap
        hx = rcx + (rw / 2 + 10) * cos_t
        hy = rcy - (rw / 2 + 10) * sin_t
        self.canvas.create_line(rcx, rcy, hx, hy, fill="#e74c3c", width=3, arrow=tk.LAST)

    def _ui_update_loop(self):
        if not self.is_running:
            return

        if self.nav_mgr:
            self.nav_mgr.update_robot_pose()
            rx = self.nav_mgr.current_x
            ry = self.nav_mgr.current_y
            yaw = self.nav_mgr.current_yaw
            lin = self.nav_mgr.current_lin_vel
            ang = self.nav_mgr.current_ang_vel
            dist = self.nav_mgr.distance_remaining
            state_val = self.nav_mgr.state.value

            self.lbl_pos.config(text=f"Pose : X = {rx:5.2f} m, Y = {ry:5.2f} m | Cap = {math.degrees(yaw):5.1f}°")
            self.lbl_vel.config(text=f"Vitesse : Lin. = {lin:4.2f} m/s | Ang. = {ang:4.2f} rad/s")
            self.lbl_state.config(text=f"État Mission : {state_val}")
            self.lbl_dist.config(text=f"Distance Restante : {dist:4.2f} m")

            self._draw_factory_map()

        self.root.after(100, self._ui_update_loop)

    def _start_single_mission(self):
        sel = self.station_combo.get()
        if not sel:
            return
        st_id = sel.split("]")[0].replace("[", "").strip()

        def run_thread():
            self.btn_send.config(state=tk.DISABLED)
            self.log(f"Lancement mission unitaire vers {st_id}...")
            ok = self.nav_mgr.navigate_to_station(st_id, dwell_time_sec=2.0)
            if ok:
                self.log(f"Mission {st_id} accomplie avec SUCCÈS.")
            else:
                self.log(f"ÉCHEC de la mission vers {st_id}.")
            self.btn_send.config(state=tk.NORMAL)

        threading.Thread(target=run_thread, daemon=True).start()

    def _start_full_cycle(self):
        route = ["ST0", "ST1", "ST3", "ST4", "ST0"]

        def run_thread():
            self.btn_cycle.config(state=tk.DISABLED)
            self.log(f"Lancement du Cycle Complet CMS : {' -> '.join(route)}")
            res = self.nav_mgr.execute_multi_station_route(route, dwell_time_per_station=2.5)
            if res["success"]:
                self.log("Cycle Industriel Complet 100% VALIDÉ !")
            else:
                self.log(f"Interruption du cycle à {res['failed']}.")
            self.btn_cycle.config(state=tk.NORMAL)

        threading.Thread(target=run_thread, daemon=True).start()

    def _emergency_stop(self):
        self.log("ARRÊT D'URGENCE DÉCLENCHÉ !")
        if self.nav_mgr:
            self.nav_mgr.cancel_active_goal()


def main():
    root = tk.Tk()
    app = MissionApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (setattr(app, 'is_running', False), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()
