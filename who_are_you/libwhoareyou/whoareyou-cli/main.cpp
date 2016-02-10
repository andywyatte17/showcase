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
  std::cout << f->create();
  return 0;
}
