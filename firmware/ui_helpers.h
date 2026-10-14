// Helpers for the P4 UI v2 (docs/ui-v2): Italian number formatting and
// on-device autonomy estimates from an hourly history ring buffer.
#pragma once
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <string>

namespace ui {

constexpr int HN = 72;             // hours of history (also the 3-day chart)
constexpr uint8_t NODATA = 255;
using Hist = std::array<uint8_t, HN>;

// "21,4" style formatting; NAN -> "--"
inline std::string fmt(float v, int decimals, const char *suffix = "") {
  if (std::isnan(v)) return std::string("--") + suffix;
  char b[24];
  snprintf(b, sizeof b, decimals == 0 ? "%.0f%s" : (decimals == 1 ? "%.1f%s" : "%.2f%s"), v, suffix);
  for (char *p = b; *p; p++)
    if (*p == '.') *p = ',';
  return b;
}

// Sample i hours ago (0 = newest). head = next slot to write.
inline uint8_t at(const Hist &h, int head, int i) { return h[((head - 1 - i) % HN + HN) % HN]; }

inline void push(Hist &h, int head, float pct) {
  h[head % HN] = std::isnan(pct) ? NODATA : (uint8_t) std::lround(std::fmax(0.0f, std::fmin(100.0f, pct)));
}

// Consumption rate in %/hour over the last 24 h, restarting after a refill
// or recharge (a rise > 8 points between two samples). Returns NAN when
// there is not enough data (< 6 h), 0 when nothing is being consumed.
inline float rate_per_hour(const Hist &h, int head, float now_pct) {
  if (std::isnan(now_pct)) return NAN;
  int oldest = -1;
  uint8_t newer = NODATA;
  for (int i = 0; i < 24; i++) {
    uint8_t v = at(h, head, i);
    if (v == NODATA) continue;
    if (newer != NODATA && (int) newer - (int) v > 8) break;  // refill between i and newer
    oldest = i;
    newer = v;
  }
  if (oldest < 6) return NAN;
  float span = oldest + 0.5f;
  float r = ((float) at(h, head, oldest) - now_pct) / span;
  return r > 0.05f ? r : 0.0f;
}

// Hours until pct reaches floor_pct. NAN = unknown, INFINITY = not consuming.
inline float hours_left(const Hist &h, int head, float now_pct, float floor_pct) {
  float r = rate_per_hour(h, head, now_pct);
  if (std::isnan(r)) return NAN;
  if (r == 0.0f) return INFINITY;
  return std::fmax(0.0f, (now_pct - floor_pct) / r);
}

// "~1,5 g", "~5 h", "> 7 g", "--"
inline std::string short_left(float hours) {
  if (std::isnan(hours)) return "--";
  if (std::isinf(hours) || hours > 24 * 7) return "> 7 g";
  if (hours < 24) return "~" + fmt(std::fmax(1.0f, std::round(hours)), 0, " h");
  return "~" + fmt(std::round(hours / 12.0f) / 2.0f, std::fmod(std::round(hours / 12.0f), 2.0f) == 0 ? 0 : 1, " g");
}

// "circa 1 giorno e mezzo" (rounded on purpose: it is an estimate)
inline std::string long_left(float hours) {
  if (std::isnan(hours)) return "stima non disponibile";
  if (std::isinf(hours) || hours > 24 * 7) return "più di una settimana";
  if (hours < 24) {
    int h = std::max(1, (int) std::lround(hours));
    return "circa " + std::to_string(h) + (h == 1 ? " ora" : " ore");
  }
  int halves = (int) std::lround(hours / 12.0f);
  int d = halves / 2;
  bool half = halves % 2;
  std::string s = "circa " + std::to_string(d) + (d == 1 ? " giorno" : " giorni");
  return half ? s + " e mezzo" : s;
}

}  // namespace ui

// LVGL helpers (only when compiled inside the ESPHome build, where lvgl.h is in)
#ifdef LVGL_VERSION_MAJOR
namespace ui {
constexpr uint32_t GREEN = 0x34C759, AMBER = 0xF0A500, RED = 0xFF5A4E, BLUE = 0x5AA9E6,
                   ACCENT = 0xE8845C, GREY = 0x8A909A;
inline void text(lv_obj_t *o, const std::string &s) { lv_label_set_text(o, s.c_str()); }
inline void color(lv_obj_t *o, uint32_t c) { lv_obj_set_style_text_color(o, lv_color_hex(c), 0); }
// back to the theme colour coming from the shared styles
inline void theme_color(lv_obj_t *o) { lv_obj_remove_local_style_prop(o, LV_STYLE_TEXT_COLOR, 0); }
inline void checked(lv_obj_t *o, bool on) {
  if (on) lv_obj_add_state(o, LV_STATE_CHECKED); else lv_obj_remove_state(o, LV_STATE_CHECKED);
}
inline void hidden(lv_obj_t *o, bool h) {
  if (h) lv_obj_add_flag(o, LV_OBJ_FLAG_HIDDEN); else lv_obj_remove_flag(o, LV_OBJ_FLAG_HIDDEN);
}
}  // namespace ui
#endif
