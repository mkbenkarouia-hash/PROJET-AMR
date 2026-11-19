#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
#  CARTOGRAPHIE SLAM MANUELLE TOUT-EN-UN — RAIA AMR (Projet 01.26)
#  Lance Gazebo, RViz2, SLAM Toolbox ET le pilotage manuel interactif
#  avec raccourci 'M' pour sauvegarder la carte en un clic !
#  Usage : bash start_manual_mapping.sh
# ═══════════════════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      RAIA AMR — CARTOGRAPHIE SLAM & TÉLÉOPÉRATION MANUELLE        ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════╝${NC}"

# 1. Nettoyage préventif
echo -e "\n${YELLOW}[1/4] Nettoyage des processus antérieurs...${NC}"
pkill -9 -f 'controller_server|planner_server|behavior_server|bt_navigator|lifecycle_manager|map_server|amcl|smoother_server|velocity_smoother|waypoint_follower|gzserver|gzclient|robot_state_publisher|rviz2|async_slam_toolbox_node|manual_teleop' 2>/dev/null || true
killall -9 gzserver gzclient robot_state_publisher component_container_isolated component_container rviz2 python3 2>/dev/null || true
rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* 2>/dev/null || true
sleep 1
echo -e "${GREEN}    ✓ Environnement prêt${NC}"

# 2. Variables d'environnement WSLg & ROS
export MESA_D3D12_DEFAULT_ADAPTER_NAME=Intel
export GAZEBO_MODEL_DATABASE_URI=""
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
colcon build --symlink-install --packages-select raia_amr_description > /dev/null 2>&1 || true
source ~/ros2_ws/install/setup.bash
cd ~/ros2_ws/src/raia_amr_description

# 3. Démarrage de Gazebo + SLAM Toolbox + RViz2 en arrière-plan
echo -e "\n${YELLOW}[2/4] Démarrage de Gazebo, RViz2 et SLAM Toolbox...${NC}"
LOG_FILE="/tmp/slam_launch.log"
rm -f "$LOG_FILE"

ros2 launch raia_amr_description slam.launch.py > "$LOG_FILE" 2>&1 &
SLAM_PID=$!

cleanup() {
    echo -e "\n${YELLOW}Fermeture de Gazebo, RViz2 et SLAM Toolbox...${NC}"
    kill -9 $SLAM_PID 2>/dev/null || true
    killall -9 gzserver gzclient robot_state_publisher component_container_isolated component_container rviz2 python3 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# 4. Attente de l'initialisation de SLAM Toolbox
echo -e "${YELLOW}[3/4] Initialisation du moteur SLAM Toolbox et de Gazebo...${NC}"
READY=0
for i in {1..45}; do
    if grep -q "Registering sensor: [laser]" "$LOG_FILE" 2>/dev/null || grep -q "async_slam_toolbox_node" "$LOG_FILE" 2>/dev/null; then
        READY=1
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

if [ $READY -eq 1 ]; then
    echo -e "${GREEN}    ✓ Gazebo, RViz2 et SLAM Toolbox sont ACTIFS !${NC}"
else
    echo -e "${YELLOW}    ⚠ SLAM Toolbox démarre en arrière-plan...${NC}"
fi

sleep 4

# 5. Lancement de la téléopération interactive dans le terminal courant
echo -e "\n${YELLOW}[4/4] Ouverture du panneau de pilotage manuel...${NC}"
echo -e "${BLUE}  Pilotez le robot dans l'atelier pour construire la carte.${NC}"
echo -e "${BLUE}  Appuyez sur 'M' à tout moment pour sauvegarder la carte !${NC}\n"

python3 ~/ros2_ws/src/raia_amr_description/manual_teleop.py

echo -e "\n${GREEN}Session de cartographie terminée.${NC}"
