#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
#  DÉMONSTRATION COMPLÈTE 100% AUTOMATIQUE — RAIA AMR (Projet 01.26)
#  Lance Gazebo + RViz2 + Nav2 puis exécute la navigation inter-lignes
#  Usage : bash start_all_and_navigate.sh
# ═══════════════════════════════════════════════════════════════════

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      RAIA AMR — DÉMONSTRATION AUTOMATIQUE COMPLÈTE NAV2          ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════╝${NC}"

# 1. Nettoyage préventif complet (tous processus ROS2 et Gazebo)
echo -e "\n${YELLOW}[1/4] Nettoyage des processus antérieurs...${NC}"
pkill -9 -f 'controller_server|planner_server|behavior_server|bt_navigator|lifecycle_manager|map_server|amcl|smoother_server|velocity_smoother|waypoint_follower|gzserver|gzclient|robot_state_publisher|rviz2' 2>/dev/null || true
killall -9 gzserver gzclient robot_state_publisher component_container_isolated component_container rviz2 python3 2>/dev/null || true
rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* 2>/dev/null || true
sleep 1
echo -e "${GREEN}    ✓ Environnement prêt${NC}"

# 2. Variables d'environnement WSLg & ROS (Accélération matérielle GPU D3D12 active pour FPS maximal)
export MESA_D3D12_DEFAULT_ADAPTER_NAME=Intel
export GAZEBO_MODEL_DATABASE_URI=""
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
cd ~/ros2_ws
colcon build --symlink-install --packages-select raia_amr_description > /dev/null 2>&1 || true
source ~/ros2_ws/install/setup.bash
cd ~/ros2_ws/src/raia_amr_description

# 3. Lancement de la simulation + Nav2
echo -e "\n${YELLOW}[2/4] Démarrage de Gazebo, RViz2 et de la pile Nav2...${NC}"
MAP_PATH="${1:-$HOME/ros2_ws/src/raia_amr_description/maps/raia_factory_map.yaml}"
LOG_FILE="/tmp/nav2_launch.log"
rm -f "$LOG_FILE"

ros2 launch raia_amr_description nav2.launch.py map:="$MAP_PATH" > "$LOG_FILE" 2>&1 &
LAUNCH_PID=$!

cleanup() {
    echo -e "\n${YELLOW}Fermeture de la simulation et arrêt des nœuds...${NC}"
    kill -9 $LAUNCH_PID $WORKER_PID 2>/dev/null || true
    killall -9 gzserver gzclient robot_state_publisher component_container_isolated component_container rviz2 python3 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

# 4. Attente de l'activation complète des nœuds Nav2 (Localization ET Navigation)
echo -e "${YELLOW}[3/4] Initialisation des nœuds Nav2 et de la carte...${NC}"
READY_LOC=0
READY_NAV=0
for i in {1..70}; do
    if [ $READY_LOC -eq 0 ] && grep -q "lifecycle_manager_localization.*Managed nodes are active" "$LOG_FILE" 2>/dev/null; then
        READY_LOC=1
    fi
    if [ $READY_NAV -eq 0 ] && grep -q "lifecycle_manager_navigation.*Managed nodes are active" "$LOG_FILE" 2>/dev/null; then
        READY_NAV=1
    fi
    if [ $READY_LOC -eq 1 ] && [ $READY_NAV -eq 1 ]; then
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

if [ $READY_LOC -eq 1 ] && [ $READY_NAV -eq 1 ]; then
    echo -e "${GREEN}    ✓ Tous les nœuds Nav2 (Localization + Navigation) sont ACTIFS et la carte est chargée !${NC}"
    echo -e "${GREEN}    ✓ Gazebo et RViz2 sont ouverts à l'écran.${NC}"
else
    echo -e "${RED}    ✗ Délai d'attente dépassé pour l'initialisation de Nav2.${NC}"
    tail -n 25 "$LOG_FILE"
    cleanup
fi

# Pause de stabilisation de la physique Gazebo et amorçage du filtre AMCL
sleep 6

# 5. Démarrage de l'animateur piéton d'atelier (Obstacle mobile)
python3 ~/ros2_ws/src/raia_amr_description/worker_patrol.py > /dev/null 2>&1 &
WORKER_PID=$!
sleep 1

# 6. Déclenchement automatique de la mission
echo -e "\n${YELLOW}[4/4] Lancement automatique de la mission inter-lignes...${NC}"
python3 -u ~/ros2_ws/src/raia_amr_description/run_mission.py

echo -e "\n${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN} [SUCCÈS] Mission inter-lignes terminée avec succès !${NC}"
echo -e "${YELLOW} Gazebo et RViz2 restent ouverts à l'écran pour observation.${NC}"
echo -e "${YELLOW} Vous pouvez continuer à tester des déplacements via RViz2 ('Nav2 Goal').${NC}"
echo -e "${YELLOW} Appuyez sur Ctrl+C dans ce terminal lorsque vous souhaitez tout quitter.${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"

wait $LAUNCH_PID
