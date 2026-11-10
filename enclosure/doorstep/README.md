# Doorstep case

White clock-style case for the Elecrow CrowPanel ESP32-S3 2.13" e-paper board, with an orange side drum ("the Latch") that turns the board's wheel. Two fronts fit the same body: **Doorstep Slope** (printed bevel insert) and **Doorstep Glass** (2 mm back-painted acrylic).

| File | What it is |
|---|---|
| [REQUIREMENTS.md](REQUIREMENTS.md) | Rules every new version must meet, each from a real print problem |
| [TESTLOG.md](TESTLOG.md) | One line per print: version, what worked, what didn't |
| [CHANGELOG.md](CHANGELOG.md) | Design notes for every change |
| `src/doorstep.py` | The whole model and its fit checks (headless FreeCAD) |
| `scripts/` | Print layout, 3MF plate, renders, checks |
| `models/` | Parts in assembled position (STEP + STL) |
| `print-ready/` | Parts laid flat for printing, plus `doorstep_slope_plate.3mf` (one X2D plate) |
| `docs/` | Assembly guide and preview images |

Versions that were printed are tagged `doorstep-print-N` (`git tag -l 'doorstep-*'`). Print files are committed only for the current version; check out a tag and rebuild to get an older one.

## Printing
Open `print-ready/doorstep_slope_plate.3mf` in Bambu Studio. Body and front in white, drum and pin in orange. The front prints on its lip ring with tree supports; the pin stands on its head. Buy 6 x 1 mm NBR O-rings for the drum hub (or print `latch_drum_orange_plain.stl`). Assembly: `docs/assembly_guide.png`.

## Building the model
Needs FreeCAD 1.1 (headless `freecadcmd` is enough) and the CrowPanel STEP, which is Elecrow's file and is not committed:

1. Download the 2.13" CrowPanel STEP from Elecrow's GitHub ([Elecrow-RD](https://github.com/Elecrow-RD), the CrowPanel ESP32 E-Paper HMI 2.13" repository) and save it as `vendor/crowpanel_2.13.step`, or point `CROWPANEL_STEP` at it.
2. From this folder:

```sh
freecadcmd -c "exec(open('src/doorstep.py').read())"   # model + fit checks -> models/, build/
freecadcmd -c "exec(open('scripts/orient.py').read())"  # print-ready STLs
freecadcmd -c "exec(open('scripts/mk3mf.py').read())"   # 3MF plate
```

`CHECK=1` runs the fit checks without saving; `DIAG=1` tests each support feature separately. Render scripts (`scripts/render_*.py`) need the GUI build under a virtual display: `xvfb-run -a freecad scripts/render_assembly.py`, then `python scripts/compose_assembly_guide.py`.

Coordinates in `src/doorstep.py`: front face at y = 0, y grows toward the back, z up, x positive at the wheel end.
