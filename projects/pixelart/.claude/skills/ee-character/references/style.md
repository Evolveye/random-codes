# EE art style

These rules come from building Ranfisz with the user over many rounds of feedback. They are what makes a character
read as an Everybody Edits smiley; break one only when the user asks.

## Head core
- The head is the 25 px EE circle (`HEAD_CIRCLE` in the engine), exactly as in the game. It must be round: an earlier
  hand-drawn head that was taller than wide was rejected.
- Border: 1 px black (14, 9, 5) outside, and a 1 px light ring just inside it whose grey runs from white on the
  top-left to ~145 on the bottom-right. Swapping them (white outside) was tried and looked worse.
- Face fill: the gold ramp `GOLD`, shaded by distance from head point (8, 5) in steps of 4.6. Other skin colours use
  the same shading with another ramp (`make_ramp`).

## Light
- Light always comes from the top-left — also on the left-facing sprite. The engine mirrors shapes first and shades
  afterwards, so never bake lit or shaded pixels into a grid by hand when a material can compute them.
- Shading is stepped: no gradients or anti-aliasing, except semi-transparent steam and the preview shadow.

## Addons (anything outside the head core)
- No light ring around addons. They get a 1 px black outline where they touch empty space. The double white+black
  border, a white-only border and no border were all tried; black was chosen.
- Where an addon overlaps the face or another part, a 1 px contour separates them (a darker shade of the part's ramp;
  black for strong objects like a cup).
- Parts behind the head are clipped by its outline (feet, the far hand, a held item on the far side).
- No single-pixel holes between outlines; the engine fills them.

## Faces
- Keep features big enough to read at 1×: eyes at least 2 px wide, ideally 4×5–6 for an expressive character.
- Features that wrap around the head (bands, stripes) follow the sphere: curve them like an equator seen slightly
  from above — steep near the sides, flat in the middle. A straight diagonal looked wrong.
- A blink (eyes as a short line) is the most effective idle detail. Draw the closed lid on the skin, not on a dark
  band, or it disappears.

## Composition
- Keep the silhouette readable at 1×: an item in the middle of the face can read as a mouth; steam, a handle or an
  off-centre position helps it read as an object.
- Held items need a holder: an item floating next to the head looked glued on. Either a visible hand holds it, or it
  sits behind the head where the hidden far hand holds it.
- The left-facing sprite may differ in layout (Ranfisz holds the cup in front on that side) as long as shapes,
  colours and light match; one side may obscure the face a little since the other shows it fully.
- Small details (an offhand peeking from behind the head) should show only 1–2 columns.

## Ranfisz reference values
- Canvas 31×29, head at (2, 1) facing right. Band: brown (98, 74, 40), lit top (128, 98, 56), bottom (66, 48, 26),
  grin (250, 248, 244). Cup: red (222, 34, 30), lit (255, 108, 92), dark (146, 14, 14), edge (104, 8, 8), red rim with
  no brown coffee pixels. Steam (240, 240, 240) at alpha 238 beside the head, 160 over the face.
