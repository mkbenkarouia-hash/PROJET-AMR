import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (IncludeLaunchDescription, DeclareLaunchArgument,
                            SetEnvironmentVariable)
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'raia_amr_description'
    pkg_share = get_package_share_directory(pkg_name)

    # ── Variables d'environnement WSLg ────────────────────────────────────
    set_model_db = SetEnvironmentVariable('GAZEBO_MODEL_DATABASE_URI', '')

    # ── Argument : world ──────────────────────────────────────────────────
    default_world = os.path.join(pkg_share, 'worlds', 'factory_workshop.world')
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=default_world,
        description='Monde Gazebo'
    )

    # ── Robot State Publisher (use_sim_time=true) ─────────────────────────
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'rsp.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # ── Gazebo + monde usine ──────────────────────────────────────────────
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('gazebo_ros'),
                'launch', 'gazebo.launch.py'
            )
        ),
        launch_arguments={'world': LaunchConfiguration('world')}.items()
    )

    # ── Spawn du robot raia_amr ───────────────────────────────────────────
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'raia_amr',
            '-z', '0.05',
            '-timeout', '60.0'
        ],
        output='screen'
    )

    # ── SLAM Toolbox (mode asynchrone = moins gourmand en CPU sous WSL2) ──
    slam_params = os.path.join(pkg_share, 'config', 'slam_params.yaml')
    slam_toolbox = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[slam_params],
    )

    # ── RViz2 avec config enrichie (LaserScan + Map + TF) ─────────────────
    rviz_slam_config = os.path.join(pkg_share, 'config', 'rviz_slam.rviz')
    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_slam_config] if os.path.exists(rviz_slam_config)
                  else ['-d', os.path.join(pkg_share, 'config', 'rviz_config.rviz')],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    return LaunchDescription([
        set_model_db,
        world_arg,
        rsp,
        gazebo,
        spawn_entity,
        slam_toolbox,
        rviz2,
    ])
