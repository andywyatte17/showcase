#include "main.h"
#include "gamelogic.h"
#include "GameTile.h"
#include "OtherDrawObjs.h"

void init_draw_objs(std::vector<std::unique_ptr<IDrawObj>> &v)
{
  v.push_back(MakeBackgroundDrawObj());
  enum { W = 6, H = 4 };
  for (int y = 0; y < H; ++y)
    for (int x = 0; x < W; ++x)
      v.push_back(MakeGameTile(x, y, W, H));
}
