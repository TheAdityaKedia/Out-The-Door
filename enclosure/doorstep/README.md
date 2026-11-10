# Doorstep case

White clock-style case for the Elecrow CrowPanel ESP32-S3 2.13" e-paper board, with an orange side drum ("the Latch") that turns the board's wheel. Two fronts fit the same body: **Doorstep Slope** (printed bevel insert) and **Doorstep Glass** (2 mm back-painted acrylic).

| File | What it is |
|---|---|
| [REQUIREMENTS.md](REQUIREMENTS.md) | Rules every new version must meet, each from a real print problem |
| [parts.md](parts.md) | Every part revision (body-4, drum-2, ...) and its commit |
| [prints/](prints/README.md) | Print log: one file per print, parts and settings |
| [assemblies/](assemblies/README.md) | Assembly log: which parts went together and how it went |
| [CHANGELOG.md](CHANGELOG.md) | Design notes for every change |
| `src/doorstep.py` | The whole model and its fit checks (headless FreeCAD) |
| `scripts/` | Print layout, 3MF plate, renders, checks |
| `models/` | Parts in assembled position (STEP) |
| `print-ready/` | Parts laid flat for printing, plus `doorstep_slope_plate.3mf` (one X2D plate) |
| `docs/` | Assembly guide and preview images |

## Conventions
- An STL change is its own commit, one STL per commit, titled `stl: <part>-<n> (what changed)`, with a row added to `parts.md` and a before/after render in `renders/<part>-<n>.png` in the same commit (`scripts/render_stl.py` + `scripts/compose_revision.py`). Numbers go up per part, only when that part's STL changes.
- Every other commit (model, scripts, docs) is free-form.
- After each print add `prints/Pnn.md` with Adi's photos in `prints/Pnn/`; after each build add `assemblies/Ann.md` with photos in `assemblies/Ann/`. Photos are shrunk to ~1600 px with location data stripped (public repo). Videos go in Google Drive (Out the Door/doorstep, https://drive.google.com/drive/folders/1XHWbFbfmchYWIL0dIsVOEYYHbMrPAYiV, one subfolder per assembly) and are linked from the assembly page, not committed.
- Note: model commits before 2026-11-10 19:00 UTC show UTC clock times labelled -0700.

## Printing
Open `print-ready/doorstep_slope_plate.3mf` in Bambu Studio. Body and front in white, drum and pin in orange. The front prints on its lip ring with tree supports; the pin stands on its head. Assembly: `docs/assembly_guide.png`.

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
