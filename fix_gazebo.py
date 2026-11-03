import os
import urllib.request
import tarfile

home = os.path.expanduser('~')
gazebo_models_dir = os.path.join(home, '.gazebo', 'models')
os.makedirs(gazebo_models_dir, exist_ok=True)

sun_config = """<?xml version="1.0"?>
<model>
  <name>Sun</name>
  <version>1.0</version>
  <sdf version="1.5">model.sdf</sdf>
  <description>A directional light for the sun.</description>
</model>"""

sun_sdf = """<?xml version="1.0" ?>
<sdf version="1.5">
  <light type="directional" name="sun">
    <cast_shadows>true</cast_shadows>
    <pose>0 0 10 0 0 0</pose>
    <diffuse>0.8 0.8 0.8 1</diffuse>
    <specular>0.2 0.2 0.2 1</specular>
    <attenuation>
      <range>1000</range>
      <constant>0.9</constant>
      <linear>0.01</linear>
      <quadratic>0.001</quadratic>
    </attenuation>
    <direction>-0.5 0.1 -0.9</direction>
  </light>
</sdf>"""

gp_config = """<?xml version="1.0"?>
<model>
  <name>Ground Plane</name>
  <version>1.0</version>
  <sdf version="1.5">model.sdf</sdf>
  <description>A simple ground plane.</description>
</model>"""

gp_sdf = """<?xml version="1.0" ?>
<sdf version="1.5">
  <model name="ground_plane">
    <static>true</static>
    <link name="link">
      <collision name="collision">
        <geometry>
          <plane><normal>0 0 1</normal><size>100 100</size></plane>
        </geometry>
      </collision>
      <visual name="visual">
        <cast_shadows>false</cast_shadows>
        <geometry>
          <plane><normal>0 0 1</normal><size>100 100</size></plane>
        </geometry>
        <material>
          <script>
            <uri>file://media/materials/scripts/gazebo.material</uri>
            <name>Gazebo/Grey</name>
          </script>
        </material>
      </visual>
    </link>
  </model>
</sdf>"""

os.makedirs(os.path.join(gazebo_models_dir, 'sun'), exist_ok=True)
os.makedirs(os.path.join(gazebo_models_dir, 'ground_plane'), exist_ok=True)

with open(os.path.join(gazebo_models_dir, 'sun', 'model.config'), 'w') as f:
    f.write(sun_config)
with open(os.path.join(gazebo_models_dir, 'sun', 'model.sdf'), 'w') as f:
    f.write(sun_sdf)

with open(os.path.join(gazebo_models_dir, 'ground_plane', 'model.config'), 'w') as f:
    f.write(gp_config)
with open(os.path.join(gazebo_models_dir, 'ground_plane', 'model.sdf'), 'w') as f:
    f.write(gp_sdf)

print("Local models 'sun' and 'ground_plane' installed successfully in ~/.gazebo/models!")
