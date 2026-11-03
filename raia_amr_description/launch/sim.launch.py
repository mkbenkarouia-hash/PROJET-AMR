import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'raia_amr_description'
    pkg_share = get_package_share_directory(pkg_name)

    # 1. Variables d'environnement WSLg
    set_model_db = SetEnvironmentVariable('GAZEBO_MODEL_DATABASE_URI', '')

    default_world = os.path.join(pkg_share, 'worlds', 'factory_workshop.world')
    world = LaunchConfiguration('world')

    world_arg = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='Chemin absolu vers le fichier monde Gazebo'
    )

    # 2. Inclure le Robot State Publisher (rsp)
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(pkg_share, 'launch', 'rsp.launch.py')
        ]),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # 3. Lancer Gazebo avec le monde d'atelier autonome
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
        ]),
        launch_arguments={'world': world}.items()
    )

    # 4. Spawner le robot raia_amr avec un timeout plus large et gestion propre
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'raia_amr', '-z', '0.05', '-timeout', '60.0'],
        output='screen'
    )

    return LaunchDescription([
        set_model_db,
        world_arg,
        rsp,
        gazebo,
        spawn_entity
    ])
