import sys
from pathlib import Path

sys.path.insert( 0, str( Path( __file__ ).resolve().parents[ 1 ] / ".claude" / "skills" / "ee-character" / "scripts" ) )

from ee_sprite import ( EYE_BLACK, GOLD, Animation, Canvas, Frame, Material, Part, blink, blob, make_ramp, run )

# Character: <name>, <one-line description of the look>.
CANVAS = Canvas( margin_x=3, top=1, bottom=3 )

# Materials: the face uses the EE smiley shading, parts get their own light point at their top-left.
HEAD = Material( GOLD, light=( 8, 5 ), step=4.6 )
SKIN = Material( GOLD, level=1 )
EYES = Material( [ EYE_BLACK ], "flat" )
MOUTH = Material( [ ( 98, 60, 18 ) ], "flat" )
HAT = Material( make_ramp( ( 60, 90, 200 ) ), "edge", level=2 )

# Shapes in head coordinates (the head circle spans columns and rows 0..24).
EYES_OPEN = [ "xx...xx" ] * 4
EYES_CLOSED = [ "......." ] * 3 + [ "xx...xx" ]
SMILE = [ "x.........x", ".x.......x.", "..xxxxxxx.." ]
FOOT = blob({ 0:( 1, 5 ), 1:( 0, 6 ), 2:( 1, 5 ) })
HAND = blob({ 0:( 1, 2 ), 1:( 0, 3 ), 2:( 0, 3 ), 3:( 1, 2 ) })
HAT_GRID = [
  "...xxxxxxx...",
  "..xxxxxxxxx..",
  "..xxxxxxxxx..",
  "xxxxxxxxxxxxx",
]

# Numbered tries, one per proposal; `python generator.py still <name>` renders one into _work/ for review.
# Animations and exports wait until the user approves the base frame.
VARIANTS = {
  "1_plain": {},
  "2_hat": { "hat":True },
}
FINAL = VARIANTS[ "1_plain" ]

# Walk: feet step 1px forward and back, the passing foot lifts 1px, hands swing against the feet.
STEP = [
  Frame( offsets={ "front_foot":( 1, 0 ), "back_foot":( -1, 0 ), "back_hand":( 1, 0 ), "front_hand":( -1, 0 ) }, phase=0 ),
  Frame( offsets={ "back_foot":( 0, -1 ) }, phase=1 ),
  Frame( offsets={ "front_foot":( -1, 0 ), "back_foot":( 1, 0 ), "back_hand":( -1, 0 ), "front_hand":( 1, 0 ) }, phase=2 ),
  Frame( offsets={ "front_foot":( 0, -1 ) }, phase=3 ),
]
IDLE = [ Frame( phase=index % 4 ) for index in range( 8 ) ]
ANIMATIONS = {
  "idle": Animation( blink( IDLE, "eyes", at=5 ), ms=180 ),
  "walk": Animation( blink( STEP * 2, "eyes", at=5 ), ms=140 ),
}


def parts( facing:str, options:dict ):
  # Authored facing right; the engine mirrors and re-shades the left side. Use `facing` for asymmetric designs.
  items = [
    Part( "eyes", EYES_OPEN, ( 9, 8 ), { "x":EYES }, depth="face", states={ "closed":EYES_CLOSED } ),
    Part( "mouth", SMILE, ( 7, 14 ), { "x":MOUTH }, depth="face" ),
    Part( "back_foot", FOOT, ( 4, 22 ), { "x":SKIN }, depth="behind" ),
    Part( "front_foot", FOOT, ( 14, 22 ), { "x":SKIN }, depth="behind" ),
    Part( "back_hand", HAND, ( -2, 14 ), { "x":SKIN } ),
    Part( "front_hand", HAND, ( 23, 14 ), { "x":SKIN } ),
  ]
  if options.get( "hat" ): items.append( Part( "hat", HAT_GRID, ( 6, -1 ), { "x":HAT } ) )

  return items


run( globals() )
