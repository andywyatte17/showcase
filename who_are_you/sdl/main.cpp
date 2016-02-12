#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <memory>
#include <functional>
#include <vector>
#include "cairosdl.h"
#include "main.h"
#include <algorithm>

#define dprintf(args)

static void blit_using_cairo(cairo_surface_t *pSurface)
{
  size_t i;
  SDL_Surface *screen = SDL_GetVideoSurface();
  cairo_t *cr;

  while (SDL_LockSurface(screen) != 0) {
    SDL_Delay(1);
  }

  cr = cairosdl_create(screen);

  int width = cairo_image_surface_get_width(pSurface);
  int height = cairo_image_surface_get_height(pSurface);

  cairo_set_source_surface(cr, pSurface, 0, 0);
  cairo_rectangle(cr, 0, 0, width, height);
  cairo_fill(cr);

  cairo_destroy(cr);

  SDL_UnlockSurface(screen);
}

static void push_expose()
{
  SDL_Event event[1];
  event->type = SDL_VIDEOEXPOSE;
  if (SDL_PushEvent(event) != 0) {
    fprintf(stderr, "Failed to push an expose event: %s\n", SDL_GetError());
  }
}

static void on_expose(CairoSurface_t surface)
{
  SDL_Surface *screen = SDL_GetVideoSurface();
  SDL_FillRect(screen, NULL,
               SDL_MapRGBA(screen->format, 0, 0, 0, SDL_ALPHA_OPAQUE));
  blit_using_cairo(surface.get());
  SDL_Flip(screen);
  push_expose(); /* Schedule another expose soon, */
}

static void event_loop(unsigned flags, int width, int height)
{
  double t0 = SDL_GetTicks() / 1000.0; /* Current simulation time.. */
  double t1;                           /* Next simulation time. */
  SDL_Event event[1];
  CairoSurface_t surface;

  std::vector<std::unique_ptr<IDrawObj>> objs;
  init_draw_objs(objs);

  for (auto &x : objs)
    x->set_size(width, height);

  event->resize.type = SDL_VIDEORESIZE;
  event->resize.w = width;
  event->resize.h = height;
  SDL_PushEvent(event);

  for (;;) {
    // auto ev = SDL_WaitEvent(event);
    t1 = SDL_GetTicks() / 1000.0;
    for (auto &x : objs)
      if (auto *p = dynamic_cast<IEvents *>(x.get()))
        p->NoOp(t1);
    auto ev = SDL_PollEvent(event);
    if (!ev) {
      fprintf(stderr, "PollEvent failed: %s\n", SDL_GetError());
    } else {
      t1 = SDL_GetTicks() / 1000.0;
      switch (event->type) {
      case SDL_VIDEORESIZE:
        if (SDL_SetVideoMode(event->resize.w, event->resize.h, 32, flags)
            == NULL) {
          fprintf(stderr, "Failed to set video mode: %s\n", SDL_GetError());
          exit(1);
        }
        width = event->resize.w;
        height = event->resize.h;
        for (auto &x : objs)
          x->set_size(width, height);
        surface = std::shared_ptr<cairo_surface_t>(
            cairo_image_surface_create(CAIRO_FORMAT_ARGB32, width, height),
            [](cairo_surface_t *p) { cairo_surface_destroy(p); });
        blit_using_cairo(surface.get());
      /* fallthrough  */

      case SDL_VIDEOEXPOSE:
        // fprintf(stderr, "Draw - %fs\n", (double)t1);
        for (auto &x : objs)
          x->draw(t1, surface);
        blit_using_cairo(surface.get());
        on_expose(surface);
        break;

      case SDL_MOUSEBUTTONDOWN:
        std::any_of(
            objs.rbegin(), objs.rend(), [&](std::unique_ptr<IDrawObj> &x) {
              if (auto *p = dynamic_cast<IEvents *>(x.get()))
                return p->OnMouseDown(t1, event->motion.x, event->motion.y)
                       == EAcceptEvent::accept;
              return false;
            });
        break;

      case SDL_MOUSEMOTION:
        std::any_of(
            objs.rbegin(), objs.rend(), [&](std::unique_ptr<IDrawObj> &x) {
              if (auto *p = dynamic_cast<IEvents *>(x.get()))
                return p->OnMouseMove(t1, event->motion.x, event->motion.y)
                       == EAcceptEvent::accept;
              return false;
            });
        break;

      case SDL_MOUSEBUTTONUP:
        std::any_of(
            objs.rbegin(), objs.rend(), [&](std::unique_ptr<IDrawObj> &x) {
              if (auto *p = dynamic_cast<IEvents *>(x.get()))
                return p->OnMouseUp(t1, event->motion.x, event->motion.y)
                       == EAcceptEvent::accept;
              return false;
            });
        break;

      case SDL_KEYDOWN:
        if (event->key.keysym.sym == SDLK_q)
          return;
      }
    }
  }
}

int main()
{
  int width = 800;
  int height = 600;
  int flags = SDL_INIT_TIMER | SDL_INIT_VIDEO | SDL_INIT_NOPARACHUTE;

  if (SDL_Init(flags) < 0) {
    fprintf(stderr, "Failed to initialise SDL: %s\n", SDL_GetError());
    exit(1);
  }
  atexit(SDL_Quit);

  if (1) {
    event_loop(SDL_SWSURFACE | SDL_RESIZABLE, width, height);
  } else {
    event_loop(SDL_HWSURFACE | SDL_FULLSCREEN | SDL_DOUBLEBUF, width, height);
  }
  return 0;
}
