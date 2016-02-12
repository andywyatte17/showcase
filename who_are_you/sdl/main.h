#ifndef MAIN_H
#define MAIN_H

#include <memory>
#include <vector>
#include <cairo.h>

using CairoSurface_t = std::shared_ptr<cairo_surface_t>;

enum class EAcceptEvent { accept, reject };

struct IEvents {
  virtual ~IEvents() {}
  virtual void NoOp(float time) {}
  virtual EAcceptEvent OnMouseDown(float time, int x, int y)
  {
    return EAcceptEvent::reject;
  }
  virtual EAcceptEvent OnMouseUp(float time, int x, int y) { return EAcceptEvent::reject; }
  virtual EAcceptEvent OnMouseMove(float time, int x, int y)
  {
    return EAcceptEvent::reject;
  }
};

struct IDrawObj {
  virtual ~IDrawObj() {}
  virtual void set_size(int width, int height) {}
  virtual void draw(double time, CairoSurface_t pSurface) = 0;
};

void init_draw_objs(std::vector<std::unique_ptr<IDrawObj>> &v);

#endif // MAIN_H
