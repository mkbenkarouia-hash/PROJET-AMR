#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════════════
  MODULE GESTIONNAIRE DE STATIONS DE PRODUCTION — RAIA AMR
  Atelier Industriel 4.0 | factory_workshop.world
  Charge et expose la cartographie sémantique des stations de l'atelier
═══════════════════════════════════════════════════════════════════════════════
"""

import os
import math
import yaml
from typing import Dict, List, Optional, Tuple


class Station:
    """Représente une station industrielle de l'atelier."""
    def __init__(self, key: str, data: dict):
        self.key: str = key
        self.id: str = data.get("id", "").strip().upper()
        self.name: str = data.get("name", "").strip()
        self.description: str = data.get("description", "").strip()
        self.x: float = float(data.get("x", 0.0))
        self.y: float = float(data.get("y", 0.0))
        self.theta: float = float(data.get("theta", 0.0))  # radians

    @property
    def theta_deg(self) -> float:
        """Cap en degrés [-180, 180]."""
        return math.degrees(self.theta)

    def distance_to(self, x: float, y: float) -> float:
        """Calcule la distance euclidienne par rapport à un point (x, y)."""
        return math.hypot(self.x - x, self.y - y)

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "x": self.x,
            "y": self.y,
            "theta_rad": self.theta,
            "theta_deg": round(self.theta_deg, 1)
        }

    def __repr__(self) -> str:
        return f"<Station [{self.id}] '{self.name}' at ({self.x:.2f}, {self.y:.2f}, {self.theta_deg:.1f}°)>"


class StationManager:
    """
    Gestionnaire centralisé des stations de production.
    Charge la configuration depuis stations.yaml et fournit des méthodes d'accès flexibles.
    """

    def __init__(self, config_path: Optional[str] = None):
        self.frame_id: str = "map"
        self._stations: Dict[str, Station] = {}
        self._id_index: Dict[str, Station] = {}

        if config_path is None:
            # Recherche relative automatique
            base_dir = os.path.dirname(os.path.abspath(__file__))
            candidates = [
                os.path.join(base_dir, "config", "stations.yaml"),
                os.path.join(base_dir, "stations.yaml"),
                "/home/khalilvr/ros2_ws/src/raia_amr_description/config/stations.yaml",
                "/home/khalilvr/ros2_ws/install/raia_amr_description/share/raia_amr_description/config/stations.yaml",
            ]
            for c in candidates:
                if os.path.exists(c):
                    config_path = c
                    break

        if config_path and os.path.exists(config_path):
            self.load_from_yaml(config_path)
        else:
            raise FileNotFoundError(f"Fichier de configuration des stations introuvable: {config_path}")

    def load_from_yaml(self, path: str):
        """Parse le fichier stations.yaml."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        self.frame_id = data.get("frame_id", "map")
        raw_stations = data.get("stations", {})

        self._stations.clear()
        self._id_index.clear()

        for key, info in raw_stations.items():
            station = Station(key, info)
            self._stations[key] = station
            if station.id:
                self._id_index[station.id] = station

    def list_stations(self) -> List[Station]:
        """Retourne la liste ordonnée de toutes les stations."""
        return sorted(list(self._stations.values()), key=lambda s: s.id)

    def get_station(self, identifier: str) -> Optional[Station]:
        """
        Recherche une station par ID (ex: 'ST1'), clé (ex: 'station_serigraphie')
        ou nom partiel insensible à la casse.
        """
        if not identifier:
            return None
        
        ident_clean = str(identifier).strip()
        ident_upper = ident_clean.upper()

        # Alias industriels
        aliases = {
            "ST_DOCK": "ST0",
            "DOCK": "ST0",
            "RECHARGE": "ST0",
            "BASE": "ST0",
            "SERIGRAPHIE": "ST1",
            "MPM": "ST1",
            "PRISE_PCB": "ST1",
            "CONVOYEUR": "ST2",
            "DEPOSE_PCB": "ST2",
            "SPEA": "ST2"
        }
        if ident_upper in aliases:
            ident_upper = aliases[ident_upper]

        # 1. Recherche par ID exact (ex: ST0, ST1, ...)
        if ident_upper in self._id_index:
            return self._id_index[ident_upper]

        # 2. Recherche par clé exacte
        if ident_clean in self._stations:
            return self._stations[ident_clean]

        # 3. Recherche par nom partiel
        ident_lower = ident_clean.lower()
        for s in self._stations.values():
            if ident_lower in s.name.lower() or ident_lower in s.key.lower():
                return s

        return None

    def get_pose(self, identifier: str) -> Optional[Tuple[float, float, float]]:
        """Retourne (x, y, theta) de la station identifiée, ou None."""
        s = self.get_station(identifier)
        if s:
            return (s.x, s.y, s.theta)
        return None

    def get_nearest_station(self, x: float, y: float) -> Tuple[Optional[Station], float]:
        """Retourne (station_la_plus_proche, distance_en_metres)."""
        if not self._stations:
            return (None, float("inf"))

        nearest = min(self._stations.values(), key=lambda s: s.distance_to(x, y))
        dist = nearest.distance_to(x, y)
        return (nearest, dist)

    def validate_station(self, identifier: str) -> Tuple[bool, str]:
        """Vérifie si une station existe et est accessible."""
        s = self.get_station(identifier)
        if s is None:
            return False, f"Station inconnue : '{identifier}'"
        return True, f"Station valide : [{s.id}] {s.name} ({s.x:.2f}, {s.y:.2f})"

    def print_overview(self):
        """Affiche un tableau récapitulatif des stations disponibles."""
        print("┌──────┬────────────────────────────────────────────┬─────────┬─────────┬──────────┐")
        print("│ ID   │ Nom de la station                         │ X (m)   │ Y (m)   │ Cap (°)  │")
        print("├──────┼────────────────────────────────────────────┼─────────┼─────────┼──────────┤")
        for s in self.list_stations():
            print(f"│ {s.id:<4} │ {s.name:<42} │ {s.x:7.2f} │ {s.y:7.2f} │ {s.theta_deg:8.1f} │")
        print("└──────┴────────────────────────────────────────────┴─────────┴─────────┴──────────┘")


if __name__ == "__main__":
    mgr = StationManager()
    print("\n[STATION MANAGER] Initialisation réussie. Liste des stations détectées :")
    mgr.print_overview()
