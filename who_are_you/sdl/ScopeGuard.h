#ifndef SCOPEGUARD_H
#define SCOPEGUARD_H

template <typename F> struct AtExit {
  F f_;
  AtExit() = delete;
  AtExit(const AtExit &) = delete;
  AtExit(F &&f) : f_(std::move(f)) {}
  AtExit(const F &f) : f_(f) {}
  AtExit &operator=(const AtExit &) = delete;
  AtExit(AtExit &&) = default;
  AtExit &operator=(AtExit &&) = default;
  void operator()(void *p) const
  {
    if (p == (void *)1)
      f_();
  }
};

/// El-cheapo ScopeGuard / ScopeExit-type (boost) object. The method 'f'
///   passed is called when the object goes out of scope.
template <typename F> std::unique_ptr<void, AtExit<F>> makeScopeGuard(F f)
{
  using T = std::unique_ptr<void, AtExit<F>>;
  return T((void *)1, AtExit<F>(std::move(f)));
}

#endif // SCOPEGUARD_h
