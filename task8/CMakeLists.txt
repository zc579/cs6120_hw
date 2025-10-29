cmake_minimum_required(VERSION 3.13)
project(IndVarElim LANGUAGES C CXX)


# 针对 LLVM 14
find_package(LLVM 14 REQUIRED CONFIG)

list(APPEND CMAKE_MODULE_PATH ${LLVM_CMAKE_DIR})
include(AddLLVM)
include(HandleLLVMOptions)

message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")

include_directories(${LLVM_INCLUDE_DIRS})
add_definitions(${LLVM_DEFINITIONS})

# 生成 opt 可加载的插件
add_library(IndVarElimPass MODULE IndVarElim.cpp)

# C++17
set_property(TARGET IndVarElimPass PROPERTY CXX_STANDARD 17)
set_property(TARGET IndVarElimPass PROPERTY CXX_STANDARD_REQUIRED ON)

# 避免在某些平台上导出符号被隐藏
if (NOT WIN32)
  set_target_properties(IndVarElimPass PROPERTIES
    COMPILE_FLAGS "-fno-rtti"
  )
endif()
