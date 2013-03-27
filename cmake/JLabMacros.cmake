#   Copyright (C) 2013~2013 by Yichao Yu
#   yyc1992@gmail.com
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

include(CMakeParseArguments)

get_filename_component(JLAB_MACRO_CMAKE_DIR
  "${CMAKE_CURRENT_LIST_FILE}" PATH)
set(JLAB_CMAKE_HELPER "${JLAB_MACRO_CMAKE_DIR}/jlab-cmake-helper.sh")

function(jlab_std_fname var fname)
  get_filename_component(fname "${fname}" ABSOLUTE)
  file(RELATIVE_PATH rel_path "${PROJECT_SOURCE_DIR}" "${fname}")
  set(${var} "${rel_path}" PARENT_SCOPE)
endfunction()

function(jlab_file_to_unique_name var fname)
  jlab_std_fname(std_fname "${fname}")
  execute_process(COMMAND "${JLAB_CMAKE_HELPER}" --unique-name "${std_fname}"
    OUTPUT_VARIABLE unique_name)
  set(${var} "${unique_name}" PARENT_SCOPE)
endfunction()

function(jlab_get_unique_name name unique_name)
  set(property_name "JLAB_UNIQUE_COUNTER_${name}")
  get_property(current_counter GLOBAL PROPERTY "${property_name}")
  if(NOT current_counter)
    set(current_counter 1)
  endif()
  set(${unique_name} "jlab-${name}-${current_counter}" PARENT_SCOPE)
  math(EXPR current_counter "${current_counter} + 1")
  set_property(GLOBAL PROPERTY "${property_name}" "${current_counter}")
endfunction()

function(jlab_add_command)
  set(options)
  set(one_value_args WORKING_DIRECTORY)
  set(multi_value_args OUTPUT DEPENDS
    # TODO
    COMMAND)
  cmake_parse_arguments(JLAB_COMMAND
    "${options}" "${one_value_args}" "${multi_value_args}" ${ARGN})

  jlab_get_unique_name(add-command unique_name)
  # set(target_names)
  # foreach(output_file ${JLAB_COMMAND_OUTPUT})
  #   jlab_file_to_unique_name(tgt_name "${output_file}")
  #   set(target_names ${target_names} ${tgt_name})
  # endforeach()
  set(STAMP_FILE "${PROJECT_BINARY_DIR}/.${unique_name}.stamp")

  set(command_extra_arg)
  if(NOT "${JLAB_COMMAND_WORKING_DIRECTORY}" STREQUAL "")
    set(command_extra_arg ${command_extra_arg}
      WORKING_DIRECTORY "${JLAB_COMMAND_WORKING_DIRECTORY}")
  endif()

  add_custom_target(${unique_name}.depend)
  add_custom_command(OUTPUT ${STAMP_FILE}
    COMMAND ${JLAB_COMMAND_COMMAND}
    COMMAND "${CMAKE_COMMAND}" -E touch "${STAMP_FILE}"
    ${command_extra_arg}
    DEPENDS ${JLAB_COMMAND_DEPENDS} ${unique_name}.depend)

  add_custom_target(${unique_name}.target ALL DEPENDS "${STAMP_FILE}")
  add_custom_command(OUTPUT ${JLAB_COMMAND_OUTPUT}
    DEPENDS ${unique_name}.target)
  add_custom_target(${unique_name} ALL DEPENDS ${JLAB_COMMAND_OUTPUT})

  _jlab_add_dependencies(${unique_name}.depend ${JLAB_COMMAND_DEPENDS})
  _jlab_register_output(${unique_name}.target ${JLAB_COMMAND_OUTPUT})
endfunction()

function(_jlab_add_dependencies target)
  foreach(depend ${ARGN})
    jlab_file_to_unique_name(unique_name "${depend}")
    get_property(depend_target GLOBAL PROPERTY "${unique_name}.target")
    if(depend_target)
      add_dependencies(${target} ${depend_target})
    endif()
    get_property(depend_list GLOBAL PROPERTY "${unique_name}.depend")
    if(NOT depend_list)
      set(depend_list)
    endif()
    set(depend_list ${depend_list} ${target})
    set_property(GLOBAL PROPERTY "${unique_name}.depend" "${depend_list}")
  endforeach()
endfunction()

function(_jlab_register_output target)
  foreach(output ${ARGN})
    jlab_file_to_unique_name(unique_name "${output}")
    set_property(GLOBAL PROPERTY "${unique_name}.target" ${target})
    get_property(depend_list GLOBAL PROPERTY "${unique_name}.depend")
    if(depend_list)
      foreach(depend ${depend_list})
        add_dependencies(${depend} ${target})
      endforeach()
    endif()
  endforeach()
endfunction()
