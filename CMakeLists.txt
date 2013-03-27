cmake_minimum_required(VERSION 2.8)
project(jlab NONE)

set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake" ${CMAKE_MODULE_PATH})

# TODO
include(JLabMacros)

add_subdirectory(pumping)
