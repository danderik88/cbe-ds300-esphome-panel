# Contributing

Reports from other campers with a CBE DS-300 are very welcome: a pin that works the same, one that differs, or a signal this repo leaves out (fresh-water levels on pins 2/7/8, OUT D+ on pin 5, mains present on pin 10, grey tank 1/3 on pin 13).

## Reporting a pin or a probe

1. **Measure** with the old panel unplugged and the van on its service battery. Start with **12.7 V between pin 15 and pin 3**: it proves the plug orientation.
2. **Change one thing at a time** and write down what you saw (relay click, light on, voltage).
3. **Open an issue** with the "Report from your camper" template, or a pull request that updates the README table and the pinout picture.

Please include your camper model and year, the DS-300 variant and the original panel model. Only verified findings are merged.

## Firmware changes

- Keep the screen labels in Italian, code identifiers in English.
- Run `esphome config firmware/panel-p4.yaml` (and `compile` if you touch C++ lambdas) before opening a pull request.
- `c++ -std=c++17 tools/test_ui_helpers.cpp -o /tmp/t && /tmp/t` must print `ui_helpers ok`.

## Please don't

- Don't post photos with your number plate, GPS position, network names or passwords.
- Don't post scans of the CBE manuals: link to the source instead.
- Don't submit pinouts you have not measured on a real vehicle.
