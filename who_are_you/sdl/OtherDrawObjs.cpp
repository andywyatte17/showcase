//
// DrawObjs.cpp
//

#include "main.h"
#include "OtherDrawObjs.h"
#include <math.h>

class Background : public IDrawObj
{
  int width = 0, height = 0;

  public:
  void set_size(int width, int height) override
  {
    this->width = width;
    this->height = height;
  }
  void draw(double time, CairoSurface_t pSurface) override
  {
    cairo_t *cr = cairo_create(pSurface.get());
    cairo_set_source_rgba(cr, 0, 0.6, 0, 1);
    cairo_paint(cr);
    cairo_destroy(cr);
  }
};

std::unique_ptr<IDrawObj> MakeBackgroundDrawObj()
{
  return std::unique_ptr<IDrawObj>{new Background{}};
}
