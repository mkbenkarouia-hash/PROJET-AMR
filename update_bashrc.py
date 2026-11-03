import os

bashrc_path = '/home/khalilvr/.bashrc'
with open(bashrc_path, 'r') as f:
    lines = f.readlines()

config_lines = [
    "# === CONFIGURATION ROS 2 & GAZEBO WSLG ===\n",
    "source /opt/ros/humble/setup.bash\n",
    "source /home/khalilvr/ros2_ws/install/setup.bash\n",
    "export LIBGL_ALWAYS_SOFTWARE=1\n",
    "export GALLIUM_DRIVER=llvmpipe\n",
    "export GAZEBO_MODEL_DATABASE_URI=\"\"\n",
    "alias clean_gazebo=\"killall -9 gzserver gzclient 2>/dev/null; echo 'Processus Gazebo nettoyés !'\"\n",
    "# ==========================================\n\n"
]

# Filter out old duplicates if present at the end
clean_lines = []
for line in lines:
    if any(k in line for k in ['GALLIUM_DRIVER', 'MESA_D3D12', 'LIBGL_ALWAYS_SOFTWARE', 'clean_gazebo', 'GAZEBO_MODEL_DATABASE_URI']):
        continue
    clean_lines.append(line)

final_content = "".join(config_lines) + "".join(clean_lines)

with open(bashrc_path, 'w') as f:
    f.write(final_content)

print("Updated ~/.bashrc cleanly with ROS 2 and Gazebo configuration at the top!")
