---
name: ee-character
description: Create Everybody Edits (EE) pixel-art characters for the projects/pixelart folder — a round 25 px EE smiley head core plus addons (hands, feet, held items, clothes, hats, effects), exported as still sprites, shadowed previews, a spritesheet and GIFs with idle and moving animations for both directions. Work goes in approved stages: the look, the other direction, the idle animation, then the moving animation. Use this whenever the user wants a new EE smiley/character/skin, wants to turn a picture or description into EE style, wants to change, add or animate parts of an existing character folder (like ranfisz/ or evolveye/), or asks for idle, walk or float animations, spritesheets or GIF previews of such a character — even if they don't say "skill" or "EE".
---

# EE character

Every character is a rounded EE head core with addons, and every character gets an idle and a moving animation,
facing right and left. The engine in `scripts/ee_sprite.py` does the shared work (head, ring, lighting, outlines,
mirroring, steam, blink, export); a character is a small `generator.py` that only describes what makes it different.

Read before starting:
- `references/style.md` — the EE art rules and the lessons learned from Ranfisz (what looked wrong and why).
- `references/engine.md` — coordinates, materials, parts, frames, commands.
- `references/animation.md` — before the idle and moving stages.

## Folder conventions

`projects/pixelart/<name>/` — the folder name is the character's name. It fills up stage by stage and, when finished,
holds only:

| File | What | Stage |
|---|---|---|
| `avatar.png` | the user's source picture (theirs, never overwrite) | — |
| `generator.py` | the character spec; `python <name>/generator.py export` re-exports every stage | — |
| `idle_right.png`, `idle_right-preview.png` | still sprite, and 12× with the EE drop shadow on a transparent background | 1 look |
| `idle_left.png`, `idle_left-preview.png` | the same facing left | 2 directions |
| `idle_right.gif`, `idle_left.gif` | 12× idle previews on the EE picker background (51, 51, 51) | 3 idle |
| `<move>_right.gif`, `<move>_left.gif` | 12× previews of the moving animation (walk, float, hop…) | 4 move |
| `spritesheet.png` | one row per animation and facing (idle right, idle left, then the move rows), 1 px gaps; idle rows after stage 3, all rows after stage 4 | 3, 4 |

`<name>/_work/` holds the numbered tries while iterating; offer to delete it once stage 4 is approved.

`ranfisz/` was the first finished character; its `generator.py` predates the engine and is standalone, so don't
refactor it unless asked, but use it and `references/style.md` as the quality bar.

## Workflow

The work goes in four stages, and each starts only after the user approves the previous one. Animating or mirroring
a design the user doesn't like yet wastes their time and buries the one question that matters at each step, so a
stage shows only its own result. Every approved stage is exported to the character folder right away, so the folder
always holds exactly what has been approved.

Within every stage, iterate the same way:
- **One proposal, not a menu.** Show the single result you think fits best and say in a sentence or two why. Offer
  alternatives only when the user asks or there is a real fork you can't decide (`variants` lays stills side by side).
- **Numbered tries.** Each revision becomes the next numbered variant (`"1_…"`, `"2_…"`) and is shown enlarged with
  1× and 2× copies, because sprites must work at game size. Never change an earlier variant's output: the user
  compares by number.
- **Short replies.** What changed and anything you're unsure about.
- **Hand edits.** If the user edits a PNG, treat it as the new base: `python <name>/generator.py diff <png> [variant]
  [right|left]` and change the spec until it reports 0 differing pixels.
- **Stop and ask.** End each stage by asking whether it is approved; anything other than a clear yes means another
  revision. Don't start the next stage's work early, even if the current one seems close.

### Stage 1 — look (facing right)
1. Look at the user's picture or description. List the core (skin colour, face features) and the addons (what is
   held, worn, floating, behind or in front of the head). If the source shows a 3/4 view, draw it facing right.
2. Copy `templates/generator.py` to `projects/pixelart/<name>/generator.py`, keep the user's picture as `avatar.png`,
   and adapt the materials, shapes and `parts()`.
3. Add the design to `VARIANTS`, run `python <name>/generator.py still <variant>` and show
   `_work/<variant>_right_view.png`. Revise until approved.
4. On approval: set `FINAL` to that variant and run `python <name>/generator.py export look`.

### Stage 2 — directions (facing left)
1. Run `python <name>/generator.py still <variant> left`. The mirror and re-shading are automatic, but held items or
   asymmetric details may need another layout on that side (use `facing` in `parts()`). Changes that also touch the
   right side become a new variant, and the right still must be re-approved with it.
2. On approval: `python <name>/generator.py export directions` (and `export look` again if the right still changed).

### Stage 3 — idle
1. Design the `"idle"` entry of `ANIMATIONS` (see `references/animation.md`): the body stays still; blink, steam and
   other small details move. Run `python <name>/generator.py preview <variant> idle` and show the GIFs from `_work/`.
2. On approval: `python <name>/generator.py export idle` (idle GIFs plus a spritesheet of the idle rows).

### Stage 4 — moving
1. Design the moving animation in `ANIMATIONS` (walk for characters with feet, float or hop otherwise), run
   `python <name>/generator.py preview <variant> <move>` and show the GIFs.
2. On approval: `python <name>/generator.py export move` (its GIFs and the full spritesheet), check the folder
   matches the table above, then offer `python <name>/generator.py clean` to delete `_work/`.

If the user later asks to change an approved stage, redo that stage and re-export it and every stage after it,
because they are built on it.

When a new animation or effect type is needed (sitting, sipping, sparkles…), add it to the engine rather than to one
character, keeping existing characters' exports byte-identical, so every later character can use it.

All Python follows the user's code-style rules from CLAUDE.md.
