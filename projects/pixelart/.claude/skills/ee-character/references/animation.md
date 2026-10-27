# Animation rules

Learned on Ranfisz; each rule fixed something the user found wrong.

## Every character
- An idle and a move animation, each facing right and left. 8 frames per loop is the default: long enough that one
  blink does not come around too often (a blink every 4 frames looks like a twitch).
- Spritesheet: rows idle right, idle left, then each move animation right and left; frames left to right; 1 px gap.
- GIF timing: idle ~180 ms, walk ~140 ms per frame.

## Movement size
- Move things 1 px at a time. A cup jumping 2 px between frames, or an offhand moving 2 px, was "too intense".
- Never stretch or resize a part to fake motion: feet stretching down while the body bobbed up was rejected twice.
  Move whole parts instead (lift a foot 1 px, step it 1 px forward).
- A grounded walker doesn't bob its whole body. A floating character may (`Frame.bob`), since nothing has to touch
  the ground.

## Idle
- Body and feet stay still. Animate small things: rising steam, a blink. Breathing by moving the body made the feet
  look like they were resizing.

## Walk
- Feet step ±1 px forward and back; on the passing frames one foot lifts 1 px.
- A free front hand swings ±1 px against the feet.
- Held items move with the hand that holds them, and only as much as it does. A cup with its own swing looked out of
  sync; the version where the cup only follows the body was chosen.
- An offhand behind the head moves at most 1 px, tucking further behind rather than peeking out.

## Effects
- Steam (`Wisp`): its bottom pixel stays on the cup in every frame; the wave travels up a row per frame so pixels seem
  to rise and swap sides; the top two pixels fade (×0.45, ×0.75); on odd phases a faint puff breaks off 2 rows above.
  Steam that rose as a block left a gap above the cup and was rejected.
- Steam may pass in front of the face on the side where the face is less important.

## Frames in the engine
- `Frame( offsets={ part:( dx, dy ) }, states={ part:state }, bob=0, phase=n )`. dx > 0 is always forward (toward the
  facing side) because frames are authored facing right and mirrored.
- `blink( frames, "eyes", at=5 )` closes the eyes on frame 6; `phase=index % 4` animates every `Wisp`.
- Use `Animation( frames, ms, frames_left=… )` only when the left-facing pose really moves differently.
