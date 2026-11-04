#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
#  ENREGISTREMENT VIDÉO COMPLET ET EXÉCUTION NAV2 — RAIA AMR
#  Atelier Industriel 4.0 | factory_workshop.world
#  - Enregistre l'écran (Gazebo + RViz2) en HD MP4 dans 'simulations/'
#  - Valide l'évitement du chariot fixe (ST1 -> ST2)
#  - Valide la détection du piéton mobile, l'arrêt et l'alerte sonore
#  Usage : bash record_and_run_simulation.sh
# ═══════════════════════════════════════════════════════════════════

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      RAIA AMR — ENREGISTREMENT VIDÉO COMPLET DE LA MISSION        ║${NC}"
echo -e "${BLUE}║          Atelier CMS 4.0 | Obstacles Fixe & Mobile + Son          ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════╝${NC}"

# 1. Dossier de destination des enregistrements
SCRIPT_DIR="$(cd -P "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SIM_DIR="$SCRIPT_DIR/../simulations"
mkdir -p "$SIM_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_VIDEO="$SIM_DIR/raia_amr_simulation_${TIMESTAMP}.mp4"
LATEST_VIDEO="$SIM_DIR/raia_amr_simulation.mp4"

# 2. Nettoyage préventif des processus
echo -e "\n${YELLOW}[1/5] Nettoyage des processus antérieurs...${NC}"
pkill -9 -f 'ffmpeg.*x11grab' 2>/dev/null || true
pkill -9 -f 'controller_server|planner_server|behavior_server|bt_navigator|lifecycle_manager|map_server|amcl|smoother_server|velocity_smoother|waypoint_follower|gzserver|gzclient|robot_state_publisher|rviz2' 2>/dev/null || true
killall -9 gzserver gzclient robot_state_publisher component_container_isolated component_container rviz2 python3 2>/dev/null || true
rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* 2>/dev/null || true
sleep 1
echo -e "${GREEN}    ✓ Environnement propre${NC}"

# 3. Variables d'environnement
export MESA_D3D12_DEFAULT_ADAPTER_NAME=Intel
export GAZEBO_MODEL_DATABASE_URI=""
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/fastdds_udp_only.xml
export DISPLAY=:0
export PULSE_SERVER=/mnt/wslg/PulseServer

source /opt/ros/humble/setup.bash
cd ~/ros2_ws
colcon build --symlink-install --packages-select raia_amr_description > /dev/null 2>&1 || true
source ~/ros2_ws/install/setup.bash
cd ~/ros2_ws/src/raia_amr_description

# 4. Lancement de l'enregistreur vidéo ffmpeg en arrière-plan
echo -e "\n${YELLOW}[2/5] Démarrage de l'enregistreur vidéo (ffmpeg x11grab :0)...${NC}"
echo -e "${CYAN}    Fichier cible : $OUTPUT_VIDEO${NC}"

FFMPEG_LOG="/tmp/ffmpeg_record.log"
ffmpeg -y -nostdin -loglevel warning \
  -f x11grab -draw_mouse 1 -video_size 1366x768 -i :0 \
  -c:v libx264 -preset ultrafast -pix_fmt yuv420p \
  "$OUTPUT_VIDEO" > "$FFMPEG_LOG" 2>&1 &
FFMPEG_PID=$!
sleep 1

if ! kill -0 $FFMPEG_PID 2>/dev/null; then
    echo -e "${RED}    ✗ Erreur lors du lancement de ffmpeg :${NC}"
    cat "$FFMPEG_LOG"
    exit 1
fi
echo -e "${GREEN}    ✓ Enregistrement vidéo en cours (PID $FFMPEG_PID)...${NC}"

cleanup() {
    echo -e "\n${YELLOW}Arrêt de l'enregistrement et clôture de la vidéo...${NC}"
    if kill -0 $FFMPEG_PID 2>/dev/null; then
        kill -2 $FFMPEG_PID 2>/dev/null || true
        wait $FFMPEG_PID 2>/dev/null || true
    fi
    kill -9 $LAUNCH_PID $WORKER_PID 2>/dev/null || true
    killall -9 gzserver gzclient robot_state_publisher component_container_isolated component_container rviz2 python3 2>/dev/null || true

    if [ -f "$OUTPUT_VIDEO" ]; then
        cp -f "$OUTPUT_VIDEO" "$LATEST_VIDEO" 2>/dev/null || true
        FILE_SIZE=$(du -h "$OUTPUT_VIDEO" | cut -f1)
        echo -e "\n${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN} ✓ VIDÉO ENREGISTRÉE AVEC SUCCÈS !${NC}"
        echo -e "${GREEN}   Fichier : $OUTPUT_VIDEO ($FILE_SIZE)${NC}"
        echo -e "${GREEN}   Lien principal : $LATEST_VIDEO${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
    fi
    exit 0
}
trap cleanup SIGINT SIGTERM

# 5. Lancement Gazebo + RViz2 + Nav2
echo -e "\n${YELLOW}[3/5] Démarrage de Gazebo, RViz2 et de la pile Nav2...${NC}"
MAP_PATH="${1:-$HOME/ros2_ws/src/raia_amr_description/maps/raia_factory_map.yaml}"
LOG_FILE="/tmp/nav2_launch.log"
rm -f "$LOG_FILE"

ros2 launch raia_amr_description nav2.launch.py map:="$MAP_PATH" > "$LOG_FILE" 2>&1 &
LAUNCH_PID=$!

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
    echo -e "${GREEN}    ✓ Nœuds Nav2 actifs et carte chargée.${NC}"
else
    echo -e "${RED}    ✗ Délai d'attente Nav2 dépassé.${NC}"
    cleanup
fi

sleep 6

# 6. Démarrage de l'obstacle mobile (Traversée piéton)
echo -e "\n${YELLOW}[4/5] Démarrage du contrôleur de traversée piéton (worker_patrol)...${NC}"
python3 ~/ros2_ws/src/raia_amr_description/worker_patrol.py > /dev/null 2>&1 &
WORKER_PID=$!
sleep 1
echo -e "${GREEN}    ✓ Obstacle mobile armé et positionné en attente de l'AMR${NC}"

# 7. Exécution de la mission complète
echo -e "\n${YELLOW}[5/5] Exécution de la mission industrielle complète...${NC}"
python3 -u ~/ros2_ws/src/raia_amr_description/run_mission.py || true

# Petite temporisation pour filmer l'amarrage final à la borne MiR Charge
sleep 4

echo -e "\n${GREEN}Mission terminée ! Finalisation du fichier vidéo...${NC}"
cleanup
