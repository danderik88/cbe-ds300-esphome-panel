// Self-check for firmware/ui_helpers.h: c++ -std=c++17 tools/test_ui_helpers.cpp -o /tmp/t && /tmp/t
#include "../firmware/ui_helpers.h"
#include <cassert>
#include <cstdio>
using namespace ui;

int main() {
  assert(fmt(21.44f, 1, "°") == "21,4°");
  assert(fmt(NAN, 0, "%") == "--%");
  Hist h; h.fill(NODATA); int head = 0;
  // 12 hours of 2 %/h drain, 80 -> 58
  for (int i = 0; i < 12; i++) push(h, head++, 80 - 2 * i);
  float now = 56;
  float r = rate_per_hour(h, head, now);
  assert(r > 1.9f && r < 2.4f);
  float left = hours_left(h, head, now, 40);  // 16 points at ~2/h
  assert(left > 6 && left < 9);
  // refill in the middle: only the part after it counts -> not enough data
  Hist w; w.fill(NODATA); int wh = 0;
  for (int i = 0; i < 10; i++) push(w, wh++, 30 - i);
  for (int i = 0; i < 3; i++) push(w, wh++, 95 - i);
  assert(std::isnan(rate_per_hour(w, wh, 92)));
  // no consumption -> infinite
  Hist f; f.fill(NODATA); int fh = 0;
  for (int i = 0; i < 10; i++) push(f, fh++, 70);
  assert(std::isinf(hours_left(f, fh, 70, 0)));
  assert(short_left(INFINITY) == "> 7 g");
  assert(short_left(36) == "~1,5 g");
  assert(short_left(48) == "~2 g");
  assert(short_left(5.2f) == "~5 h");
  assert(long_left(36) == "circa 1 giorno e mezzo");
  assert(long_left(72) == "circa 3 giorni");
  assert(long_left(NAN) == "stima non disponibile");
  puts("ui_helpers ok");
}
