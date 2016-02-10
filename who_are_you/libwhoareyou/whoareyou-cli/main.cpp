//
// main.cpp
//

#include <iostream>
#include "people.h"

using namespace std;

int main()
{
  using namespace whoareyou;
  auto f = RandomPersonFactory();
  std::cout << f->create() << std::endl;
  std::cout << f->create() << std::endl;
  std::cout << f->create() << std::endl;
  std::cout << f->create() << std::endl;
  return 0;
}
