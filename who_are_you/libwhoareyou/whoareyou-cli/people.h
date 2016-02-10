//
// people.h
//

#pragma once

#include <string>
#include <vector>
#include <memory>
#include <iostream>
#include "optional.h"

namespace whoareyou
{
using utf8str_t = std::string;

using Names_t = std::shared_ptr<const std::vector<utf8str_t>>;

enum class FaceFeature {
  eyes,
  hair,
  nose,
  mouth,
  /* _count_ must be last! */ _count_
};

enum class Size { large, small, /* _count_ must be last! */ _count_ };

enum class Colour {
  red,
  brown,
  blond,
  gray,
  white,
  blue,
  /* _count_ must be last! */ _count_
};

struct Feature {
  Feature() = default;
  Feature(const Feature &) = default;
  Feature &operator=(const Feature &) = default;
  FaceFeature feature;
  optional<Size> size;
  optional<Colour> colour;
  static Feature MakeFace(Colour colour)
  {
    auto rv = Feature{};
    rv.feature = FaceFeature::hair;
    rv.colour = colour;
    return rv;
  }
  static Feature MakeEyes(Colour colour)
  {
    auto rv = Feature{};
    rv.feature = FaceFeature::eyes;
    rv.colour = colour;
    return rv;
  }
  static Feature MakeNose(Size size)
  {
    auto rv = Feature{};
    rv.feature = FaceFeature::nose;
    rv.size = size;
    return rv;
  }
  static Feature MakeMouth(Size size)
  {
    auto rv = Feature{};
    rv.feature = FaceFeature::mouth;
    rv.size = size;
    return rv;
  }
};

class Person
{
  public:
  virtual ~Person() {}
  utf8str_t name;
  std::vector<Feature> features;
};

std::ostream &operator<<(std::ostream &, const Person &person);
std::ostream &operator<<(std::ostream &, const FaceFeature &v);
std::ostream &operator<<(std::ostream &, const Size &v);
std::ostream &operator<<(std::ostream &, const Colour &v);

struct OutOfNamesException {
};

struct PersonFactory {
  virtual ~PersonFactory() {}
  virtual Person create() = 0;
};

std::unique_ptr<PersonFactory> RandomPersonFactory(optional<uint32_t> seed
                                                   = {});

Names_t names();
}

// ...
