set(BSCAN_RF_NAMES
  bscan_nf/03-15-bscan_nf_rf1
  bscan_nf/03-15-bscan_nf_rf2
  bscan_nf/03-15-bscan_nf_rf3
  bscan_nf/03-15-bscan_nf_rf4
  bscan_nf/03-15-bscan_nf_rf5
  bscan_nf/03-15-bscan_nf_rf6
  bscan_nf/03-15-bscan_nf_rf7
  bscan_nf/03-15-bscan_nf_rf8
  bscan_nf/03-15-bscan_nf_rf9
  )

set(BSWITCH_TEMP_NAMES
  bswitch_nf/03-15-bswitch_nf_temp1
  bswitch_nf/03-15-bswitch_nf_temp2
  bswitch_nf/03-15-bswitch_nf_temp3
  bswitch_nf/03-15-bswitch_nf_temp4
  bswitch_nf/03-15-bswitch_nf_temp5
  bswitch_nf/03-15-bswitch_nf_temp6
  bswitch_nf/03-15-bswitch_nf_temp7
  bswitch_nf/03-15-bswitch_nf_temp8
  bswitch_nf/03-15-bswitch_nf_temp9
  bswitch_nf/03-15-bswitch_nf_temp10
  bswitch_nf/03-15-bswitch_nf_temp11
  bswitch_nf/03-15-bswitch_nf_temp12
  bswitch_nf/03-15-bswitch_nf_temp13
  )

set(BSWITCH_Z_NAMES
  bswitch_nf/03-15-bswitch_nf_z1
  bswitch_nf/03-15-bswitch_nf_z2
  bswitch_nf/03-15-bswitch_nf_z3
  bswitch_nf/03-15-bswitch_nf_z4
  bswitch_nf/03-15-bswitch_nf_z5
  )

set(BSWITCH_OD_NAMES
  bswitch_nf/03-19-bswitch_nf_od1
  bswitch_nf/03-19-bswitch_nf_od2
  bswitch_nf/03-19-bswitch_nf_od3
  bswitch_nf/03-19-bswitch_nf_od4
  bswitch_nf/03-19-bswitch_nf_od5
  bswitch_nf/03-19-bswitch_nf_od6
  bswitch_nf/03-19-bswitch_nf_od7
  bswitch_nf/03-19-bswitch_nf_od8
  bswitch_nf/03-19-bswitch_nf_od9
  bswitch_nf/03-19-bswitch_nf_od10
  bswitch_nf/03-19-bswitch_nf_od11
  bswitch_nf/03-19-bswitch_nf_od12
  )

set(BSWITCH_X_NAMES
  bswitch_nf/03-19-bswitch_nf_x1
  bswitch_nf/03-19-bswitch_nf_x2
  bswitch_nf/03-19-bswitch_nf_x3
  bswitch_nf/03-19-bswitch_nf_x4
  bswitch_nf/03-19-bswitch_nf_x5
  bswitch_nf/03-19-bswitch_nf_x6
  bswitch_nf/03-19-bswitch_nf_x7
  bswitch_nf/03-19-bswitch_nf_x8
  bswitch_nf/03-19-bswitch_nf_x9
  bswitch_nf/03-19-bswitch_nf_x10
  bswitch_nf/03-19-bswitch_nf_x11
  bswitch_nf/03-19-bswitch_nf_x12
  )

set(RFSCAN_Y_NAMES
  rfscan_nf/03-19-rfscan_nf_y1
  rfscan_nf/03-19-rfscan_nf_y2
  rfscan_nf/03-19-rfscan_nf_y3
  rfscan_nf/03-19-rfscan_nf_y4
  rfscan_nf/03-19-rfscan_nf_y5
  rfscan_nf/03-19-rfscan_nf_y6
  rfscan_nf/03-19-rfscan_nf_y7
  rfscan_nf/03-19-rfscan_nf_y8
  rfscan_nf/03-19-rfscan_nf_y9
  rfscan_nf/03-19-rfscan_nf_y10
  rfscan_nf/03-19-rfscan_nf_y11
  )

set(BSCAN_NAMES
  ${BSCAN_RF_NAMES}
  )

set(BSWITCH_NAMES
  ${BSWITCH_TEMP_NAMES}
  ${BSWITCH_Z_NAMES}
  ${BSWITCH_OD_NAMES}
  ${BSWITCH_X_NAMES}
  )

set(RFSCAN_NAMES
  ${RFSCAN_Y_NAMES}
  )

set(RFSWITCH_NAMES
  )

set(DATA_NAMES
  ${BSCAN_NAMES}
  ${BSWITCH_NAMES}
  ${RFSCAN_NAMES}
  ${RFSWITCH_NAMES}
  )

foreach(DATA_NAME ${DATA_NAMES})
  jlab_add_command(OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/${DATA_NAME}.py"
    COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/loadcsv.py" "${DATA_NAME}.csv"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    DEPENDS "${DATA_NAME}.csv" loadcsv.py)
  jlab_add_command(OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/${DATA_NAME}.png"
    COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/plot.py"
    "${DATA_NAME}.py" "${DATA_NAME}.png"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    DEPENDS "${DATA_NAME}.py" plot.py)
endforeach()

foreach(DATA_NAME ${BSWITCH_NAMES})
  jlab_add_command(OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/${DATA_NAME}_peaks.py"
    COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/bswitch.py"
    "${DATA_NAME}.py" "${DATA_NAME}_peaks.py"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    DEPENDS "${DATA_NAME}.py" bswitch.py)
endforeach()

foreach(DATA_NAME ${RFSCAN_NAMES})
  jlab_add_command(OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/${DATA_NAME}_peaks.py"
    COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/rfscan.py"
    "${DATA_NAME}.py" "${DATA_NAME}_peaks.py"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    DEPENDS "${DATA_NAME}.py" rfscan.py)
endforeach()

foreach(DATA_NAME ${BSCAN_NAMES})
  jlab_add_command(OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/${DATA_NAME}_peaks.py"
    COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/bscan.py"
    "${DATA_NAME}.py" "${DATA_NAME}_peaks.py"
    WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
    DEPENDS "${DATA_NAME}.py" bscan.py)
endforeach()

jlab_add_command(OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/all_data/coil_b.py"
  COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/coil.py"
  "all_data/coil.py" "all_data/coil_b.py"
  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
  DEPENDS "all_data/coil.py" coil.py)

set(V_T_DATA
  all_data/03-12-v_T.txt)

set(RFSCAN_14_X_DATA
  rfscan_nf/03-14-rfscan_x.txt)
set(RFSCAN_14_Y_DATA
  rfscan_nf/03-14-rfscan_y.txt)
set(RFSCAN_14_Z_DATA
  rfscan_nf/03-14-rfscan_z.txt)

function(jlab_add_with_suffix lst suf)
  set(tmp_list ${${lst}})
  foreach(ele ${ARGN})
    set(tmp_list ${tmp_list} "${ele}${suf}")
  endforeach()
  set(${lst} ${tmp_list} PARENT_SCOPE)
endfunction()

set(BSCAN_15_RF_DATA_RF
  bscan_nf/03-15-bscan_nf_rf.txt)
set(BSCAN_15_RF_DATA_PEAKS)
jlab_add_with_suffix(BSCAN_15_RF_DATA_PEAKS "_peaks.py" ${BSCAN_RF_NAMES})

# TODO
set(BSWITCH_15_TEMP_DATA_RF
  bswitch_nf/03-15-bswitch_nf_temp.txt)
set(BSWITCH_15_TEMP_DATA_PEAKS)
jlab_add_with_suffix(BSWITCH_15_TEMP_DATA_PEAKS
  "_peaks.py" ${BSWITCH_TEMP_NAMES})

# TODO
set(BSWITCH_15_Z_DATA_PEAKS)
jlab_add_with_suffix(BSWITCH_15_Z_DATA_PEAKS "_peaks.py" ${BSWITCH_Z_NAMES})

set(BSWITCH_19_OD_DATA_RF
  bswitch_nf/03-19-bswitch_nf_od.txt)
set(BSWITCH_19_OD_DATA_PEAKS)
jlab_add_with_suffix(BSWITCH_19_OD_DATA_PEAKS "_peaks.py" ${BSWITCH_OD_NAMES})

# TODO
set(BSWITCH_19_X_DATA_RF
  bswitch_nf/03-19-bswitch_nf_x.txt)
set(BSWITCH_19_X_DATA_PEAKS)
jlab_add_with_suffix(BSWITCH_19_X_DATA_PEAKS "_peaks.py" ${BSWITCH_X_NAMES})

set(RFSCAN_19_Y_DATA_RF
  rfscan_nf/03-19-rfscan_nf_y.txt)
set(RFSCAN_19_Y_DATA_PEAKS)
jlab_add_with_suffix(RFSCAN_19_Y_DATA_PEAKS "_peaks.py" ${RFSCAN_Y_NAMES})

jlab_add_command(OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/rfscan_nf/rfscan_x.py"
  "${CMAKE_CURRENT_SOURCE_DIR}/rfscan_nf/rfscan_x_fit.png"
  COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/rfscan_baxis.py"
  "${RFSCAN_14_X_DATA}" "rfscan_nf/rfscan_x.py" "x" "all_data/coil_b.py"
  "rfscan_nf/rfscan_x"
  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
  DEPENDS "all_data/coil_b.py" rfscan_baxis.py "${RFSCAN_14_X_DATA}")

jlab_add_command(OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/rfscan_nf/rfscan_z.py"
  "${CMAKE_CURRENT_SOURCE_DIR}/rfscan_nf/rfscan_z_fit.png"
  COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/rfscan_baxis.py"
  "${RFSCAN_14_Z_DATA}" "rfscan_nf/rfscan_z.py" "z" "all_data/coil_b.py"
  "rfscan_nf/rfscan_z"
  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
  DEPENDS "all_data/coil_b.py" rfscan_baxis.py "${RFSCAN_14_Z_DATA}")

set(RFSCAN_19_Y_DATA
  rfscan_nf/03-19-rfscan_y.txt)
jlab_add_command(OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/rfscan_nf/rfscan_y.py"
  "${CMAKE_CURRENT_SOURCE_DIR}/rfscan_nf/rfscan_y_fit.png"
  COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/rfscan_baxis.py"
  "${RFSCAN_19_Y_DATA}" "rfscan_nf/rfscan_y.py" "y" "all_data/coil_b.py"
  "rfscan_nf/rfscan_y"
  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
  DEPENDS "all_data/coil_b.py" rfscan_baxis.py "${RFSCAN_19_Y_DATA}")

set(RFSCAN_19_Y_HEIGHTS
  rfscan_nf/03-19-rfscan_y_heights.txt)
jlab_add_command(OUTPUT "${CMAKE_CURRENT_SOURCE_DIR}/${RFSCAN_19_Y_DATA}"
  "${CMAKE_CURRENT_SOURCE_DIR}/${RFSCAN_19_Y_HEIGHTS}"
  COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/rfscan_baxis_combine.py"
  "${RFSCAN_19_Y_DATA}" "${RFSCAN_19_Y_HEIGHTS}" "${RFSCAN_19_Y_DATA_RF}"
  ${RFSCAN_19_Y_DATA_PEAKS}
  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
  DEPENDS "${RFSCAN_19_Y_DATA_RF}" rfscan_baxis_combine.py
  ${RFSCAN_19_Y_DATA_PEAKS})

jlab_add_command(OUTPUT
  "${CMAKE_CURRENT_SOURCE_DIR}/bscan_nf/03-15-bscan_nf_rf_fit.png"
  "${CMAKE_CURRENT_SOURCE_DIR}/bscan_nf/03-15-bscan_nf_rf_fit.py"
  COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/bscan_rf.py"
  bscan_nf/03-15-bscan_nf_rf_fit.py
  bscan_nf/03-15-bscan_nf_rf all_data/coil_b.py
  "${BSCAN_15_RF_DATA_RF}"
  ${BSCAN_15_RF_DATA_PEAKS}
  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
  DEPENDS bscan_rf.py all_data/coil_b.py "${BSCAN_15_RF_DATA_RF}"
  ${RFSCAN_15_RF_DATA_PEAKS})

jlab_add_command(OUTPUT
  "${CMAKE_CURRENT_SOURCE_DIR}/bswitch_nf/03-19-bswitch_nf_od_height.png"
  "${CMAKE_CURRENT_SOURCE_DIR}/bswitch_nf/03-19-bswitch_nf_od_tau.png"
  "${CMAKE_CURRENT_SOURCE_DIR}/bswitch_nf/03-19-bswitch_nf_od_fit.py"
  COMMAND "${CMAKE_CURRENT_SOURCE_DIR}/bswitch_od.py"
  bswitch_nf/03-19-bswitch_nf_od_fit.py
  bswitch_nf/03-19-bswitch_nf_od
  "${BSWITCH_19_OD_DATA_RF}"
  ${BSWITCH_19_OD_DATA_PEAKS}
  WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
  DEPENDS bswitch_od.py "${BSWITCH_19_OD_DATA_RF}" ${BSWITCH_19_OD_DATA_PEAKS})
