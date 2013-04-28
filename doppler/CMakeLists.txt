set(ALL_DOPPLER_DATAS
  # all_data/4-18/20130418-11_35_44
  all_data/4-18/20130418-12_52_13
  all_data/4-18/20130418-12_54_15
  all_data/4-18/20130418-12_56_31
  all_data/4-18/20130418-13_0_10
  all_data/4-18/20130418-13_16_3
  all_data/4-18/20130418-13_27_10
  all_data/4-18/20130418-13_28_28
  all_data/4-18/20130418-13_35_27
  all_data/4-18/20130418-13_37_29
  all_data/4-18/20130418-13_3_8
  all_data/4-18/20130418-13_45_10
  all_data/4-18/20130418-13_46_0
  all_data/4-18/20130418-13_49_11
  all_data/4-18/20130418-13_50_21
  all_data/4-18/20130418-13_58_49
  all_data/4-18/20130418-13_59_25
  all_data/4-18/20130418-14_12_48
  all_data/4-18/20130418-14_14_27
  all_data/4-18/20130418-14_6_54
  all_data/4-18/20130418-14_8_8
  )

foreach(data ${ALL_DOPPLER_DATAS})
  jlab_add_command(OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/${data}.py"
    COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/loadcsv.py" "${data}.csv"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    DEPENDS "${data}.csv" loadcsv.py)
endforeach()

foreach(data ${ALL_DOPPLER_DATAS})
  jlab_add_command(OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/${data}_combine.py"
    COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/combine_regions.py"
    "${data}.py" "${data}_region.py" "${data}_combine.py"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    DEPENDS "${data}.py" "${data}_region.py" combine_regions.py)
endforeach()

foreach(data ${ALL_DOPPLER_DATAS})
  jlab_add_command(OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/${data}_peak_combine.py"
    COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/combine_peaks.py"
    "${data}.py" "${data}_combine.py" "${data}_peaks_type.py"
    "${data}_peaks_name.py" "all_data/peaks_value.py" "${data}_peak_combine.py"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    DEPENDS combine_regions.py "${data}.py" "${data}_combine.py"
    "${data}_peaks_type.py" "${data}_peaks_name.py" "all_data/peaks_value.py")
endforeach()
