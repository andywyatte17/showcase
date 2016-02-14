//
// GameTile.cpp
//

#include "main.h"
#include <math.h>
#include "optional.h"
#include "ScopeGuard.h"

using namespace whoareyou;

void cairo_ellipse(cairo_t *cr, double x, double y, double w, double h,
                   optional<double> rotation = optional<double>())
{
  cairo_save(cr);
  auto sgCairoRestore = makeScopeGuard([=]() { cairo_restore(cr); });
  cairo_new_sub_path(cr);
  cairo_translate(cr, x, y);
  cairo_scale(cr, w, h);
  if (rotation)
    cairo_rotate(cr, *rotation);
  cairo_translate(cr, -x, -y);
  cairo_arc(cr, x, y, 1, 0, 6.28);
  cairo_close_path(cr);
}

void cairo_rounded_rect(cairo_t *cr, double x, double y, double width,
                        double height, double radius)
{
  cairo_new_sub_path(cr);
  double from_degrees = M_PI / 180.0;
  cairo_arc(cr, x + width - radius, y + radius, radius, -90 * from_degrees,
            0 * from_degrees);
  cairo_arc(cr, x + width - radius, y + height - radius, radius,
            0 * from_degrees, 90 * from_degrees);
  cairo_arc(cr, x + radius, y + height - radius, radius, 90 * from_degrees,
            180 * from_degrees);
  cairo_arc(cr, x + radius, y + radius, radius, 180 * from_degrees,
            270 * from_degrees);
  cairo_close_path(cr);
}

struct RectXYWH {
  int x, y, w, h;
};

enum class EAnimating { no, to_visible, to_invisible };

class Rect : public IDrawObj, public IEvents
{
  int width = 0, height = 0;
  int px, py, nx, ny;
  RectXYWH r2, r;
  bool is_visible = true;

  float animating_start_time = 0.0f;
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
    r2.x = margin * (1 + px) + px * w;
    r2.y = margin * (1 + py) + py * h;
    r2.w = static_cast<int>(w);
    r2.h = static_cast<int>(h);
    const float w_div_h = 0.7;
    r = r2;
    auto newW = r.h * w_div_h;
    if (newW > r.w) {
      auto newH = r.w / w_div_h;
      r.y += (r.h - newH) / 2;
      r.h = newH;
    } else {
      r.x += (r.w - newW) / 2;
      r.w = newW;
    }
  }

  void draw(double time, CairoSurface_t pSurface) override
  {
    cairo_t *cr = cairo_create(pSurface.get());
    auto sgCairoDestroy = makeScopeGuard([=]() { cairo_destroy(cr); });
    struct RGB {
      float r, g, b;
    };
    const auto Gray = RGB{0.98, 0.98, 0.98};
    const auto Yellow = RGB{0.9, 0.9, 0.5};

    auto FillRect = [cr](int x, int y, int w, int h, RGB rgb) {
      cairo_set_source_rgba(cr, rgb.r, rgb.g, rgb.b, 1);
      cairo_rounded_rect(cr, x, y, w, h, 5);
      cairo_close_path(cr);
      cairo_fill(cr);
    };

    auto absf = [](float x) { return x < 0 ? -x : x; };
    cairo_set_operator(cr, CAIRO_OPERATOR_OVER);
    {
      float squeeze = 0;
      bool visible = this->is_visible;
      if (this->animating != EAnimating::no) {
        float ani_mid = this->animating_start_time + animate_duration / 2;
        const auto time_from_mid = time - ani_mid;
        auto mSqueeze
            = cos((M_PI / 2) * (absf(time_from_mid) / (animate_duration / 2)));
        squeeze = (r.h - 10.0f) * mSqueeze;
        if ((time_from_mid < 0) ^ (animating == EAnimating::to_visible))
          visible = true;
        else
          visible = false;
      }

      const auto centreX = r.x + r.w / 2.0;
      const auto centreY = r.y + r.h / 2.0;
      cairo_save(cr);
      auto sgCairoRestore = makeScopeGuard([cr]() { cairo_restore(cr); });

      cairo_translate(cr, centreX, centreY);
      cairo_scale(cr, 1, (r.h - squeeze) / r.h);
      cairo_translate(cr, -centreX, -centreY);

      if (visible) {
        FillRect(r.x, r.y, r.w, r.h, Yellow);
        FillRect(r.x + r.w / 10.0, r.y + r.h / 10.0, r.w - r.w / 5.0,
                 r.h - r.h / 5.0, Gray);
        cairo_ellipse(cr, centreX, centreY, r.w / 3.0, r.h / 3.0);
        cairo_ellipse(cr, centreX - r.w / 8.0, centreY, r.w / 20.0, r.h / 40.0);
        cairo_ellipse(cr, centreX + r.w / 8.0, centreY, r.w / 20.0, r.h / 40.0);
        cairo_ellipse(cr, centreX - r.w / 8.0, centreY, r.w / 20.0, r.h / 40.0);
        cairo_ellipse(cr, centreX, centreY + r.h / 5.0, r.w / 10.0, r.h / 40.0);
        cairo_ellipse(cr, centreX, centreY + r.h / 12.0, r.w / 40.0,
                      r.h / 20.0);
        cairo_set_source_rgb(cr, 0, 0, 0);
        ::cairo_set_line_width(cr, r.h / 100.0);
        cairo_stroke(cr);

        // hair
        cairo_ellipse(cr, centreX - r.w / 5.0, centreY - r.h / 5.0, r.w / 12.0,
                      r.h / 8.0, 45 * (M_PI / 180.0));
        cairo_fill(cr);

      } else
        FillRect(r.x, r.y, r.w, r.h, Yellow);
    }
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
