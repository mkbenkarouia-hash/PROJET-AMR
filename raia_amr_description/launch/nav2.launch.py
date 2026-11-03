import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                            SetEnvironmentVariable)
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name  = 'raia_amr_description'
    pkg_share = get_package_share_directory(pkg_name)

    # ── Variables d'environnement WSLg ────────────────────────────────────
    set_model_db = SetEnvironmentVariable('GAZEBO_MODEL_DATABASE_URI', '')
    fastdds_conf = os.path.join(pkg_share, 'config', 'fastdds_udp_only.xml')
    set_fastdds  = SetEnvironmentVariable('FASTRTPS_DEFAULT_PROFILES_FILE', fastdds_conf)

    # ── Arguments ─────────────────────────────────────────────────────────
    map_yaml_arg = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(pkg_share, 'maps', 'raia_factory_map.yaml'),
        description='Chemin vers la carte .yaml générée par SLAM'
    )
    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz', default_value='true',
        description='Lancer RViz2 avec la config Nav2'
    )
    gui_arg = DeclareLaunchArgument(
        'gui', default_value='true',
        description='Lancer Gazebo avec interface graphique (ou false pour headless)'
    )

    map_yaml    = LaunchConfiguration('map')
    use_rviz    = LaunchConfiguration('use_rviz')
    gui         = LaunchConfiguration('gui')

    # ── Robot State Publisher (use_sim_time=true) ─────────────────────────
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_share, 'launch', 'rsp.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # ── Gazebo + monde usine ──────────────────────────────────────────────
    default_world = os.path.join(pkg_share, 'worlds', 'factory_workshop.world')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('gazebo_ros'),
                'launch', 'gazebo.launch.py'
            )
        ),
        launch_arguments={'world': default_world, 'gui': gui}.items()
    )

    # ── Spawn du robot (Station de recharge MiR Charge : Sud x=0, y=-3.80, Cap=90°) ──
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'raia_amr',
            '-x', '0.0',
            '-y', '-3.80',
            '-z', '0.05',
            '-Y', '1.5708',
            '-timeout', '60.0'
        ],
        output='screen'
    )

    # ── Nav2 Bringup complet ───────────────────────────────────────────────
    nav2_params = os.path.join(pkg_share, 'config', 'nav2_params.yaml')
    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('nav2_bringup'),
                'launch', 'bringup_launch.py'
            )
        ),
        launch_arguments={
            'map':                 map_yaml,
            'use_sim_time':        'true',
            'params_file':         nav2_params,
            'autostart':           'true',
            'use_composition':     'False',
        }.items()
    )

    # ── RViz2 avec configuration Nav2 ─────────────────────────────────────
    rviz_nav2_config = os.path.join(pkg_share, 'config', 'rviz_nav2.rviz')
    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_nav2_config] if os.path.exists(rviz_nav2_config)
                  else [],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(use_rviz),
        output='screen'
    )

    return LaunchDescription([
        set_model_db,
        set_fastdds,
        map_yaml_arg,
        use_rviz_arg,
        gui_arg,
        rsp,
        gazebo,
        spawn_entity,
        nav2_bringup,
        rviz2,
    ])
