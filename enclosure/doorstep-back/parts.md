# Part revisions

Same rules as [Doorstep](../doorstep/parts.md): each part has its own number, bumped only when its STL changes, one `stl: <part>-<n> (...)` commit per revision. Doorstep-back numbers are separate from Doorstep's.

| Part | File |
|---|---|
| body | `print-ready/doorstep_back_body_white.stl` |
| cap | `print-ready/doorstep_back_cap_white.stl` |
| drum | `print-ready/latch_drum_orange.stl` |
| pin | `print-ready/latch_pin_orange.stl` |

| Revision | Commit | Model commit | What changed | Printed in | Render |
|---|---|---|---|---|---|
| body-1 | `e9b0567` | `5a48217` | One piece with a bevelled front; board loads from the back onto front pads, 4 snap arms | | [png](renders/body-1.png) |
