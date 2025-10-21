#!/usr/bin/python3
# Copyright 2020, EAIBOT
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch_ros.actions import LifecycleNode
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch.actions import LogInfo

import lifecycle_msgs.msg
import os

LIDAR_NUM = 2

def generate_launch_description():
    share_dir = get_package_share_directory("ydlidar_ros2_driver")
    rviz_config_file = os.path.join(share_dir, "config", "ydlidar.rviz")
    parameter_file = LaunchConfiguration("params_file")
    params_declare = DeclareLaunchArgument(
        "params_file",
        default_value=os.path.join(share_dir, "params", "GS5.yaml"),
        description="FPath to the ROS2 parameters file to use.",
    )

    # Generate driver nodes using a loop for maintainability
    driver_nodes = [
        LifecycleNode(
            package="ydlidar_ros2_driver",
            executable="ydlidar_ros2_driver_node",
            name=f"ydlidar_ros2_driver_node_{i+1}",
            output="screen",
            emulate_tty=True,
            parameters=[parameter_file],
            namespace="/",
            remappings=[("/scan", f"/scan_{i+1}")],
        )
        for i in range(LIDAR_NUM)  # Change to 6 if you want all 6 nodes enabled
    ]
    # tf2 static transform parameters for each lidar
    tf2_params = [
        # x, y, z, roll, pitch, yaw, frame_id, child_frame_id
        ("0.130",  "0.048",  "0.000", "0", "0",  "0.38048",  "base_link", "laser_frame_1"),  # 左前
        ("0.130",  "-0.048", "0.000", "0", "0", "-0.38048",  "base_link", "laser_frame_2"),  # 右前
        # ("0.0",    "0.0954", "0.000", "0", "0",  "1.0",      "base_link", "laser_frame_3"),  # 左
        # ("0.0",    "-0.0954","0.000", "0", "0", "-1.0",      "base_link", "laser_frame_4"),  # 右
        # ("-0.130", "0.048",  "0.000", "0", "0",  "2.76",     "base_link", "laser_frame_5"),  # 左後
        # ("-0.130", "-0.048", "0.000", "0", "0", "-2.76",     "base_link", "laser_frame_6"),  # 右後
    ]
    tf2_nodes = [
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name=f"static_tf_pub_laser_{i+1}",
            arguments=[
                x, y, z, roll, pitch, yaw, "1", frame_id, child_frame_id
            ],
        )
        for i, (x, y, z, roll, pitch, yaw, frame_id, child_frame_id) in enumerate(tf2_params)
    ]
    rviz2_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config_file],
    )

    return LaunchDescription(
        [
            # params_declare,
            # *driver_nodes,
            *tf2_nodes,
            rviz2_node,
        ]
    )
