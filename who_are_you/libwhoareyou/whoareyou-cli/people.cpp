//
// people.cpp
//

#include "people.h"
#include <random>

using namespace whoareyou;

Names_t whoareyou::names()
{
  // I did want to protect static construction here with std::call_once
  //   but it crashed on this compile. Should be protected by C++11 'magic
  //   statics'
  //   when implemented.
  static Names_t s_names
      = std::make_shared<std::vector<std::string>>(std::vector<std::string>{
          "Simon", "Sarah", "Tracy", "Stan", "Barry", "Brian", "Laura", "Colin",
          "Trevor", "Terry", "Sam", "Bill", "David", "Steve", "Rachel",
          "Grace"});
  return s_names;
}

namespace
{
template <typename E, typename Rand> auto RandomOfEnum(Rand &r) -> E
{
  auto ix
      = std::uniform_int_distribution<>(0, static_cast<int>(E::_count_) - 1)(r);
  return static_cast<E>(ix);
}

template <typename E, typename Rand>
auto RandomOf(Rand &r, std::initializer_list<E> e) -> E
{
  auto ix = std::uniform_int_distribution<>(0, e.size() - 1)(r);
  return *std::next(e.begin(), ix);
}

template <typename E>
std::ostream &EnumMap(std::ostream &o, E e,
                      std::vector<std::pair<E, std::string>> esp)
{
  for (const auto &x : esp) {
    if (x.first == e) {
      o << x.second;
      return o;
    }
  }
  o << "??";
  return o;
}
}

std::ostream &whoareyou::operator<<(std::ostream &o, const FaceFeature &v)
{
  using T = FaceFeature;
  static_assert(static_cast<int>(T::_count_) == 4, "...");
  return EnumMap(o, v, {{T::eyes, "eyes"},
                        {T::hair, "hair"},
                        {T::nose, "nose"},
                        {T::mouth, "mouth"}});
}

std::ostream &whoareyou::operator<<(std::ostream &o, const Size &v)
{
  using T = Size;
  static_assert(static_cast<int>(T::_count_) == 2, "...");
  return EnumMap(o, v, {{T::small, "small"}, {T::large, "large"}});
}

std::ostream &whoareyou::operator<<(std::ostream &o, const Colour &v)
{
  using T = Colour;
  static_assert(static_cast<int>(T::_count_) == 6, "...");
  return EnumMap(o, v, {
                        {Colour::blond, "blond"},
                        {Colour::blue, "blue"},
                        {Colour::brown, "brown"},
                        {Colour::gray, "gray"},
                        {Colour::red, "red"},
                        {Colour::white, "white"},
                       });
}

std::unique_ptr<PersonFactory>
whoareyou::RandomPersonFactory(optional<uint32_t> seed)
{
  struct Factory : PersonFactory {
    std::mt19937 mt;
    std::vector<utf8str_t> names;
    int names_left = 0;
    Factory(optional<uint32_t> seed) : mt(seed ? *seed : std::random_device()())
    {
      for (auto &n : *whoareyou::names())
        names.push_back(n);
      names_left = names.size();
    }
    Person create() override
    {
      Person p;
      if (names_left == 0)
        throw OutOfNamesException{};
      auto ix = std::uniform_int_distribution<>(0, names_left - 1)(mt);
      p.name = names[ix];
      names_left--;
      std::swap(names[ix], names[names_left]);
      p.features.push_back(Feature::MakeFace(RandomOfEnum<Colour>(mt)));
      p.features.push_back(Feature::MakeNose(RandomOfEnum<Size>(mt)));
      p.features.push_back(Feature::MakeMouth(RandomOfEnum<Size>(mt)));
      p.features.push_back(Feature::MakeEyes(
          RandomOf<Colour>(mt, {Colour::blue, Colour::brown})));
      return p;
    }
  };
  return std::unique_ptr<PersonFactory>(new Factory(seed));
}

std::ostream &whoareyou::operator<<(std::ostream &o,
                                    const whoareyou::Person &person)
{
  o << person.name << " : ";
  for (auto &x : person.features) {
    o << x.feature;
    if (x.size)
      o << " " << *x.size;
    if (x.colour)
      o << " " << *x.colour;
    o << ", ";
  }
  return o;
}
