#ifndef OPTIONAL_H
#define OPTIONAL_H

#include <utility>

namespace whoareyou
{
template <typename T> class optional
{
  T t;
  bool engaged = false;

  public:
  optional() = default;
  optional(const optional &rhs) { *this = rhs; }
  optional(optional &&rhs) { *this = std::move(rhs); }
  optional(const T &rhs) { *this = rhs; }
  optional(T &&rhs) { *this = std::move(rhs); }
  optional &operator=(const optional &rhs)
  {
    if (this != &rhs) {
      t = rhs.t;
      engaged = rhs.engaged;
    }
    return *this;
  }
  optional &operator=(optional &&rhs)
  {
    if (this != &rhs) {
      t = std::move(rhs.t);
      engaged = rhs.engaged;
    }
    return *this;
  }
  optional &operator=(const T &rhs_t)
  {
    t = rhs_t;
    engaged = true;
    return *this;
  }
  optional &operator=(T &&rhs_t)
  {
    t = std::move(rhs_t);
    engaged = true;
    return *this;
  }
  const T &operator*() const { return t; }
  T &operator*() { return t; }
  explicit operator bool() const { return engaged; }
  const T &get() const { return t; }
  T &get() { return t; }
};
}

#endif // OPTIONAL_H
