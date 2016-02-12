#ifndef GAMETIME_H
#define GAMETIME_H

#include "main.h"
#include <memory>

std::unique_ptr<IDrawObj> MakeGameTile(int px, int py, int nx, int ny);

#endif // GAMETIME_H
