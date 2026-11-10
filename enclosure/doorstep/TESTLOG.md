# Doorstep test log

One line per print on the Bambu X2D (white body and front, orange drum and pin). Each print gets a `doorstep-print-N` tag on the commit it was printed from.
Prints 1-3 were matched to commits afterwards. Drum-only reprints are not counted.

Note: the replayed commits before 2026-11-10 19:00 UTC carry UTC clock times wrongly labelled -0700. Subtract 8 hours (7 in October) for Pacific time; the dates below are already Pacific.

| Tag | Date (Pacific) | Commit | Worked | Didn't work |
|---|---|---|---|---|
| doorstep-print-1 | 2026-11-05/06 | `d515d98` Corner snap arms | Overall shape | Board fell back into the shell (shelves printed as floating overhangs); drum and wheel could not be assembled; front plate too loose (not sure) |
| doorstep-print-2 | 2026-11-09 | `f99f9fc` Drum on a separate pin | End stops; drum goes in through the window | USB-C hole half filled by a gusset; front bowed out with the panel in; pin would not enter the post. Drum test: hub missed the wheel by ~0.8 mm, ~0.5 mm side play, drum slid along the pin, pressing moved the board |
| doorstep-print-3 | 2026-11-09 | `d340d7d` Springy drum mount | "Performing much better"; drum held on the wheel | Drum dragged on the pin, so turning clicked the button; plain PLA hub only drove the wheel when pressed; front bumps lifted the plate at the bottom, seams uneven; button pillars weak; needle through two holes; wheel window too wide. Drop test: plate and panel popped out; panel gives when plugging in USB |
| doorstep-print-4 | 2026-11-09 night | `1c2e20c` Board lock, plate pads removed (to confirm) | (feedback pending) | (feedback pending) |

## Tags
The cloud session can't push tags, so they live here until someone runs this once from a checkout:

```sh
git fetch origin
for p in 1:d515d98 2:f99f9fc 3:d340d7d 4:1c2e20c; do
  git tag -a doorstep-print-${p%%:*} ${p#*:} -m "Doorstep print ${p%%:*}"; done
git push origin --tags
```
