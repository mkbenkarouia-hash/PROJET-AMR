#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
#  SCRIPT DE DÉMARRAGE RAPIDE — NAVIGATION AUTONOME Nav2
#  Projet RAIA 01.26 | raia_amr_description
#  Usage : bash start_nav2.sh [chemin_carte.yaml]
#  Exemple : bash start_nav2.sh ~/ros2_ws/src/raia_amr_description/maps/raia_factory_map.yaml
# ═══════════════════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    RAIA AMR — Jalon 2 : Navigation Autonome Nav2     ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"

# ── Chemin carte (argument ou défaut) ───────────────────────────
MAP_PATH="${1:-$HOME/ros2_ws/src/raia_amr_description/maps/raia_factory_map.yaml}"

# ── 1. Variables d'environnement WSLg & Nettoyage ────────────────
echo -e "\n${YELLOW}[1/5] Nettoyage et configuration environnement WSLg...${NC}"
killall -9 gzserver gzclient robot_state_publisher component_container_isolated component_container rviz2 python3 2>/dev/null || true
rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* 2>/dev/null || true
export MESA_D3D12_DEFAULT_ADAPTER_NAME=Intel
export GAZEBO_MODEL_DATABASE_URI=""
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/fastdds_udp_only.xml
echo -e "${GREEN}    ✓ Processus orphelins nettoyés${NC}"
echo -e "${GREEN}    ✓ Accélération matérielle GPU D3D12 activée${NC}"

# ── 2. Source ROS2 + workspace ──────────────────────────────────
echo -e "\n${YELLOW}[2/5] Sourcing ROS2 Humble + workspace...${NC}"
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
echo -e "${GREEN}    ✓ ROS2 Humble + workspace sourcés${NC}"

# ── 3. Vérification de la carte ─────────────────────────────────
echo -e "\n${YELLOW}[3/5] Vérification de la carte OGM...${NC}"
if [ -f "$MAP_PATH" ]; then
    echo -e "${GREEN}    ✓ Carte trouvée : $MAP_PATH${NC}"
else
    echo -e "${RED}    ✗ Carte introuvable : $MAP_PATH${NC}"
    echo -e "${RED}    → Lancez d'abord start_slam.sh pour générer la carte !${NC}"
    exit 1
fi

# ── 4. Synchronisation + compilation du package ─────────────────
echo -e "\n${YELLOW}[4/5] Synchronisation et compilation du package...${NC}"
PKG_SRC=~/ros2_ws/src/raia_amr_description

# Chemin correct WSL2 vers le bureau Windows
WIN_PKG="/mnt/c/Users/khalil/Desktop/STUDY/Bizerte/2eme/PROJET HMIDA/raia_amr_description"

# Copier les fichiers modifiés vers le workspace ROS2
if [ -d "$PKG_SRC" ] && [ -d "$WIN_PKG" ]; then
    cp -rf "$WIN_PKG/config/"*    "$PKG_SRC/config/"    2>/dev/null || true
    cp -rf "$WIN_PKG/maps/"*      "$PKG_SRC/maps/"      2>/dev/null || true
    cp -rf "$WIN_PKG/launch/"*    "$PKG_SRC/launch/"    2>/dev/null || true
    cp -rf "$WIN_PKG/urdf/"*      "$PKG_SRC/urdf/"      2>/dev/null || true
    echo -e "${GREEN}    ✓ Fichiers synchronisés depuis le bureau Windows${NC}"
else
    echo -e "${YELLOW}    ⚠ Sync ignorée (dossier Windows non trouvé)${NC}"
fi

# Recompiler le package
cd ~/ros2_ws
colcon build --symlink-install --packages-select raia_amr_description 2>&1 | tail -5
source ~/ros2_ws/install/setup.bash
echo -e "${GREEN}    ✓ Package raia_amr_description compilé et prêt${NC}"

# ── 5. Instructions de navigation ───────────────────────────────
echo -e "\n${YELLOW}[5/5] Démarrage de la navigation autonome...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  La pile Nav2 démarre avec localisation automatique (AMCL à (0,0)).${NC}"
echo -e "${GREEN}  Option A (Mission automatique) :${NC}"
echo -e "    Ouvrir un 2ème terminal WSL et lancer la mission inter-lignes :"
echo -e "    ${BLUE}python3 run_mission.py${NC}  (ou python3 scratch/test_navigation_mission.py)"
echo -e "${GREEN}  Option B (Navigation interactive RViz2) :${NC}"
echo -e "    Cliquer sur l'outil 'Nav2 Goal' dans la barre RViz2 et cliquer sur la carte."
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}  Carte utilisée : ${GREEN}$MAP_PATH${NC}"
echo -e "${YELLOW}  Appuyez sur Entrée pour démarrer...${NC}"
read

ros2 launch raia_amr_description nav2.launch.py map:="$MAP_PATH"
