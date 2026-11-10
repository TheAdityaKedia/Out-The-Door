# Enclosure development

How we design, version, print and test cases. Each case lives in its own folder (`doorstep/` is the first). These rules apply to all of them.

## Folder layout (per case)

| Path | What goes there |
|---|---|
| `src/<case>.py` | The whole model and its fit checks, as a headless FreeCAD script |
| `scripts/` | Print layout (`orient.py`), 3MF plate (`mk3mf.py`), renders, checks |
| `print-ready/` | One STL per printable part, laid flat for the bed, plus the 3MF plate |
| `models/` | Parts in assembled position, STEP only |
| `renders/` | One before/after image per part revision |
| `parts.md` | Index of every part revision |
| `prints/` | Print log: `Pnn.md` per print, photos in `Pnn/` |
| `assemblies/` | Assembly log: `Ann.md` per build, photos in `Ann/` |
| `REQUIREMENTS.md` | Rules every new version must meet, each from a real print problem |
| `CHANGELOG.md` | Design notes for each model change |
| `docs/` | Assembly guide, preview images |
| `vendor/`, `build/` | Git-ignored: third-party STEP files and intermediate files |

## Part revisions
- Each printable part (body, front, drum, pin, ...) has its own revision number: `body-4`, `drum-3`.
- A part's number goes up only when its STL actually changes. A model edit usually touches one or two parts, so the others keep their number.
- Model versions that are never exported as an STL revision get no number.

## Commits
- **STL commits**: one STL per commit, titled `stl: <part>-<n> (what changed)`. The body names the model commit it came from. The same commit adds:
  - the updated file in `print-ready/`;
  - `renders/<part>-<n>.png`, showing the previous revision above the new one (`scripts/render_stl.py`, then `scripts/compose_revision.py`);
  - a row in `parts.md`.
- **Every other commit** (model, scripts, docs, logs) is free-form, but should not change any STL in `print-ready/`.
- Find a revision by name: `git log --grep "stl: drum-2"`. Get its file: `git show <commit>:enclosure/<case>/print-ready/<file>`.
- No git tags: the cloud sessions can't push them, and the `stl:` titles plus `parts.md` do the same job.

## Print log (`prints/Pnn.md`)
One file per print job, numbered P1, P2, ... in order. Each one records:
- date (Pacific time) and the printer;
- every part on the plate: revision, filament/colour, slicer settings (layer height, walls, infill, supports, orientation), and how it came out;
- print problems (failed parts, stringing, warping, a print abandoned partway);
- Adi's photos in `prints/Pnn/`, embedded in the page.

Add a row to `prints/README.md` too.

## Assembly log (`assemblies/Ann.md`)
One file per build, numbered A1, A2, ... A build can mix parts from several prints. Each one records:
- the parts used, as `body-3 (P3) + drum-2 (P2) + ...`;
- what worked, what didn't, and how it felt in the hand;
- photos in `assemblies/Ann/`, embedded;
- links to videos in Google Drive.

Add a row to `assemblies/README.md` too. A problem a build shows that any future version must avoid also goes into `REQUIREMENTS.md`.

## Photos and videos
- Adi posts photos and videos in the project thread, and Claude files them.
- Photos are committed after shrinking to about 1600 px on the long side and stripping location data (EXIF), because the repo is public.
- Videos are not committed. They go in Google Drive, in `Out the Door/<case>/Ann/` (Doorstep: https://drive.google.com/drive/folders/1XHWbFbfmchYWIL0dIsVOEYYHbMrPAYiV), and the assembly page links to them. If a video is too big to upload from the cloud, it stays in the project files and is linked from there.

## Third-party files
Vendor CAD (for example Elecrow's CrowPanel STEP) is not committed. It goes in the git-ignored `vendor/` folder, and the case README says where to download it.

## Building and checking
From the case folder, with FreeCAD 1.1:

```sh
freecadcmd -c "exec(open('src/<case>.py').read())"     # model + fit checks -> models/, build/
freecadcmd -c "exec(open('scripts/orient.py').read())"  # print-ready STLs
freecadcmd -c "exec(open('scripts/mk3mf.py').read())"   # 3MF plate
RSTL=print-ready/<file>.stl ROUT=build/r_<part>-<n> xvfb-run -a freecadcmd -c "exec(open('scripts/render_stl.py').read())"
```

- `CHECK=1` runs the fit checks without saving.
- Before an STL commit, read the fit-check output: there should be no clashes, and every opening should be re-checked after the supports are added.
- Printed holes on the X2D come out about 0.2-0.3 mm small; size for that.

## Times
Adi is in Pacific time; the cloud containers run on UTC. Logs use Pacific dates. Doorstep model commits made before 2026-11-10 19:00 UTC show UTC clock times wrongly labelled -0700.
