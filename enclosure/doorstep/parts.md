# Part revisions

Each printable part gets its own number, bumped only when its STL changes. Every revision is one commit titled `stl: <part>-<n> (...)` that changes only that STL in `print-ready/`. To find one: `git log --grep "stl: drum-2"`. Its render (before/after the previous revision) is `renders/<part>-<n>.png`, added in the same commit from now on. To get the file: `git show <commit>:enclosure/doorstep/print-ready/<file>`.

| Part | File |
|---|---|
| body | `print-ready/doorstep_body_white.stl` |
| front | `print-ready/doorstep_slope_front_white.stl` (Slope) |
| drum | `print-ready/latch_drum_orange.stl` |
| pin | `print-ready/latch_pin_orange.stl` |

| Revision | Commit | Model commit | What changed | Printed in | Render |
|---|---|---|---|---|---|
| body-1 | `5563e61` | `d515d98` | Corner snap arms, small shelves | P1 | [png](renders/body-1.png) |
| body-2 | `c9a60e5` | `f99f9fc` | Long gusseted ledges, end stops, straight drum window, pin post | P2 | [png](renders/body-2.png) |
| body-3 | `4227a07` | `d340d7d` | USB re-cut, board mount 0.6 mm deeper, springy drum arm | P3 | [png](renders/body-3.png) |
| body-4 | `c2b81ba` | `23641a8` | Seat + groove for the plate lip, press tabs, gussets, 24 mm drum slot, edge stops + leaf springs | P5 | [png](renders/body-4.png) |
| front-1 | `ed0c579` | `d515d98` | 4 friction ridges, 0.25 mm | P1 | [png](renders/front-1.png) |
| front-2 | `69a13b2` | `f99f9fc` | 6 ridges, 0.45 mm | P2, P3 | [png](renders/front-2.png) |
| front-3 | `e2cecd9` | `23641a8` | Continuous lip, window flush with live area, pads on the back | P4 (failed) | [png](renders/front-3.png) |
| front-4 | `737d85a` | `1c2e20c` | front-3 without the pads | P5 | [png](renders/front-4.png) |
| drum-1 | `6566892` | `d515d98` | 18 mm, one piece with its axle | P1 | [png](renders/drum-1.png) |
| drum-2 | `a8ac727` | `f99f9fc` | 18 mm, 3.5 mm bore on a separate pin | P2 | [png](renders/drum-2.png) |
| drum-3 | `599d5c8` | `166a22b` | 24 mm, plain hub, sits deeper (same shape as the `latch_drum_orange_plain.stl` made on 11-09) | P5 | [png](renders/drum-3.png) |
| pin-1 | `8a42916` | `f99f9fc` | 3 mm plain pin | P2 | [png](renders/pin-1.png) |
| pin-2 | `aecb9b9` | `1c2e20c` | 3 mm, 4 mm head, 17 mm | P5 | [png](renders/pin-2.png) |

Model versions that were never printed (for example the 24 mm O-ring drum) get no number. Older STLs were rebuilt from the model at that commit, so they match what was printed but may be laid out on the bed differently.
