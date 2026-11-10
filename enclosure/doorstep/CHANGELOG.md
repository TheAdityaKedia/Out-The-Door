# Doorstep changelog

Design notes per change, oldest first. `git log -- enclosure/doorstep` has one commit per saved model version.

## Clock-style case (riff on the white alarm clock, 2026-10-19)

80 x 44 x 30 mm, matte white, front leans back 6 deg, all edges soft (9 mm corners, 3 mm front, 4 mm back).
Built headless in cloud FreeCAD: `src/doorstep.py` (model + fit checks). Files: body, front_lens, orange_wheel_cap (.step/.stl, assembled position).

### Parts
- **Body**: one piece, 1.8 mm walls. Panel goes in from the front (wheel end first), then the lens closes it. No back cover, no side seam.
- **Front lens**: 1.5 mm clear acrylic, covers the whole flat front, flush; hairline seam only where the rounded edge starts.
- **Orange drum** (revised 2026-10-19): the CrowPanel wheel sits inside a housing; only a 2.7 mm sliver of its rim sticks out past the board end, so nothing can clip onto it. Instead an orange part (r 4 hub + 18 mm knurled drum + 3 mm axle) rides on a post moulded on the back wall. The hub presses on the wheel's exposed rim (0.2 mm preload; add an O-ring or TPU tyre for grip), so turning the drum turns the wheel (opposite direction: flip it in firmware). The post hole is slotted 1.2 mm toward the wheel, so pushing the drum in clicks the wheel. Drum juts 3.7 mm out of the right side. See wheel_drive.png.
- **MENU/EXIT**: two 1.6 mm pin holes in the right end (rarely used).
- **USB-C**: tunnel through the base + cable groove to the back, so it stands flat and the port is hidden.
- **Battery**: fits a 40 x 30 x 10 mm cell (103040, ~1500 mAh) beside the drum; the 50 x 35 mm 2000 mAh cell does not fit this size.
- Fit checks: no clashes between panel, battery, cap and body (cap intentionally overlaps the wheel by 0.5 mm3 = the grip).

### Making the front read as one surface (e-paper has no light, so it must match by reflection)
1. **Back-painted clear lens (recommended)**: 1-1.5 mm acrylic or glass, screen-printed / spray-masked on the back in the e-paper's own grey-white, clear only over the active area. Match paint to the panel's white (warm light grey ~#D8D8D2, test a few chips). Laminate the lens to the panel with OCA or keep the gap < 0.2 mm so there is no parallax shadow. Add an anti-glare matte finish (etched AG glass or matte film over everything) so paint and screen share one sheen.
2. **Matte film only**: a printed vinyl/PET overlay with a window, plus one continuous matte clear film over the whole face. Cheapest, prototype tonight; edge shows a little.
3. **IMD / in-mould decoration** (production): the white face and window are printed inside a molded clear PC front. Same result as 1, scaled.
4. **Firmware helps**: keep text off the outer 1-2 mm of the active area, use a white background with no borders, and set the panel border to white so nothing outlines the screen.
Avoid: tinted/smoked "dead front" (needs a backlight; e-paper would go dark) and frosted diffusers (blur the text because the pixels sit ~1 mm behind).

## Fallback: sloped bezel version (bezel/, 2026-10-19)
Same body and orange drum, no acrylic lens, 30 mm deep. The whole flat front rolls inward in one continuous convex curve (screen 2.0 mm behind the face; set FRONT in clock_bezel.py, 1.2-3.5 all fit, see screen_depth_options.png) from the edge fillet down to a window 0.3 mm inside the active area, symmetric left-right. Split into front_lid + back_shell 5.5 mm behind the face (one seam line around the sides). The panel goes in from the back of the lid. Files: bezel/front_lid, back_shell, orange_drum (.step/.stl), bezel_renders.png.
Fix applied to both versions: the drum's axle hole in the back post is now blind (it used to poke through the back).

## One body, two fronts (2026-10-21)
body.step now has a 2 mm front pocket that takes either front:
- **A: front_lens** — 2 mm clear cast acrylic, back-painted e-paper white with a window.
- **B: front_bevel** — 2 mm printed insert, same outline; its face rolls inward in one convex curve from the seam to a window 0.3 mm inside the active area. Symmetric.
The screen sits in the same place for both (glass 0.1 mm behind the insert). Panel goes in from the front, then the front presses in (friction, a dab of glue, or small magnets). No lid/shell split. bezel/ folder is the older split-lid take, superseded. Renders: two_fronts_one_body.png.

## Board retention + front bumps (2026-10-21)
- CrowPanel drops in from the front onto 2 posts (far end, flat tops on the corner pads) and 2 ribs (wheel end) that grow from the back wall. The front piece then clamps it: board is sandwiched, no glue. (The STEP has no corner holes modelled, so no locating pins.)
- front_bevel has 4 friction ridges (top/bottom edges, 0.25 mm proud, ~0.15 mm interference). front_lens: thin VHB tape or a dab of clear silicone at the rim.
- Battery moved to the left (x -29) to clear the posts. Cutaway: board_supports.png.

## Corner snaps (2026-10-22) — replaces the posts/ribs above
- 4 springy arms (1.2 mm thick, ~9.6 mm long, rooted on the top/bottom walls) near the board corners. Each has a 0.6 mm hook that clicks over the 1 mm bare rim on the board's front face; a small shelf beside each arm sits under the board's back. Board pushes in from the front, then the front piece goes on.
- To remove the board: with the front off, push the arms outward with a fingernail.
- Diagram: corner_snaps.png. Old posts version kept as scratch only.

## Names (2026-10-27)
- **Doorstep**: the clock body (body.step). Fronts: **Doorstep Glass** (front_lens, painted acrylic) and **Doorstep Slope** (front_bevel). Orange drum: **the Latch**.
- **Threshold**: the retired split lid/shell bezel version (bezel/).

## v2 fixes after first X2D print (2026-11-06)
- Board fell back into the shell: the 4 small shelves were 5.6 mm cantilevers that print as floating overhangs (back-down). Replaced with long ledges along both long walls (1 mm under the board's back edge, notched around parts), each with a 45 deg gusset to the wall so they print without supports.
- Slope front friction: ridges now 0.45 mm proud (0.35 mm interference, was 0.15) and 2 more ridges on the short ends.
- Print-ready plate regenerated: print-ready/doorstep_slope_plate.3mf.
- End stops (2026-11-06): ribs from the back wall touch both short edges of the board (0.15 mm gap). Far end: two corner ribs (|z| 10.5-14.5) leaving the middle open for the panel FPC that wraps round that end; wheel end: two ribs beside the wheel housing that touch only the PCB edge, in front of the MENU/BACK plungers (pin holes re-opened). No clashes with the CrowPanel.
- Drum assembly fix (2026-11-09): the one-piece drum+axle could not be fitted (drum has to pass the wall in front of the slot). Now: straight-sided 19 mm window through the right wall; drum (with hub) has a 3.5 mm bore and is passed in edge-first from outside; a separate 3 mm pin (latch_pin, or a 3 x 19 mm steel dowel) is pushed in from the front through the drum into a 2.9 mm press-fit hole in the post. Do this before fitting the CrowPanel. Drum now prints flat-face-down with no supports.
- Test-print fixes (2026-11-10): (1) USB-C hole was half filled by the bottom ledge's gusset; tunnel + groove now re-cut after the supports. (2) Front bowed out with the panel in: glass sat only 0.1 mm behind the front plate; whole board mount (hooks, ledges, stops, drum, USB, pin holes) moved 0.6 mm deeper -> 0.7 mm gap. Front plate unchanged. (3) Pin would not enter the post: hole 2.9 -> 3.2 mm (prints undersize, gives a snug push fit).

## Springy drum mount (2026-11-10, after drum test on the end-stop shell)
- Adi's test: hub missed the wheel by ~0.8 mm, board side play ~0.5 mm (tolerance), drum slid along its pin, pressing moved the board.
- Axle now 1.85 mm (nominal) into the wheel, on a boss hung from the top wall by a 22 x 5 x 1.2 mm arm that flexes sideways (~1.3 N preload, ~0.7% strain at full deflection, 1.78 mm room to the side wall). The spring holds the hub on the wheel and pushes the board against the far end stops; pressing the drum bends it further and clicks the button.
- Boss sits 0.2 mm behind the drum and the pin has a 4 mm x 0.7 mm head in front, so the drum can't slide along the pin. Drum bore 3.3 mm (turns freely). Far end-stop gap 0.05 mm.
- Pin prints standing head-down. Reprint body, drum, pin; the front is unchanged.

## Free-spinning drum (2026-11-10, second test on new shell)
- Adi: the drum dragged on the pin, so turning it needed pressure, which clicked the wheel button.
- Drum bore 3.3 -> 3.6 mm; boss gap behind drum 0.2 -> 0.3 mm; the post hole is 0.5 mm shallower so the pin bottoms out with its head 0.3 mm off the drum (pushing the pin fully home can no longer clamp the drum). Reprint drum and body only (pin unchanged).
- Rubber tyre on the hub (2026-11-10): plain PLA hub only drove the wheel when pressed. Hub now has a groove (floor 5.7 mm dia, 1.1 mm wide, open at the front; back flange 6.6 mm dia) for a 6 mm ID x 1 mm cross-section nitrile O-ring; only the rubber (about 7.6 mm OD) touches the wheel. Buy: 6x1 mm NBR 70A O-rings. Reprint the drum only.

## Continuous lip, button tabs, smaller wheel window (2026-11-10, after third shell print)
- Front plate: bumps removed. Body now has a seat ledge round the mouth 2 mm behind the face (45 deg chamfer under it) so the plate always sits flush, with a continuous 0.8 x 0.95 mm tongue on the seat. Plate has a matching 1.0 x 1.0 mm groove in its back (0.5 mm in from its edge). Seat and tongue are notched where the pin goes in from the front. The acrylic lens option has no groove yet.
- Wheel end: end stops are now solid blocks tied into the side wall, pillars thickened (2.2 mm) with gussets at the back wall. Each button has a 0.8 mm press tab (free at the front, 1 mm gap behind) with a ramped nub 0.08 mm off the plunger tip; one straight 1.6 mm bore from outside reaches the tab, so a pin only has to go through one hole.
- Wheel window: 6.3 x 18 mm for the drum plus a 2 x 9 mm notch in front for the hub (was 8.4 x 19.2). The drum no longer fits through edge-first: drop it in through the front (keep it to the left), then slide it right so its rim comes out of the window, then push the pin in.
- Revised same day (Adi): lip moved to the plate (0.8 x 0.95 mm, flush with its outer edge) and a 1.0 x 1.0 mm groove cut into the body's seat, so a flat 2 mm acrylic lens can also sit on the seat (hold it with a thin tape ring). The plate now prints back-down on its lip and needs tree supports under its hidden back. Screen window flush with the live area (48.54 x 23.70). Hub notch is now a blind pocket inside the wall (0.45 mm skin), so only the 6.3 x 18 drum slot shows. USB: plain 10.5 x 7.5 mm opening for a straight plug from below; cable groove removed. Seat chamfer is cut back where the corner snap arms flex.

## Bigger drum (2026-11-10)
- Drum 18 -> 24 mm dia (80 knurls), sits 1.4 mm deeper (y 9.2-14.5, behind the CrowPanel wheel housing) on a longer 6 mm spacer; same hub/O-ring and axle position, so it pops out 5.1 mm instead of 2.1. Side slot 6.3 x 24.2 mm. Wheel-end blocks and press tabs are cleared where the drum sits and along the path it slides in on (tabs keep their nub; their upper part is narrower). Pin now 17 mm. Assembly: drop the drum in on the left, slide it right until the rim pokes out, then push the pin in. Reprint body, drum, pin.

## Board lock (2026-11-10, after drop test + USB wiggle)
- 7 rigid edge stops from the top/bottom walls, 0.1 mm off the board's long edges (in front of the ledges): above the USB, either side of the USB opening, and at x -20 / +15. USB push now meets solid wall.
- 4 leaf springs: 0.5 mm cantilevers (4-4.5 mm long) cut into the long ledges in gaps between the board's back-side parts, bump 0.3 mm proud of the board back, pushing it forward onto the corner hooks.
- 8 pads on the front plate's back, 0.05 mm off the board's bare top/bottom rim (not the glass), so the board can't come forward in a drop while the plate is on. The plate now prints standing on these pads: use tree supports.
- Manufacturing note: for molding or a metal shell, move these inner features into a separate plastic inner frame.
- Plate pads removed (2026-11-10): they printed first as tiny islands and wrecked the plate print; Adi sees no front-back wiggle without them. Plate prints standing on its lip ring with tree supports.
