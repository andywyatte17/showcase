//
// GameTile.cpp
//

#include "main.h"
#include <math.h>

struct RectXYWH {
  int x, y, w, h;
};

class Rect : public IDrawObj, public IEvents
{
  int width = 0, height = 0;
  int px, py, nx, ny;
  RectXYWH r;
  bool is_visible = true;

  float animating_start_time = 0.0f;
  enum class EAnimating { no, to_visible, to_invisible };
  EAnimating animating = EAnimating::no;
  const float animate_duration = 1.0f;

  public:
  Rect() = delete;

  Rect(int pxi, int pyi, int nxi, int nyi) : px(pxi), py(pyi), nx(nxi), ny(nyi)
  {
  }

  void NoOp(float t) override
  {
    if (t > (this->animating_start_time + animate_duration))
      animating = EAnimating::no;
  }

  void set_size(int width, int height) override
  {
    this->width = width;
    this->height = height;
    const int margin = 10;
    width -= 200;
    width -= (nx + 1) * margin;
    height -= (ny + 1) * margin;
    float w = static_cast<float>(width) / nx;
    float h = static_cast<float>(height) / ny;
    r.x = margin * (1 + px) + px * w;
    r.y = margin * (1 + py) + py * h;
    r.w = static_cast<int>(w);
    r.h = static_cast<int>(h);
  }

  void draw(double time, CairoSurface_t pSurface) override
  {
    cairo_t *cr = cairo_create(pSurface.get());
    auto BackgroundToGray =
        [&]() { cairo_set_source_rgba(cr, 0.9, 0.9, 0.9, 1); };
    auto BackgroundToYellow =
        [&]() { cairo_set_source_rgba(cr, 0.9, 0.9, 0.5, 1); };

    auto absf = [](float x) { return x < 0 ? -x : x; };
    cairo_set_operator(cr, CAIRO_OPERATOR_OVER);
    if (this->animating == EAnimating::no) {
      if (this->is_visible)
        BackgroundToGray();
      else
        BackgroundToYellow();
      cairo_rectangle(cr, r.x, r.y, r.w, r.h);
    } else {
      float ani_mid = this->animating_start_time + animate_duration / 2;
      auto time_from_mid = time - ani_mid;
      if ((time_from_mid < 0) ^ (animating == EAnimating::to_visible))
        BackgroundToGray();
      else
        BackgroundToYellow();
      float squeeze = (r.h - 10.0f)
                      * (1 - (absf(time_from_mid) / (animate_duration / 2)));
      cairo_rectangle(cr, r.x, r.y + squeeze / 2, r.w, r.h - squeeze);
    }
    cairo_close_path(cr);
    cairo_fill(cr);
    cairo_destroy(cr);
  }
  EAcceptEvent OnMouseDown(float time, int x, int y) override
  {
    if (r.x <= x && x <= r.x + r.w && r.y <= y && y <= r.y + r.h) {
      if (this->animating == EAnimating::no) {
        this->animating_start_time = time;
        this->animating = is_visible ? EAnimating::to_invisible
                                     : EAnimating::to_visible;
        this->is_visible = !this->is_visible;
      }
      return EAcceptEvent::accept;
    }
    return EAcceptEvent::reject;
  }
  EAcceptEvent OnMouseUp(float time, int x, int y) override
  {
    return EAcceptEvent::reject;
  }
  EAcceptEvent OnMouseMove(float time, int x, int y) override
  {
    return EAcceptEvent::reject;
  }
};

std::unique_ptr<IDrawObj> MakeGameTile(int px, int py, int nx, int ny)
{
  return std::unique_ptr<IDrawObj>{new Rect{px, py, nx, ny}};
}
