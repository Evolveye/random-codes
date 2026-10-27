# Engine reference (`scripts/ee_sprite.py`)

A character's `generator.py` adds the scripts folder to `sys.path`, imports the engine, defines the names below and ends
with `run( globals() )`. Start from `templates/generator.py`.

## What generator.py defines

| Name | Meaning |
|---|---|
| `CANVAS` | `Canvas( margin_x=3, top=1, bottom=3 )`: frame = 25 + 2·margin_x wide, top + 25 + bottom tall. Raise `top` for tall hats, `bottom` for long legs, `margin_x` for wide items. Side margins are equal so the mirror fits. |
| `HEAD` | `Material` of the face fill, usually `Material( GOLD, light=( 8, 5 ), step=4.6 )`. Its `ring` RGB tints the light ring (white when None). A variant's options may hold `"head"` to use another head material. Its `border( column, row, kind )` restyles the head's black and ring pixels: None keeps one, `"fill"` makes it face fill, an RGB recolours it, `"clear"` removes it (a smaller head), `"edge"` makes it face fill that turns black only where nothing is drawn outside it. |
| `parts( facing, options )` | Returns a list of `Part` and `Wisp`, authored facing right. `options` is a dict from `VARIANTS`/`FINAL`; `facing` lets the left side use another layout. |
| `VARIANTS` | `{ "1_name":{ options }, … }`: numbered tries. Only add; changing old entries changes outputs the user compared. |
| `FINAL` | The options dict that `export` uses. |
| `ANIMATIONS` | `{ "idle":Animation(…), "walk":Animation(…) }`. Order = spritesheet row order; idle first. |

## Coordinates
Head coordinates: the head circle spans columns and rows 0..24; negative values or values above 24 reach into the
margins. Canvas point = ( margin_x + column, top + row ). Everything is authored facing right; the left sprite is
mirrored around the head centre and then shaded, so light stays top-left.

## Materials
`Material( ramp, shading="radial", level=0, step=2.0, light=None, contour=None )`
- `radial`: `ramp[ level + distance // step ]` from `light` (head coordinates) or, if None, from a point 30% into the
  part's bounding box — good for round skin parts.
- `flat`: `ramp[ level ]` — eyes, mouths, flat details.
- `edge`: `ramp[ level − 1 ]` on the top/left rim, `ramp[ level + 1 ]` on the bottom/right rim — cloth, hats, items.
- `rows`: one ramp step per row from the part's top — capes, drips, gradients done in steps.
- `contour`: the line drawn where the part meets other parts; default is the ramp's darkest colour × 0.62.
- Helpers: `GOLD`, `EYE_BLACK`, `make_ramp( rgb )` (5 tones, light to dark).

## Parts
`Part( name, grid, at, palette, depth="front", outline=True, states={} )`
- `grid`: list of strings, `.` = empty, other symbols looked up in `palette` (symbol → Material). One part can mix
  materials (e.g. a hat with a band).
- `at`: head coordinates of the grid's top-left.
- `depth`: `face` (painted only inside the face: eyes, mouth, bands, face paint; no outline), `behind` (clipped by
  the head: feet, far hand, tails, backpacks), `front` (over the head: hands, held items, hats, scarves).
  Parts are drawn in list order within a depth.
- `outline=False` for things that shouldn't get a black edge (e.g. a glow); an RGB/RGBA colour, or a function
  `( column, row ) -> colour | None` in head coordinates, gives coloured or dotted edges. Variant option
  `"animations":{ name:Animation }` gives a variant its own animations instead of the character's `ANIMATIONS`
  (previews and export). `"open_gaps":True` skips the black gap fill (needed with dotted edges). `Material( …, alpha=190 )` makes a
  semi-transparent material. `edges=False` draws no outline or contour at all, for loose pixels (sparks, evaporating
  embers) laid over whatever is there; their states are picked per frame like any part.
- `states`: alternative grids, e.g. `{ "closed":… }` for a blink, picked by `Frame.states`.
- `blob( { row:( first, last ) } )` builds a grid from consecutive row spans.

## Effects
`Wisp( anchor, path, alpha=238 )`: steam/smoke rising along `path` (bottom to top, head coordinates), moving with the
part named `anchor`. A frame with `phase=None` draws the plain path (stills); phases animate the rise.

## Frames and animations
`Frame( offsets={}, states={}, bob=0, phase=None )`, `Animation( frames, ms=140, frames_left=None )`,
`blink( frames, part, state="closed", at=5 )`. See `animation.md`.

## Commands (`python <name>/generator.py <command>`)
- `still <variant> [right|left]`: one proposal into `_work/`: the still, its preview and `<variant>_<facing>_view.png`
  (enlarged plus 1× and 2× copies). Stages 1 and 2.
- `variants [right|left|both]`: every variant's stills and previews plus `compare.png` side by side (default right).
- `preview <variant> [animation …]`: animation GIFs of that variant into `_work/`, only the named ones if given
  (`idle` in stage 3, the move animation in stage 4).
- `export <stage>`: writes one approved stage of `FINAL` next to `generator.py`: `look` (right still and preview),
  `directions` (left still and preview), `idle` (idle GIFs and an idle-only spritesheet), `move` (all animation GIFs and
  the full spritesheet). `export` without a stage (also what a bare run does) re-exports every stage — only use it when
  all stages are approved.
- `diff <png> [variant] [right|left]`: lists pixels where a PNG differs from the render, in head coordinates.
- `clean`: deletes `_work/`.

## Extending
Add new shading modes, effects or frame fields to the engine with defaults that keep current behaviour, then
re-export the existing characters and check their files are byte-identical.
