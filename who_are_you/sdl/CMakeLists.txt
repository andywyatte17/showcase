project(who_are_you_sdl)
cmake_minimum_required(VERSION 2.8)
add_executable(${PROJECT_NAME}
  "main.cpp"  "main.h"
  "cairosdl.c"  "cairosdl.h"
  "GameTile.cpp"  "GameTile.h"
  "gamelogic.cpp"  "gamelogic.h"
  "OtherDrawObjs.cpp"  "OtherDrawObjs.h"
  "ScopeGuard.h"
)
add_definitions(-std=c++11 -g)
include_directories(
  "/usr/include/SDL"
  "/usr/include/cairo"
  "../libwhoareyou/whoareyou-cli"
)
target_link_libraries(${PROJECT_NAME} "SDL" "cairo")
