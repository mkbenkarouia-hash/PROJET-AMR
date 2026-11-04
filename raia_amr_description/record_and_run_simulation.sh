#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
#  ENREGISTREMENT VIDÉO COMPLET ET EXÉCUTION NAV2 — RAIA AMR
#  Atelier Industriel 4.0 | factory_workshop.world
#  Capture 100% visuelle du monde Gazebo 3D sans écran noir via Xvfb
#  - Enregistre la simulation Gazebo en HD MP4 dans 'simulations/'
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

# 2. Nettoyage préventif des processus et verrous d'affichage
echo -e "\n${YELLOW}[1/5] Nettoyage des processus antérieurs et verrous d'affichage...${NC}"
pkill -9 -f 'ffmpeg.*x11grab' 2>/dev/null || true
pkill -9 -f 'Xvfb :99|openbox' 2>/dev/null || true
pkill -9 -f 'controller_server|planner_server|behavior_server|bt_navigator|lifecycle_manager|map_server|amcl|smoother_server|velocity_smoother|waypoint_follower|gzserver|gzclient|robot_state_publisher|rviz2' 2>/dev/null || true
killall -9 gzserver gzclient robot_state_publisher component_container_isolated component_container rviz2 python3 Xvfb openbox 2>/dev/null || true
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* 2>/dev/null || true
sleep 1
echo -e "${GREEN}    ✓ Environnement propre${NC}"

# 3. Démarrage du serveur graphique virtuel Xvfb dédié à l'enregistrement vidéo réel (Résout l'écran noir de WSLg)
echo -e "\n${YELLOW}[2/5] Initialisation du framebuffer virtuel Xvfb (1366x768 24-bit RGB)...${NC}"
Xvfb :99 -screen 0 1366x768x24 -ac +extension GLX +render -noreset > /dev/null 2>&1 &
XVFB_PID=$!
sleep 1

export DISPLAY=:99
openbox > /dev/null 2>&1 &
OPENBOX_PID=$!
sleep 1

# Variables d'environnement de simulation et audio
export MESA_D3D12_DEFAULT_ADAPTER_NAME=Intel
export GAZEBO_MODEL_DATABASE_URI=""
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/fastdds_udp_only.xml
export PULSE_SERVER=/mnt/wslg/PulseServer

source /opt/ros/humble/setup.bash
cd ~/ros2_ws
colcon build --symlink-install --packages-select raia_amr_description > /dev/null 2>&1 || true
source ~/ros2_ws/install/setup.bash
cd ~/ros2_ws/src/raia_amr_description

# 4. Lancement de l'enregistreur vidéo ffmpeg sur l'affichage virtuel :99
echo -e "\n${YELLOW}[3/5] Démarrage de la capture vidéo directe (ffmpeg x11grab :99)...${NC}"
echo -e "${CYAN}    Fichier cible : $OUTPUT_VIDEO${NC}"

FFMPEG_LOG="/tmp/ffmpeg_record.log"
ffmpeg -y -nostdin -loglevel warning \
  -f x11grab -draw_mouse 0 -video_size 1366x768 -i :99 \
  -c:v libx264 -preset ultrafast -pix_fmt yuv420p \
  "$OUTPUT_VIDEO" > "$FFMPEG_LOG" 2>&1 &
FFMPEG_PID=$!
sleep 1

if ! kill -0 $FFMPEG_PID 2>/dev/null; then
    echo -e "${RED}    ✗ Erreur lors du lancement de ffmpeg :${NC}"
    cat "$FFMPEG_LOG"
    exit 1
fi
echo -e "${GREEN}    ✓ Enregistreur vidéo actif (PID $FFMPEG_PID)${NC}"

cleanup() {
    echo -e "\n${YELLOW}Arrêt de l'enregistrement et finalisation de la vidéo...${NC}"
    if kill -0 $FFMPEG_PID 2>/dev/null; then
        kill -2 $FFMPEG_PID 2>/dev/null || true
        wait $FFMPEG_PID 2>/dev/null || true
    fi
    kill -9 $LAUNCH_PID $WORKER_PID $OPENBOX_PID $XVFB_PID $MAXIMIZER_PID 2>/dev/null || true
    killall -9 gzserver gzclient robot_state_publisher component_container_isolated component_container rviz2 python3 Xvfb openbox 2>/dev/null || true
    rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 2>/dev/null || true

    if [ -f "$OUTPUT_VIDEO" ]; then
        cp -f "$OUTPUT_VIDEO" "$LATEST_VIDEO" 2>/dev/null || true
        FILE_SIZE=$(du -h "$OUTPUT_VIDEO" | cut -f1)
        echo -e "\n${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN} ✓ VIDÉO ENREGISTRÉE AVEC SUCCÈS ! (100% VISIBLE ET COLORÉE)${NC}"
        echo -e "${GREEN}   Fichier : $OUTPUT_VIDEO ($FILE_SIZE)${NC}"
        echo -e "${GREEN}   Lien principal : $LATEST_VIDEO${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
    fi
    exit 0
}
trap cleanup SIGINT SIGTERM

# 5. Lancement Gazebo + Nav2 sur l'affichage virtuel
echo -e "\n${YELLOW}[4/5] Démarrage de Gazebo et de la pile Nav2 sur :99...${NC}"
MAP_PATH="${1:-$HOME/ros2_ws/src/raia_amr_description/maps/raia_factory_map.yaml}"
LOG_FILE="/tmp/nav2_launch.log"
rm -f "$LOG_FILE"

ros2 launch raia_amr_description nav2.launch.py map:="$MAP_PATH" use_rviz:=false > "$LOG_FILE" 2>&1 &
LAUNCH_PID=$!

# Maximisation automatique de la fenêtre 3D Gazebo pour remplir tout l'écran
(
    for i in {1..40}; do
        if DISPLAY=:99 wmctrl -l | grep -q "Gazebo"; then
            DISPLAY=:99 wmctrl -r "Gazebo" -b add,maximized_vert,maximized_horz 2>/dev/null || true
            break
        fi
        sleep 1
    done
) &
MAXIMIZER_PID=$!

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
echo -e "\n${YELLOW}[5/5] Activation de l'obstacle mobile piéton et exécution de la mission...${NC}"
python3 ~/ros2_ws/src/raia_amr_description/worker_patrol.py > /dev/null 2>&1 &
WORKER_PID=$!
sleep 1
echo -e "${GREEN}    ✓ Opérateur piéton positionné sur le couloir de transit${NC}"

# Exécution de la mission
python3 -u ~/ros2_ws/src/raia_amr_description/run_mission.py || true

# Temporisation pour visualiser l'amarrage final à la borne MiR Charge
sleep 4

echo -e "\n${GREEN}Mission terminée ! Finalisation du fichier vidéo...${NC}"
cleanup
