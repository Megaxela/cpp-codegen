set(CODEGEN_SCRIPT_FILE ${CMAKE_CURRENT_LIST_DIR}/../main.py)

function(target_codegen TARGET)
  find_package(Python3 COMPONENTS Interpreter)
  if (NOT Python3_Interpreter_FOUND)
    message(FATAL_ERROR "Unable to find python3 interpreter")
  endif()

  get_target_property(TARGET_PROJECT_DIR ${TARGET} SOURCE_DIR)
  get_target_property(TARGET_BUILD_DIR ${TARGET} BINARY_DIR)
  get_target_property(TARGET_INCLUDE_DIRS ${TARGET} INCLUDE_DIRECTORIES)

  set(CODEGEN_INCLUDE_DIR ${TARGET_BUILD_DIR}/include)
  set(CODEGEN_SOURCE_DIR  ${TARGET_BUILD_DIR}/src)

  file(MAKE_DIRECTORY ${CODEGEN_INCLUDE_DIR})
  file(MAKE_DIRECTORY ${CODEGEN_SOURCE_DIR})

  set(CODEGEN_SCRIPT_ARGS
    ${Python3_EXECUTABLE}
    ${CODEGEN_SCRIPT_FILE}
    --project_dir ${TARGET_PROJECT_DIR}
    --output_include_dir ${CODEGEN_INCLUDE_DIR}
    --output_source_dir ${CODEGEN_SOURCE_DIR}
    --namespace ''
    --ignore_path_glob test_*
    --ignore_path_glob ${CODEGEN_INCLUDE_DIR}/*
    --ignore_path_glob ${CODEGEN_SOURCE_DIR}/*
  )
  foreach (TARGET_INCLUDE_DIR ${TARGET_INCLUDE_DIRS})
    list(APPEND CODEGEN_SCRIPT_ARGS --project_include_dir)
    list(APPEND CODEGEN_SCRIPT_ARGS ${TARGET_INCLUDE_DIR})
  endforeach()

  execute_process(
    COMMAND ${CODEGEN_SCRIPT_ARGS}
    WORKING_DIRECTORY ${TARGET_PROJECT_DIR}
    RESULT_VARIABLE EXIT_CODE
    ERROR_VARIABLE ERROR_DATA
  )

  # list(JOIN CODEGEN_SCRIPT_ARGS " " COMMAND_STR)
  # message(STATUS ${COMMAND_STR})

  if (NOT ${EXIT_CODE} STREQUAL "0")
    message(SEND_ERROR "Generator status code: ${EXIT_CODE}")
    message(SEND_ERROR ${ERROR_DATA})
    message(FATAL_ERROR "Unable to execute generator on '${TARGET}' target")
  endif()

  # Iterating new sources
  file(GLOB_RECURSE SRC_FILES ${CODEGEN_SOURCE_DIR}/*.cpp)
  target_sources(${TARGET}
    PRIVATE
      ${SRC_FILES}
  )

  target_include_directories(${TARGET}
    PUBLIC
      ${CODEGEN_INCLUDE_DIR}
  )
endfunction()
