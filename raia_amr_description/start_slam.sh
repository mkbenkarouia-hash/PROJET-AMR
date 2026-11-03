#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
#  SCRIPT DE DÉMARRAGE RAPIDE — SLAM CARTOGRAPHIE
#  Projet RAIA 01.26 | raia_amr_description
#  Usage : bash start_slam.sh
# ═══════════════════════════════════════════════════════════════════

set -e  # Arrêt immédiat si une commande échoue

# ── Couleurs terminal ────────────────────────────────────────────
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║    RAIA AMR — Jalon 2 : Cartographie SLAM            ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════╝${NC}"

# ── 1. Variables d'environnement WSLg ────
echo -e "\n${YELLOW}[1/4] Configuration environnement WSLg...${NC}"
export MESA_D3D12_DEFAULT_ADAPTER_NAME=Intel
export GAZEBO_MODEL_DATABASE_URI=""
echo -e "${GREEN}    ✓ Accélération matérielle GPU D3D12 activée${NC}"
echo -e "${GREEN}    ✓ GAZEBO_MODEL_DATABASE_URI vide (cache local)${NC}"

# ── 2. Source ROS2 + workspace ───────────────────────────────────
echo -e "\n${YELLOW}[2/4] Sourcing ROS2 Humble + workspace...${NC}"
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
echo -e "${GREEN}    ✓ ROS2 Humble sourcé${NC}"
echo -e "${GREEN}    ✓ Workspace ~/ros2_ws sourcé${NC}"

# ── 3. Vérification du package ──────────────────────────────────
echo -e "\n${YELLOW}[3/4] Vérification du package raia_amr_description...${NC}"
if ros2 pkg list 2>/dev/null | grep -q raia_amr_description; then
    echo -e "${GREEN}    ✓ Package raia_amr_description trouvé${NC}"
else
    echo -e "${RED}    ✗ Package introuvable — recompilation...${NC}"
    cd ~/ros2_ws
    colcon build --symlink-install --packages-select raia_amr_description
    source ~/ros2_ws/install/setup.bash
fi

# ── 4. Lancement SLAM ───────────────────────────────────────────
echo -e "\n${YELLOW}[4/4] Lancement Gazebo + SLAM Toolbox + RViz2...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  → Ouvrez un SECOND terminal et lancez :${NC}"
echo -e "${GREEN}     ros2 run teleop_twist_keyboard teleop_twist_keyboard${NC}"
echo -e "${YELLOW}  → Pilotez le robot dans toute l'usine (i=avant, ,=arrière, j/l=rotation, k=stop)${NC}"
echo -e "${YELLOW}  → Quand la carte est complète, ouvrez un 3ème terminal :${NC}"
echo -e "${GREEN}     ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/src/raia_amr_description/maps/raia_factory_map${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}  Appuyez sur Entrée pour démarrer...${NC}"
read

ros2 launch raia_amr_description slam.launch.py
