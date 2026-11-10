# Doorstep test log

One line per print on the Bambu X2D (white body and front, orange drum and pin). Each print gets a `doorstep-print-N` tag on the commit it was printed from.
Rows marked **(?)** were matched to a commit after the fact from notes and file times. Correct them if your memory differs.

| Tag | Date | Commit | Printed | Worked | Didn't work |
|---|---|---|---|---|---|
| doorstep-print-1 | 2026-11-05 | `d515d98` Corner snap arms | body, Slope front, drum | Overall shape, snap arms | Board fell back into the shell (shelves printed as floating overhangs); front plate too loose |
| doorstep-print-2 **(?)** | 2026-11-06 | `7daff15` v2 fixes | body, front, drum | Board held by the long ledges | One-piece drum and axle could not be fitted past the wall |
| doorstep-print-3 **(?)** | 2026-11-09 | `f99f9fc` Drum on a separate pin | body, front, drum, pin | End stops, drum goes in through the window | USB-C hole half filled by a gusset; front bowed out with the panel in; pin would not enter the post |
| doorstep-print-4 **(?)** | 2026-11-10 | `5e7d310` Fixes from the second test print | body, drum, pin | USB lines up; front sits flat | Hub missed the wheel by ~0.8 mm; ~0.5 mm side play; drum slid along the pin; pressing moved the board |
| doorstep-print-5 | 2026-11-10 | `d340d7d` Springy drum mount | body, drum, pin | "Performing much better"; drum held on the wheel | Drum dragged on the pin, so turning it clicked the button; plain PLA hub only drove the wheel when pressed |
| doorstep-print-6 **(?)** | 2026-11-10 | `c1e9469` O-ring tyre on the hub | body, front, drum | O-ring drum turns the wheel | Front plate bumps lifted it at the bottom, seams uneven; button pillars weak; needle through two holes; wheel window too wide |
| doorstep-print-7 **(?)** | 2026-11-10 | `4443e9f` Bigger drum | body, front, drum, pin | Continuous lip, press tabs, 24 mm drum | Drop test: plate and panel popped out; panel gives when plugging in USB |
| doorstep-print-8 | 2026-11-10 | `23641a8` Board lock (with plate pads) | front plate (body uncertain) | No front-back wiggle | Plate pads printed as tiny islands and ruined the plate; some up-down and slight side-to-side board wiggle remain |

Not printed yet: **Remove the plate pads** (the latest commit).

## Tags
The cloud session can't push tags, so they live here until someone runs this once from a checkout:

```sh
git fetch origin
for p in 1:d515d98 2:7daff15 3:f99f9fc 4:5e7d310 5:d340d7d 6:c1e9469 7:4443e9f 8:23641a8; do
  git tag -a doorstep-print-${p%%:*} ${p#*:} -m "Doorstep print ${p%%:*}"; done
git push origin --tags
```
