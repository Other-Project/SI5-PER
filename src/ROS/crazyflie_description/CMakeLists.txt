cmake_minimum_required(VERSION 3.8)
project(crazyflie_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(sensor_msgs REQUIRED)


if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# Install launch files
install(DIRECTORY
  launch
  urdf
  meshes
  rviz
  config
  worlds
  DESTINATION share/${PROJECT_NAME}/
)

# Install Python executables
install(PROGRAMS
  launch/laser_frame_fixer.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME laser_frame_fixer
)

ament_package()
