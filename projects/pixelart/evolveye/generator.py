import sys
from colorsys import hsv_to_rgb, rgb_to_hsv
from dataclasses import replace
from functools import cache
from math import atan2, cos, hypot, pi, radians, sin
from pathlib import Path

sys.path.insert( 0, str( Path( __file__ ).resolve().parents[ 1 ] / ".claude" / "skills" / "ee-character" / "scripts" ) )

from ee_sprite import ( EYE_BLACK, GOLD, Animation, Canvas, Frame, Material, Part, blink, blob, render, run )

# Character: Evolveye, a floating soul shaped like an eye, wrapped in blue flames.
CANVAS = Canvas( margin_x=5, top=5, bottom=5 )

# Materials: the flames share one blue ramp lit from the top-left; the eye white is tinted blue at its shaded rim.
EYEBALL = [ ( 255, 255, 255 ), ( 240, 244, 252 ), ( 222, 230, 246 ), ( 200, 212, 236 ), ( 178, 194, 226 ) ]
FLAME = [ ( 156, 210, 255 ), ( 104, 174, 246 ), ( 62, 136, 232 ), ( 38, 100, 204 ), ( 26, 68, 156 ), ( 18, 44, 108 ) ]
FIRE = [ ( 127, 189, 255 ), ( 63, 140, 236 ), ( 34, 96, 196 ), ( 22, 57, 125 ), ( 15, 42, 92 ) ]
FLAME_LIGHT = ( -2, -2 )

HEAD = Material( EYEBALL, light=( 8, 5 ), step=5.5 )
PUPIL = Material( [ EYE_BLACK ], "flat" )
GLINT = Material( [ ( 255, 255, 255 ) ], "flat" )
FLAME_TIP = Material( FLAME, light=FLAME_LIGHT, step=9 )
FLAME_BODY = Material( FLAME, level=1, light=FLAME_LIGHT, step=9 )
FLAME_ROOT = Material( FLAME, level=2, light=FLAME_LIGHT, step=9 )
FIRE_MATERIALS = { symbol:Material( FIRE, level=level, light=( 4, 2 ), step=14 ) for symbol, level in ( ( "t", 0 ), ( "b", 1 ), ( "r", 2 ) ) }
FLAT_FIRE_MATERIALS = { symbol:Material( FIRE, level=level, light=( 4, 2 ), step=24 ) for symbol, level in ( ( "t", 0 ), ( "b", 1 ), ( "r", 2 ) ) }
EYE_WHITE = { "w":Material( [ ( 255, 255, 255 ) ], "flat" ), "l":Material( [ ( 234, 242, 255 ) ], "flat" ), "e":Material( [ ( 185, 210, 247 ) ], "flat" ) }

# Shapes in head coordinates (the head circle spans columns and rows 0..24).
PUPIL_GRID = blob({ 0:( 1, 4 ), 1:( 0, 5 ), 2:( 0, 5 ), 3:( 0, 5 ), 4:( 0, 5 ), 5:( 0, 5 ), 6:( 0, 5 ), 7:( 0, 5 ), 8:( 1, 4 ) })
PUPIL_CLOSED = [ "......" ] * 7 + [ "xxxxxx" ] + [ "......" ]
GLINT_GRID = [ "xx", "xx" ]
SMALL_EYE = blob({ 0:( 3, 7 ), 1:( 1, 9 ), 2:( 0, 10 ), 3:( 0, 10 ), 4:( 0, 10 ), 5:( 0, 10 ), 6:( 0, 10 ), 7:( 0, 10 ), 8:( 0, 10 ), 9:( 0, 10 ), 10:( 1, 9 ), 11:( 3, 7 ) })
SMALL_EYE_AT = ( 8, 6 )
SMALL_PUPIL = blob({ 0:( 1, 3 ), 1:( 0, 4 ), 2:( 0, 4 ), 3:( 0, 4 ), 4:( 0, 4 ), 5:( 1, 3 ) })
SMALL_PUPIL_CLOSED = [ "....." ] * 4 + [ "xxxxx" ] + [ "....." ]
WIDE_PUPIL = blob({ 0:( 1, 4 ), 1:( 0, 5 ), 2:( 0, 5 ), 3:( 0, 5 ), 4:( 0, 5 ), 5:( 0, 5 ), 6:( 1, 4 ) })
WIDE_PUPIL_CLOSED = [ "......" ] * 5 + [ "xxxxxx" ] + [ "......" ]
BLUE_RING_HEAD = Material( FIRE, light=( 8, 5 ), step=5.5, ring=( 185, 215, 255 ) )
BIG_TONGUE_RING = { "radius":11.8, "front":1.0, "back":2.6, "tongues":9, "height":3.2, "swirl":0.3 }

# Head border styles (head coordinates of the final sprite): the round EE outline, softened or dropped.
NAVY = ( 22, 57, 125 )
NO_BORDER = lambda column, row, kind: "fill"
SHADOW_ARC = lambda column, row, kind: None if kind == "black" and column + row > 28 else "fill"
DASHED_NAVY = lambda column, row, kind: "fill" if kind == "ring" or int( ( atan2( row - 12, column - 12 ) + pi ) / ( 2 * pi ) * 27 ) % 3 == 0 else NAVY
SHRINK_1 = lambda column, row, kind: "clear" if kind == "black" else "fill"
SHRINK_2 = lambda column, row, kind: "clear"
EDGE_ONLY = lambda column, row, kind: "edge" if kind == "black" else "fill"
GLOW_RIM = lambda column, row, kind: "fill" if kind == "black" else None
NAVY_LINE = lambda column, row, kind: "fill" if kind == "ring" else NAVY
TONGUE_TIPS = { "radius":10.6, "front":0, "back":0.6, "tongues":9, "height":4.4, "swirl":0.3 }

# Flame rings: thin in front of the gaze, thick trailing behind, with swept tongues around it.
RING = { "radius":12.3, "front":0.6, "back":2.6, "tongues":8, "height":3.0, "swirl":0.35 }
TONGUE_RING = { "radius":11.8, "front":0.8, "back":1.8, "tongues":9, "height":2.6, "swirl":0.3 }

# Big eye like the reference: a wide white with a pale blue rim, a tall pupil near its front edge.
BIG_EYE = blob({ 0:( 4, 8 ), 1:( 2, 10 ), 2:( 1, 11 ), 3:( 1, 11 ), 4:( 0, 12 ), 5:( 0, 12 ), 6:( 0, 12 ), 7:( 0, 12 ), 8:( 0, 12 ), 9:( 0, 12 ), 10:( 0, 12 ), 11:( 1, 11 ), 12:( 1, 11 ), 13:( 2, 10 ), 14:( 4, 8 ) })
BIG_EYE_AT = ( 7, 5 )
BIG_PUPIL = blob({ 0:( 1, 4 ), 1:( 0, 5 ), 2:( 0, 5 ), 3:( 0, 5 ), 4:( 0, 5 ), 5:( 0, 5 ), 6:( 0, 5 ), 7:( 1, 4 ) })
BIG_PUPIL_CLOSED = [ "......" ] * 6 + [ "xxxxxx" ] + [ "......" ]
BIG_EYE_WHITE = { **EYE_WHITE, "m":Material( [ ( 220, 233, 255 ) ], "flat" ) }

# Banded core: fire darkens toward the eye in ragged rings, from light tips outside to navy around the white.
BAND_LIMITS = [ ( 1.0, "n" ), ( 2.4, "d" ), ( 4.2, "m" ), ( 6.2, "b" ) ]
BAND_MATERIALS = { symbol:Material( FLAME, level=level, light=FLAME_LIGHT, step=24 ) for symbol, level in ( ( "t", 0 ), ( "b", 1 ), ( "m", 2 ), ( "d", 3 ), ( "n", 4 ) ) }
SOFT_FLAMES = { "t":Material( FLAME, light=FLAME_LIGHT, step=24 ), "b":Material( FLAME, light=FLAME_LIGHT, step=24 ), "r":Material( FLAME, level=1, light=FLAME_LIGHT, step=24 ) }

# Cloudy look: tongues point straight out instead of sweeping round, band edges wobble in soft blobs.
PEAK_RING = { "radius":11.8, "front":1.0, "back":2.4, "tongues":10, "height":3.0, "swirl":0.08, "peak":True }
CLOUD_WOBBLE = 1.3

# Wilder edge: tongues of uneven length with sharp tips, leaning a little and licking higher on top.
# Dark seams between the tongues run on into the head, so the tongues seem to grow from inside the fire.
WILD_RING = { "radius":11.8, "front":0.5, "back":1.3, "tongues":9, "height":3.4, "swirl":0.25, "peak":True, "sharp":1.5, "rise":0.6, "lengths":[ 1.0, 0.6, 1.25, 0.75, 1.15, 0.55, 1.3, 0.8, 0.95 ], "seams":3.5 }
# Softer dark: shading steps less often and stops one tone above the darkest navy.
SOFT_FLAME = FLAME[ :5 ]
SOFT_DARK_BANDS = { symbol:Material( SOFT_FLAME, level=level, light=FLAME_LIGHT, step=13 ) for symbol, level in ( ( "t", 0 ), ( "b", 1 ), ( "m", 2 ), ( "d", 3 ), ( "n", 4 ) ) }
SOFT_DARK_FLAMES = { symbol:Material( SOFT_FLAME, level=level, light=FLAME_LIGHT, step=13 ) for symbol, level in ( ( "t", 0 ), ( "b", 1 ), ( "r", 2 ) ) }
DARK_BAND_MATERIALS = { symbol:Material( FLAME, level=level, light=FLAME_LIGHT, step=9 ) for symbol, level in ( ( "t", 0 ), ( "b", 1 ), ( "m", 2 ), ( "d", 3 ), ( "n", 4 ) ) }

# Placed tongues: ( angle in degrees, 0 = front, -90 = up; length; half width at the base ). Every tongue bends upward
# like rising fire; the long ones sit on the diagonals where the square frame has room.
TONGUE_LIST = [
  ( -90, 3.2, 2.2 ), ( -64, 2.8, 2.0 ), ( -38, 4.0, 2.2 ), ( -12, 2.4, 1.8 ), ( 14, 2.0, 1.8 ), ( 40, 3.0, 2.0 ),
  ( 68, 2.0, 1.8 ), ( 95, 2.4, 2.0 ), ( 122, 3.4, 2.2 ), ( 146, 4.2, 2.2 ), ( 172, 3.4, 2.2 ), ( -160, 3.6, 2.2 ),
  ( -134, 4.6, 2.4 ), ( -112, 2.8, 2.0 ),
]
PLACED_RING = { "radius":11.8, "base":0.9, "tongue_list":TONGUE_LIST, "bend":0.35 }

# Smooth billows: few rounded tongues of uneven length with a wobble, so the edge shakes without spikes.
BILLOWS_6 = { "radius":11.8, "front":0.8, "back":2.0, "tongues":6, "height":2.6, "swirl":0.1, "round":True, "lengths":[ 1.0, 0.6, 1.2, 0.75, 1.1, 0.55 ], "shake":0.5 }
BILLOWS_7 = { "radius":11.8, "front":0.8, "back":2.0, "tongues":7, "height":2.6, "swirl":0.15, "round":True, "sharp":1.5, "lengths":[ 1.1, 0.5, 0.9, 1.25, 0.6, 1.0, 0.7 ], "shake":0.9 }
BILLOWS_5 = { "radius":11.8, "front":1.0, "back":2.0, "tongues":5, "height":2.4, "swirl":0.05, "round":True, "lengths":[ 1.0, 0.7, 1.2, 0.8, 1.1 ], "shake":1.1 }
BILLOWS_8 = { "radius":11.8, "front":0.8, "back":2.0, "tongues":8, "height":2.8, "swirl":0.2, "round":True, "sharp":2, "lengths":[ 1.15, 0.55, 0.95, 0.7, 1.25, 0.6, 1.0, 0.8 ], "shake":0.6 }

# Sparse tongues: many narrow flames with open gaps between them, uneven and slightly curling, so the edge stays airy.
SPARSE_10 = { "radius":11.8, "front":0.4, "back":1.2, "tongues":10, "height":3.2, "swirl":0.15, "round":True, "sharp":3, "lengths":[ 1.0, 0.55, 1.2, 0.7, 0.95, 0.5, 1.25, 0.65, 1.1, 0.8 ], "shake":0.3 }
SPARSE_12 = { "radius":11.8, "front":0.3, "back":1.0, "tongues":12, "height":3.2, "swirl":0.25, "round":True, "sharp":4, "lengths":[ 1.1, 0.6, 0.9, 1.25, 0.5, 1.0, 0.75, 1.2, 0.55, 0.95, 1.15, 0.65 ], "shake":0.3 }
SPARSE_9 = { "radius":11.8, "front":0.5, "back":1.2, "tongues":9, "height":3.0, "swirl":0.1, "round":True, "sharp":2.5, "lengths":[ 1.0, 0.7, 1.15, 0.6, 0.9, 1.2, 0.65, 1.05, 0.8 ], "rise":0.7, "shake":0.3 }
SPARSE_11 = { "radius":11.8, "front":0.4, "back":1.1, "tongues":11, "height":3.4, "swirl":0.2, "round":True, "sharp":3, "lengths":[ 1.15, 0.35, 1.0, 0.4, 1.25, 0.35, 0.95, 0.45, 1.2, 0.4, 1.05 ], "shake":0.2 }

# Smaller flame edge with loose single pixels floating around it, like sparks drifting off the fire.
SMALL_PEAK_RING = { **PEAK_RING, "front":0.6, "back":1.6, "height":2.3 }
TINY_PEAK_RING = { **PEAK_RING, "front":0.4, "back":1.2, "height":1.8 }
EMBER = Material( [ FLAME[ 1 ] ], "flat" )
EMBER_DARK = Material( [ FLAME[ 3 ] ], "flat" )
# Each ember: ( angle in degrees, 0 = front, -90 = up; extra gap beyond the closest free spot; "e" light or "d" dark ).
EMBERS_LIGHT = [ ( -100, 0, "e" ), ( -55, 1, "e" ), ( -20, 0, "e" ), ( 30, 1, "e" ), ( 75, 0, "e" ), ( 120, 1, "e" ), ( 160, 0, "e" ), ( -165, 1, "e" ), ( -135, 0, "e" ) ]
EMBERS_MIXED = [ ( -100, 0, "e" ), ( -75, 1, "d" ), ( -48, 0, "e" ), ( -15, 1, "d" ), ( 25, 0, "e" ), ( 62, 1, "d" ), ( 100, 0, "e" ), ( 135, 1, "d" ), ( 162, 0, "e" ), ( -170, 1, "d" ), ( -140, 0, "e" ), ( -122, 2, "d" ) ]

# Smaller body (the head loses its outer 1 or 2 px) with taller flames growing from the new edge.
TALL_RING_1 = { **PEAK_RING, "radius":10.8, "front":1.0, "back":2.4, "height":3.8 }
TALL_RING_2 = { **PEAK_RING, "radius":9.8, "front":1.0, "back":2.6, "height":4.4 }

# Lighter 16: the same flames around a body 1 or 2 px smaller; shaky versions give the tongues uneven lengths and a wobble.
SHAKY_LENGTHS = [ 1.0, 0.6, 1.25, 0.75, 1.1, 0.55, 1.3, 0.8, 0.65, 1.15 ]
PEAK_RING_1 = { **PEAK_RING, "radius":10.8 }
PEAK_RING_2 = { **PEAK_RING, "radius":9.8 }
SHAKY_RING_1 = { **PEAK_RING_1, "lengths":SHAKY_LENGTHS, "shake":0.5 }
SHAKY_RING_2 = { **PEAK_RING_2, "lengths":SHAKY_LENGTHS, "shake":0.5 }

# Body ends on the base circle: no flame band around it, only separate tongues growing from its edge.
CIRCLE_TONGUES_10 = { "radius":12.0, "front":0, "back":0, "tongues":10, "height":3.4, "swirl":0.08, "peak":True, "lengths":SHAKY_LENGTHS, "shake":0.3 }
CIRCLE_TONGUES_8 = { "radius":12.0, "front":0, "back":0, "tongues":8, "height":3.8, "swirl":0.1, "round":True, "sharp":2, "lengths":[ 1.0, 0.6, 1.2, 0.75, 1.1, 0.55, 1.15, 0.8 ], "shake":0.3 }
CIRCLE_TONGUES_12 = { "radius":12.0, "front":0, "back":0.8, "tongues":12, "height":3.0, "swirl":0.08, "peak":True, "lengths":[ 1.0, 0.6, 1.2, 0.75, 1.1, 0.55, 1.25, 0.8, 0.65, 1.15, 0.7, 0.95 ], "shake":0.3 }

# Ghostly flames: no spikes on the front or bottom, a few broad steady tongues rising up and trailing back.
GHOST_CROWN = { "radius":12.0, "base":0.3, "base_top":1.2, "base_back":0.8, "bend":0.2, "bend_x":0.15, "tongue_list":[ ( -150, 3.6, 3.0 ), ( -118, 4.2, 3.2 ), ( -84, 3.6, 3.0 ), ( -50, 2.4, 2.4 ) ] }
GHOST_TRAIL = { "radius":12.0, "base":0.3, "base_top":0.6, "base_back":1.4, "bend":0.08, "bend_x":0.12, "tongue_list":[ ( -172, 4.2, 3.0 ), ( 168, 3.6, 2.6 ), ( 140, 2.8, 2.4 ), ( -140, 3.6, 2.8 ), ( -102, 2.6, 2.4 ) ] }
GHOST_CANDLE = { "radius":12.0, "base":0.6, "base_top":0.6, "bend":0.25, "tongue_list":[ ( -92, 4.0, 3.0 ), ( -126, 3.4, 2.8 ), ( -58, 3.0, 2.6 ), ( -160, 2.4, 2.4 ), ( -24, 2.0, 2.2 ) ] }

# Steady all-round flames: a soft band around the circle with broad, uneven tongues pointing every way.
STEADY_9 = { "radius":12.0, "front":0.6, "back":1.2, "tongues":9, "height":2.6, "swirl":0.08, "peak":True, "sharp":1.3, "lengths":[ 1.0, 0.65, 1.2, 0.8, 1.1, 0.6, 1.15, 0.75, 0.9 ], "shake":0.3 }
STEADY_PLACED = { "radius":12.0, "base":0.6, "bend":0, "tongue_list":[
  ( -90, 3.4, 2.8 ), ( -64, 2.6, 2.6 ), ( -38, 3.0, 2.8 ), ( -12, 2.2, 2.4 ), ( 14, 2.6, 2.6 ), ( 40, 2.2, 2.4 ), ( 66, 2.8, 2.6 ),
  ( 92, 2.2, 2.4 ), ( 118, 3.0, 2.8 ), ( 144, 2.4, 2.6 ), ( 170, 3.2, 2.8 ), ( -164, 2.6, 2.6 ), ( -140, 3.4, 2.8 ), ( -115, 2.4, 2.6 ),
] }
STEADY_8_ROUND = { "radius":12.0, "front":0.8, "back":1.4, "tongues":8, "height":2.8, "swirl":0.06, "round":True, "sharp":1.5, "lengths":[ 1.0, 0.7, 1.15, 0.8, 1.1, 0.65, 1.2, 0.85 ], "shake":0.3 }

# Balanced 16: less blue body, and 16's flames taller or thicker to fill the room it frees.
BALANCED_1 = { **PEAK_RING, "radius":10.8, "front":1.2, "back":2.6, "height":3.8 }
BALANCED_2 = { **PEAK_RING, "radius":9.8, "front":1.2, "back":2.8, "height":4.4 }
BALANCED_2_THICK = { **PEAK_RING, "radius":9.8, "front":1.6, "back":3.2, "height":3.6 }

# 47 refined: the back flames pulled in toward the circle, grainy dark bands under the eye.
BALANCED_2_NEAR = { **BALANCED_2_THICK, "back":2.2 }
BALANCED_2_ROUND = { **BALANCED_2_THICK, "back":1.6 }

# Rounded, airy flames: soft billow tops instead of points, lighter tones so the flames feel weightless.
LIGHT_FLAMES = { "t":Material( SOFT_FLAME, light=FLAME_LIGHT, step=13 ), "b":Material( SOFT_FLAME, light=FLAME_LIGHT, step=13 ), "r":Material( SOFT_FLAME, level=1, light=FLAME_LIGHT, step=13 ) }
ROUND_10 = { **BALANCED_2_NEAR, "peak":False, "round":True, "sharp":1.2, "height":3.2 }
ROUND_8 = { **BALANCED_2_NEAR, "peak":False, "round":True, "sharp":1.0, "tongues":8, "height":3.4 }
ROUND_10_SOFT = { **BALANCED_2_NEAR, "peak":False, "round":True, "sharp":1.5, "height":3.4 }

# 47 fixed: the same flames with softly rounded tips, and the core in 12's gentler gradient, speckled with lighter blue.
ROUNDED_47 = { **BALANCED_2_THICK, "peak":False, "round":True, "sharp":2.0 }
ROUNDER_47 = { **BALANCED_2_THICK, "peak":False, "round":True, "sharp":1.6 }

# Best flames combined (angles: 0 = front, 90 = down): 47's rounded crest above the pupil, 54's softer tongues on the
# front and lower back, 16's bottom tongue with its dangling pixel over 47's body. The gradient spans eye to body edge.
COMBINED_RING = { "radius":9.8, "default":[ BALANCED_2_THICK ], "sectors":[
  ( -100, -45, [ BALANCED_2_THICK ] ), ( -45, 50, [ ROUNDED_47 ] ), ( 60, 115, [ BALANCED_2_THICK, PEAK_RING ] ), ( 115, 180, [ ROUNDED_47 ] ),
] }
RELATIVE_LIMITS = [ ( 0.16, "n" ), ( 0.36, "d" ), ( 0.58, "m" ), ( 0.8, "b" ) ]
BODY_EDGE = 10.4

# 59 refined: 47's colours with the core ending on the flames' body tone and flame roots no darker than it, so no
# ring shows where the circle meets the flames; 54's rounded tongues reach round the bottom-right, and 16's bottom
# tongue with its dangling pixel is turned 1 px left (and in 60 also raised 1 px).
SMOOTH_FLAMES = { symbol:Material( SOFT_FLAME, level=level, light=FLAME_LIGHT, step=13 ) for symbol, level in ( ( "t", 0 ), ( "b", 1 ), ( "r", 1 ) ) }
SMOOTH_LIMITS = [ ( 0.18, "n" ), ( 0.42, "d" ), ( 0.7, "m" ), ( 2, "b" ) ]
BOTTOM_LEFT_UP = { **PEAK_RING, "offset":-0.12, "radius":10.8 }
BOTTOM_LEFT = { **PEAK_RING, "offset":-0.12 }
SMOOTH_RING_UP = { "radius":9.8, "default":[ BALANCED_2_THICK ], "sectors":[
  ( -100, -45, [ BALANCED_2_THICK ] ), ( -45, 72, [ ROUNDED_47 ] ), ( 72, 115, [ BALANCED_2_THICK, BOTTOM_LEFT_UP ] ), ( 115, 180, [ ROUNDED_47 ] ),
] }
SMOOTH_RING = { **SMOOTH_RING_UP, "sectors":[ ( start, end, [ BALANCED_2_THICK, BOTTOM_LEFT ] if BOTTOM_LEFT_UP in sources else sources ) for start, end, sources in SMOOTH_RING_UP[ "sectors" ] ] }

# 47's colours and gradient with 54's rounded flames, keeping 47's crest above the pupil (wide or narrow sector).
CREST_RING = { "radius":9.8, "default":[ ROUNDED_47 ], "sectors":[ ( -100, -45, [ BALANCED_2_THICK ] ) ] }
CREST_RING_NARROW = { "radius":9.8, "default":[ ROUNDED_47 ], "sectors":[ ( -90, -55, [ BALANCED_2_THICK ] ) ] }

# 64 refined: the upper-back flames moved 1 px forward, thinner tongues like 47, and three shorter, pointier ones.
THIN_ROUNDED = { **ROUNDED_47, "sharp":2.6 }
THIN_SHORT = { **THIN_ROUNDED, "sharp":3.2, "lengths":[ 1, 1, 0.55, 1, 1, 1, 0.5, 1, 1, 0.6 ] }
SHIFTED_CREST = { "radius":9.8, "default":[ ROUNDED_47 ], "sectors":[
  ( -90, -55, [ BALANCED_2_THICK ] ), ( -180, -90, [ { "shift":( 1, 0 ), "source":ROUNDED_47 } ] ), ( 150, 181, [ { "shift":( 1, 0 ), "source":ROUNDED_47 } ] ),
] }
THIN_CREST = { **SHIFTED_CREST, "default":[ THIN_ROUNDED ], "sectors":[
  ( -90, -55, [ BALANCED_2_THICK ] ), ( -180, -90, [ { "shift":( 1, 0 ), "source":THIN_ROUNDED } ] ), ( 150, 181, [ { "shift":( 1, 0 ), "source":THIN_ROUNDED } ] ),
] }
SHORT_CREST = { **SHIFTED_CREST, "default":[ THIN_SHORT ], "sectors":[
  ( -90, -55, [ BALANCED_2_THICK ] ), ( -180, -90, [ { "shift":( 1, 0 ), "source":THIN_SHORT } ] ), ( 150, 181, [ { "shift":( 1, 0 ), "source":THIN_SHORT } ] ),
] }

# 65 refined: the top-right and right flames curl up a little (lift grows with distance from the body), the left
# flame comes from 47.
LIFTED_CREST = { "radius":9.8, "default":[ ROUNDED_47 ], "sectors":[
  ( -90, -55, [ BALANCED_2_THICK ] ), ( 160, 181, [ BALANCED_2_THICK ] ), ( -180, -160, [ BALANCED_2_THICK ] ),
  ( -180, -90, [ { "shift":( 1, 0 ), "source":ROUNDED_47 } ] ), ( 150, 181, [ { "shift":( 1, 0 ), "source":ROUNDED_47 } ] ),
  ( -55, 25, [ { "lift":0.12, "source":ROUNDED_47 } ] ),
] }
LIFT_REACH = 5.5
LIFTED_MORE_CREST = { **LIFTED_CREST, "sectors":LIFTED_CREST[ "sectors" ][ :-1 ] + [ ( -55, 25, [ { "lift":0.22, "source":ROUNDED_47 } ] ) ] }
LIFTED_LESS_CREST = { **LIFTED_CREST, "sectors":LIFTED_CREST[ "sectors" ][ :-1 ] + [ ( -55, 25, [ { "lift":0.06, "source":ROUNDED_47 } ] ) ] }
LIFTED_SLIGHT_CREST = { **LIFTED_CREST, "sectors":LIFTED_CREST[ "sectors" ][ :-1 ] + [ ( -55, 25, [ { "lift":0.08, "source":ROUNDED_47 } ] ) ] }

# Glowing like the pixel reference: a dotted navy edge instead of solid black, tones scattered through the flames,
# a little mixing by the eye; 73 also makes the flame tips and edge dots see-through.
GLOW_EDGE = lambda column, row: ( 15, 42, 92 ) if pixel_noise( column + 7, row + 13 ) > -0.3 else None
GLOW_EDGE_SOFT = lambda column, row: ( 15, 42, 92, 200 ) if pixel_noise( column + 7, row + 13 ) > -0.3 else None
GLOW_FLAMES = { **SOFT_DARK_FLAMES, "t":replace( SOFT_DARK_FLAMES[ "t" ], alpha=190 ) }
CHAOTIC_CREST = { **LIFTED_SLIGHT_CREST, "sectors":[ ( start, end, [ { "chaos":0.3, "source":source } for source in sources ] ) for start, end, sources in LIFTED_SLIGHT_CREST[ "sectors" ] ], "default":[ { "chaos":0.3, "source":ROUNDED_47 } ] }

# Reference palette (the user's pixel art): its five blues for the core and flames, and a light blue edge instead of
# black for a ghostly glow; 75 scatters tones like the reference, 76 leaves gaps in the edge.
REFERENCE_BLUE = ( 127, 189, 255 )
REFERENCE_BANDS = { symbol:Material( FIRE, level=level, light=FLAME_LIGHT, step=13 ) for symbol, level in ( ( "t", 0 ), ( "b", 1 ), ( "m", 2 ), ( "d", 3 ), ( "n", 4 ) ) }
REFERENCE_FLAMES = { symbol:Material( FIRE, level=level, light=FLAME_LIGHT, step=13 ) for symbol, level in ( ( "t", 0 ), ( "b", 1 ), ( "r", 2 ) ) }
# Lighter: every tone one step up the ramp and slower shading toward the bottom-right.
LIGHT_REFERENCE_BANDS = { symbol:Material( FIRE, level=level, light=FLAME_LIGHT, step=20 ) for symbol, level in ( ( "t", 0 ), ( "b", 0 ), ( "m", 1 ), ( "d", 2 ), ( "n", 3 ) ) }
LIGHT_REFERENCE_FLAMES = { symbol:Material( FIRE, level=level, light=FLAME_LIGHT, step=20 ) for symbol, level in ( ( "t", 0 ), ( "b", 0 ), ( "r", 1 ) ) }
# Full gradient: the reference's blues spread evenly from the eye to the flame tips.
GRADIENT_BINS = 120
GRADIENT_STEP = 40
GRADIENT_4 = FIRE[ :4 ]
GRADIENT_5 = FIRE
# Inner flames: every tone of the gradient ends in its own tongues, alternating their lean so they drift different ways.
INNER_FLAMES = { "tongues":[ 7, 9, 8, 10 ], "lean":0.6, "height":0.18 }
WILD_INNER_FLAMES = { "tongues":[ 6, 9, 7, 10 ], "lean":1.0, "height":0.28 }
# Lightest blue only as a 1 px rim: the inside runs through the other tones, the rim is the outline (whole, dotted,
# or only on the lit top-left side).
INSIDE_TONES = FIRE[ 1:4 ]
LIT_EDGE = lambda column, row: REFERENCE_BLUE if column + row < 26 else None
# Random turns: the inner flames of 88 each lean their own way (two seeds, and one with wilder turns).
RANDOM_INNER = { **WILD_INNER_FLAMES, "random":1, "lean":1.0 }
RANDOM_INNER_WILD = { **WILD_INNER_FLAMES, "random":1, "lean":1.6, "jitter":0.3 }
RANDOM_INNER_OTHER = { **WILD_INNER_FLAMES, "random":5, "lean":1.0 }
# Outer flames with random turns (lean and length per tongue) and 47's stepped upper-back edge instead of a straight one.
RANDOM_FLAMES = { "seed":2, "lean":0.25, "length":0.25 }
RANDOM_FLAMES_WILD = { "seed":2, "lean":0.4, "length":0.35 }
RANDOM_FLAMES_OTHER = { "seed":9, "lean":0.25, "length":0.25 }
# Calmer: 71's four top-right flames untouched, 47's upper-back flame, only a light random turn elsewhere.
GENTLE_FLAMES = { "seed":9, "lean":0.12, "length":0.15 }
GENTLE_LEAN = { "seed":9, "lean":0.12, "length":0 }
# 95's lower-back flames redone: 47's, curling up like rising fire, or shorter and rounder.
LOWER_BACK_CURL = [ { "lift":0.1, "source":ROUNDED_47 } ]
LOWER_BACK_SHORT = [ { **ROUNDED_47, "height":2.6, "back":2.4 } ]
# Squeezed: the back half pulled 1 px forward and the bottom half 1 px up, with four new lower-back flames to fit.
SQUEEZE = ( 1, 1 )
LOWER_BACK_FOUR_ROUND = [ { **ROUNDED_47, "tongues":16, "height":3.0, "offset":0.3, "lengths":[ 1 ] * 9 + [ 0.85, 1.1, 0.8, 1.0 ] + [ 1 ] * 3 } ]
LOWER_BACK_FOUR_PEAK = [ { **BALANCED_2_THICK, "tongues":16, "height":2.8, "offset":0.3, "lengths":[ 1 ] * 9 + [ 0.85, 1.1, 0.8, 1.0 ] + [ 1 ] * 3 } ]
# The user's hand-edited 101 (101-2.png): its blue area without the light rim, which the outline adds back. Built on
# it: the eye 1 px higher and new inner flames, each tongue turned at random, with pixels flickering between tones.
SILHOUETTE_101_2 = [
  "...................................",
  "...................................",
  ".............x.....................",
  "............xxx....xxx.............",
  "............xxxx.xxxx..............",
  "...........xxxxxxxxxx.....x........",
  "...........xxxxxxxxxxx...xxx.......",
  "...........xxxxxxxxxxxxxxxxxx......",
  ".....xx...xxxxxxxxxxxxxxxxxx.......",
  ".....xxx.xxxxxxxxxxxxxxxxxxx.......",
  ".....xxxxxxxxxxxxxxxxxxxxxx........",
  ".....xxxxxxxxxxxxxxxxxxxxxxx.......",
  "......xxxxxxxxxxxxxxxxxxxxxxxx.....",
  "......xxxxxxxxxxxxxxxxxxxxxxxxxx...",
  "......xxxxxxxxxxxxxxxxxxxxxxxxxx...",
  "......xxxxxxxxxxxxxxxxxxxxxxxxxx...",
  ".....xxxxxxxxxxxxxxxxxxxxxxxxxx....",
  "..xxxxxxxxxxxxxxxxxxxxxxxxxxx......",
  "....xxxxxxxxxxxxxxxxxxxxxxxxx......",
  ".....xxxxxxxxxxxxxxxxxxxxxxxxx.....",
  ".....xxxxxxxxxxxxxxxxxxxxxxxxx.....",
  "......xxxxxxxxxxxxxxxxxxxxxxxxx....",
  ".......xxxxxxxxxxxxxxxxxxxxxxxx....",
  ".......xxxxxxxxxxxxxxxxxxxxxxx.....",
  ".......xxxxxxxxxxxxxxxxxxx..xx.....",
  "......xxxxxxxxxxxxxxxxxxxx.........",
  ".......xxxxxxxxxxxxxxxxxx..........",
  "............xxxxxxxxxxxxx..........",
  "..............xxxxx..xxxx..........",
  "..............xxxx...xxx...........",
  "..............xxx....xxx...........",
  "...................................",
  "...................................",
  "...................................",
  "...................................",
]
RAISED_EYE = ( BIG_EYE_AT[ 0 ], BIG_EYE_AT[ 1 ] - 1 )

# 101-2 with the two lower-back flames 1 px forward (the leftmost pixel of canvas rows 16-26 dropped), and calm inner
# flames with softly mixed tone borders.
SILHOUETTE_NUDGED = [ line[ :line.index( "x" ) ] + "." + line[ line.index( "x" ) + 1: ] if 16 <= row <= 26 else line for row, line in enumerate( SILHOUETTE_101_2 ) ]
# The user's hand edits of 107 (107-2.png), canvas ( column, row ): tone 0 mid, 1 dark, 2 navy, "." removed.
# Rim highlights inside the black outline: white for the normal character, gold for the premium one, shaded from the
# top-left light like the EE head ring.
WHITE_RIM = Material( [ ( 255, 255, 255 ), ( 232, 236, 244 ), ( 205, 212, 228 ), ( 178, 188, 210 ), ( 150, 162, 190 ) ], light=FLAME_LIGHT, step=8 )
GOLD_RIM = Material( GOLD, light=FLAME_LIGHT, step=8 )
EDITS_107_2 = {
  ( 9, 12 ):"2", ( 9, 17 ):"1", ( 9, 18 ):"2", ( 12, 10 ):"2", ( 13, 4 ):"1", ( 13, 29 ):"0", ( 15, 28 ):"1", ( 16, 28 ):"1",
  ( 16, 30 ):".", ( 19, 26 ):"1", ( 21, 29 ):".", ( 21, 30 ):".", ( 22, 30 ):".", ( 23, 30 ):".", ( 24, 28 ):".", ( 25, 9 ):"2",
  ( 25, 25 ):".", ( 26, 20 ):"2", ( 28, 21 ):"1", ( 29, 14 ):"1",
}
CALM_INNER = { **INNER_FLAMES, "lean":0.4, "height":0.12 }
CHAOTIC_INNER = { **WILD_INNER_FLAMES, "random":3, "lean":1.0 }
CHAOTIC_INNER_OTHER = { **WILD_INNER_FLAMES, "random":7, "lean":1.3, "jitter":0.2 }
LIGHT_EDGE_DOTTED = lambda column, row: REFERENCE_BLUE if pixel_noise( column + 7, row + 13 ) > -0.5 else None

# Flame core: tongues growing out from the eye's rim toward the head's edge.
CORE_TONGUES = 7
CORE_SWIRL = 0.3
CORE_BASE = 1.5
CORE_HEIGHT = 6

FIRE_HEAD = { "flame_head":True, "head":BLUE_RING_HEAD, "streaks":0.45, "wide_pupil":True, "ring":BIG_TONGUE_RING, "fire":FLAT_FIRE_MATERIALS, "glow":( 1.0, 2.0 ) }

SOFT_DARK = { **FIRE_HEAD, "head":replace( BLUE_RING_HEAD, border=NO_BORDER ), "big_eye":True, "cloudy":True, "ring":PEAK_RING, "dark":"soft" }

REFERENCE_LOOK = { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":LIFTED_SLIGHT_CREST, "bands":REFERENCE_BANDS, "flames":REFERENCE_FLAMES, "outline":REFERENCE_BLUE, "open_gaps":True }

VARIANTS_95 = { **REFERENCE_LOOK, "gradient":INSIDE_TONES, "inner":WILD_INNER_FLAMES, "outline":LIT_EDGE, "upper_back_from_47":True }

EDITED_107 = { **VARIANTS_95, "silhouette":SILHOUETTE_NUDGED, "eye_at":RAISED_EYE, "inner":CALM_INNER, "edits":EDITS_107_2 }

# 110-119 again in 47's blues (become 130-139).
# 47's broad left-middle flame instead of the thin spike (canvas rows 16-21 start at these columns, 47's shape moved
# 2 px forward to sit on the squeezed body); the 47-blues versions with it become 140-149.
LEFT_FLAME_47 = { 16:6, 17:3, 18:4, 19:5, 20:6, 21:6 }
SILHOUETTE_LEFT_47 = [ "." * LEFT_FLAME_47[ row ] + "x" * ( line.index( "x" ) - LEFT_FLAME_47[ row ] ) + line[ line.index( "x" ): ] if row in LEFT_FLAME_47 and LEFT_FLAME_47[ row ] < line.index( "x" ) else line for row, line in enumerate( SILHOUETTE_NUDGED ) ]
# Black outline outside the whole character: the light blue (or white / gold) rim stays the last pixel and the black
# goes around it (the 47-flame versions with black edges, renumbered 153-159).
OUTER_RIMS = {
  "113_edited_107_black":( "lit", "l" ), "114_edited_107_dark_rim_black":( "lit", "l" ), "115_edited_107_darker_rim_black":( "lit", "l" ),
  "116_white_double_border":( "all", "w" ), "117_gold_double_border":( "all", "w" ), "118_white_lit_rim":( "lit", "w" ), "119_gold_lit_rim":( "lit", "w" ),
}
# Softer ends for the lit-side rims: dithered out between two diagonals, or fading through light blue first.
RIM_FADE = ( 20, 32 )
FADED_RIMS = {
  "118_white_lit_rim":[ ( "dither", ( "lit", "w", RIM_FADE ) ), ( "blue", ( "lit", "w", RIM_FADE, "l" ) ) ],
  "119_gold_lit_rim":[ ( "dither", ( "lit", "w", RIM_FADE ) ), ( "blue", ( "lit", "w", RIM_FADE, "l" ) ) ],
}
# Rims that turn into the flames' blue toward the shaded bottom-right instead of ending: white to blue (normal) and
# gold to blue (premium), all round, for both colourings.
WHITE_TO_BLUE = Material( [ ( 255, 255, 255 ), ( 214, 232, 255 ), ( 170, 208, 255 ), ( 127, 189, 255 ), ( 98, 160, 240 ) ], light=FLAME_LIGHT, step=8 )
GOLD_TO_BLUE = Material( [ ( 252, 216, 124 ), ( 226, 210, 160 ), ( 180, 200, 215 ), ( 127, 189, 255 ), ( 98, 160, 240 ) ], light=FLAME_LIGHT, step=8 )
# Warmer premium rims: gold through bright yellow and cream into pale blue (no grey middle), or gold to pale yellow.
GOLD_CREAM_BLUE = Material( [ ( 252, 216, 124 ), ( 255, 234, 150 ), ( 250, 242, 200 ), ( 214, 230, 250 ), ( 156, 205, 255 ) ], light=FLAME_LIGHT, step=8 )
GOLD_PALE_YELLOW = Material( [ ( 252, 216, 124 ), ( 255, 228, 140 ), ( 255, 236, 165 ), ( 250, 240, 190 ), ( 240, 236, 205 ) ], light=FLAME_LIGHT, step=8 )
# 47's sprite as the colour source for the transferred versions (176-181), and its tones for the user's dark specks.
SOURCE_47 = { "flame_head":True, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "big_eye":True, "cloudy":True, "ring":BALANCED_2_THICK, "dark":"soft", "streaks":0.45, "wide_pupil":True, "fire":FLAT_FIRE_MATERIALS, "glow":( 1.0, 2.0 ) }
SPECK_47 = { "2":SOFT_FLAME[ 4 ], "1":SOFT_FLAME[ 3 ], "0":SOFT_FLAME[ 1 ] }
# Smooth 47 ramp (darkest first is reversed below: index 0 is the lightest), a smaller navy core hugging the white.
SMOOTH_TONES = SOFT_FLAME
SMOOTH_FLAT = { "limits":[ 0.1, 0.3, 0.55, 0.8 ], "wobble":0.06 }
SMOOTH_SHADED = { **SMOOTH_FLAT, "shade":{ "start":0.45, "steps":2 } }
# Fresh colouring: dark blue around the white, two middle blues, a lighter blue toward the edge and a light blue
# 1 px border, no light direction. Tones lightest first; limits are shares of the way from the eye to the edge.
FRESH_NAVY = { "tones":[ ( 96, 166, 246 ), ( 63, 140, 236 ), ( 46, 116, 216 ), ( 22, 57, 125 ) ], "limits":[ 0.14, 0.45, 0.75 ], "wobble":0.05, "border":( 127, 189, 255 ) }
FRESH_DARK = { **FRESH_NAVY, "tones":[ ( 96, 166, 246 ), ( 63, 140, 236 ), ( 46, 116, 216 ), ( 34, 96, 196 ) ] }
# Thinner dark ring: navy only right by the white (an absolute width), the middle blues and the lighter blue share
# the rest of the way to the light border.
FRESH_THIN = { **FRESH_NAVY, "dark_px":1.2, "rest_limits":[ 0.35, 0.7 ] }
FRESH_MIDDLE = { **FRESH_NAVY, "dark_px":1.8, "rest_limits":[ 0.35, 0.7 ] }
FRESH_MIDDLE_WIDE = { **FRESH_NAVY, "dark_px":2.3, "rest_limits":[ 0.35, 0.7 ] }
# Even ramp: every tone the same step from the next, from the light border blue down to a dark blue (not navy).
EVEN_RAMP = [ tuple( round( light + ( dark - light ) * step / 4 ) for light, dark in zip( ( 127, 189, 255 ), ( 30, 92, 200 ) ) ) for step in range( 5 ) ]
EVEN_RAMP_6 = [ tuple( round( light + ( dark - light ) * step / 5 ) for light, dark in zip( ( 127, 189, 255 ), ( 30, 92, 200 ) ) ) for step in range( 6 ) ]
FRESH_EVEN = { **FRESH_MIDDLE, "tones":EVEN_RAMP[ 1: ], "border":EVEN_RAMP[ 0 ], "ramp_specks":True }
FRESH_EVEN_SOFT = { **FRESH_EVEN, "dither":0.08 }
FRESH_EVEN_6 = { **FRESH_MIDDLE, "tones":EVEN_RAMP_6[ 1: ], "border":EVEN_RAMP_6[ 0 ], "ramp_specks":True, "dark_px":1.6, "rest_limits":[ 0.25, 0.5, 0.75 ], "dither":0.06 }
# 195 with a slightly bigger step down to the darkest blue, and with volume (lit top-left, shaded bottom-right).
DEEPER_RAMP_6 = EVEN_RAMP_6[ :5 ] + [ ( 22, 78, 182 ) ]
FRESH_DEEPER = { **FRESH_EVEN_6, "tones":DEEPER_RAMP_6[ 1: ] }
FRESH_VOLUME = { **FRESH_DEEPER, "volume":0.15 }
FRESH_VOLUME_STRONG = { **FRESH_DEEPER, "volume":0.25, "shade":{ "start":0.6, "steps":1 } }
# Every blue a little darker (red and green drop more than blue, so the tones stay saturated).
DIMMED_RAMP_6 = [ ( round( red * 0.85 ), round( green * 0.87 ), round( blue * 0.93 ) ) for red, green, blue in DEEPER_RAMP_6 ]
DIMMED = { "tones":DIMMED_RAMP_6[ 1: ], "border":DIMMED_RAMP_6[ 0 ] }
# Brighter lightest blue: only the border tone raised, or the whole ramp re-spread in equal steps from it down to the
# dimmed darkest blue.
BRIGHT_BORDER = ( 122, 182, 252 )
EVEN_DIMMED_RAMP = [ tuple( round( light + ( dark - light ) * step / 5 ) for light, dark in zip( BRIGHT_BORDER, DIMMED_RAMP_6[ -1 ] ) ) for step in range( 6 ) ]
# More vibrant, like 47's blues: every tone's saturation raised (same brightness), and 47's near-pure blue hue.
VIBRANCE = 1.3
VIBRANT = lambda color: tuple( round( channel * 255 ) for channel in hsv_to_rgb( 0.6, min( 1, rgb_to_hsv( *( channel / 255 for channel in color ) )[ 1 ] * VIBRANCE ), rgb_to_hsv( *( channel / 255 for channel in color ) )[ 2 ] ) )
VIBRANT_DIMMED = { "tones":[ VIBRANT( tone ) for tone in DIMMED_RAMP_6[ 1: ] ], "border":VIBRANT( DIMMED_RAMP_6[ 0 ] ) }
VIBRANT_BRIGHT = { **VIBRANT_DIMMED, "border":VIBRANT( BRIGHT_BORDER ) }
VIBRANT_EVEN = { "tones":[ VIBRANT( tone ) for tone in EVEN_DIMMED_RAMP[ 1: ] ], "border":VIBRANT( EVEN_DIMMED_RAMP[ 0 ] ) }
# 47's way of shading: tones step darker with distance from a top-left light point (47 uses ( -2, -2 ) and 13 px).
LIGHT_47 = { "light_point":( -2, -2 ), "light_step":13 }
# 47's own lighting on the edited silhouette: 47's cloudy bands on the body, 47's flame tongues (their light tips make
# the streaks on the left), every tone stepping darker every 13 px from a light point just off the top-left corner, so
# the top-left is the brightest blue. Optionally in more vibrant blues.
VIBRANT_47_RAMP = [ VIBRANT( tone ) for tone in SOFT_FLAME ]
# Flame tip steps per frame (> 0 grows, < 0 shrinks), one row per tongue clockwise from the left, changing 1 px a frame.
IDLE_TIPS = [ [ 0, 1, 1, 0, 0, 0, -1, 0 ], [ 1, 0, 0, -1, 0, 1, 1, 0 ], [ 0, 0, -1, 0, 1, 1, 0, 0 ], [ -1, 0, 1, 1, 0, 0, 0, -1 ], [ 0, 1, 0, 0, -1, 0, 1, 0 ] ]
FLOAT_TIPS = [ [ 1, 1, 0, 0, 1, 1, 1, 0 ], [ 0, 1, 1, 1, 0, 0, 1, 1 ], [ 0, 0, 1, 0, 0, 1, 1, 0 ], [ 0, -1, -1, 0, 0, -1, 0, 0 ], [ -1, -1, 0, 0, -1, -1, 0, -1 ], [ 0, 0, 1, 1, 0, 0, 1, 1 ], [ 1, 1, 0, 1, 1, 0, 0, 1 ] ]
# Flame motions for `flow`. Idle: each tongue licks 1 px out at its own moment, the extra pixel breaks off and rises
# as it fades, the tongue dips 1 px later; tongues pointing down shed nothing. Float: the moment runs with the column,
# so waves travel from the front to the back; the front tongues press in, upright tongues bend back, and sparks
# stream backward off every tongue that isn't in front.
IDLE_FLOW = { "offset":lambda number, column: number * 3 % 8, "cycles":{ role:[ 0, 1, 1, 0, 0, 0, -1, 0 ] for role in ( "front", "back", "side" ) }, "born":[ 3 ], "drift":( 0, -1 ), "spark_from":lambda role, outward: outward[ 1 ] <= 0 }
FLOAT_FLOW = { "offset":lambda number, column: column // 4, "cycles":{ "front":[ -1, -1, 0, -1, -1, 0, 0, -1 ], "back":[ 1, 1, 0, 0, 1, 1, 0, 0 ], "side":[ 1, 1, 0, 0, 1, 1, 0, 0 ] }, "bend":-1, "born":[ 2, 6 ], "drift":( -1, 0 ), "spark_from":lambda role, outward: role != "front" }
SPARKS = { "0":Material( [ ( 214, 234, 255 ) ], "flat" ), "1":Material( [ ( 170, 208, 255 ) ], "flat", alpha=225 ), "2":Material( [ REFERENCE_BLUE ], "flat", alpha=165 ), "3":Material( [ REFERENCE_BLUE ], "flat", alpha=95 ) }
# Idle with the flame ring turning: one tongue further every 8 frames, a slow 1 px float, no blink (it never stops
# watching).
SPIN_BOB = [ 0, 0, 0, 1, 1, 1, 1, 0 ]
PROFILE_BINS = 720
SPIN_IDLE = [ Frame( states={ "flames":f"spin{index}", "fire":f"spin{index}", "sparks":f"spin{index}" }, bob=SPIN_BOB[ index ] ) for index in range( 8 ) ]
# Float: the flames stream backward over the top and the bottom, sparks drift back, the pupil looks 1 px ahead.
STREAM_FLOAT = [ Frame( { "pupil":( 1, 0 ), "glint":( 1, 0 ) }, { "flames":f"stream{index}", "fire":f"stream{index}", "sparks":f"stream{index}" }, SPIN_BOB[ index ] ) for index in range( 8 ) ]
LIT_47 = { **EDITED_107, "colors_47":True, "silhouette":SILHOUETTE_LEFT_47, "tongues_47":True, "outline":True, "open_gaps":False }
# Richer gold: deepest gold where the light falls, softening with distance from it (to pale gold, or into light blue).
RICH_GOLD = Material( [ ( 232, 172, 52 ), ( 240, 190, 84 ), ( 238, 204, 124 ), ( 226, 210, 160 ), ( 205, 205, 185 ) ], light=FLAME_LIGHT, step=8 )
RICH_GOLD_TO_BLUE = Material( [ ( 232, 172, 52 ), ( 240, 190, 84 ), ( 228, 206, 140 ), ( 170, 196, 230 ), ( 127, 189, 255 ) ], light=FLAME_LIGHT, step=8 )
# Gold that melts into the light blue as smoothly as the white rim does: eight even steps from deep gold to the
# border blue, the blue reached about where the white rim reaches it.
GOLD_BLUE_STEPS = [ tuple( round( gold + ( blue - gold ) * step / 7 ) for gold, blue in zip( ( 232, 172, 52 ), ( 127, 189, 255 ) ) ) for step in range( 8 ) ]
SMOOTH_GOLD_TO_BLUE = Material( GOLD_BLUE_STEPS, light=FLAME_LIGHT, step=4 )
SLOW_GOLD_TO_BLUE = Material( GOLD_BLUE_STEPS, light=FLAME_LIGHT, step=5 )
FRESH_THINNEST = { **FRESH_NAVY, "dark_px":0.7, "rest_limits":[ 0.3, 0.65 ] }
DARKER_47 = { "t":"b", "b":"m", "r":"d", "m":"d", "d":"n" }

# 110-119 again with 47's shading toward the bottom-right (become 120-129).
SHADED_SOURCES = {
  "110_edited_107": EDITED_107,
  "111_edited_107_dark_rim": { **EDITED_107, "dark_rim":1 },
  "112_edited_107_darker_rim": { **EDITED_107, "dark_rim":2 },
  "113_edited_107_black": { **EDITED_107, "outline":True, "open_gaps":False },
  "114_edited_107_dark_rim_black": { **EDITED_107, "dark_rim":1, "outline":True, "open_gaps":False },
  "115_edited_107_darker_rim_black": { **EDITED_107, "dark_rim":2, "outline":True, "open_gaps":False },
  "116_white_double_border": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( WHITE_RIM, "all" ) },
  "117_gold_double_border": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( GOLD_RIM, "all" ) },
  "118_white_lit_rim": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( WHITE_RIM, "lit" ) },
  "119_gold_lit_rim": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( GOLD_RIM, "lit" ) },
}

# Numbered tries, one per proposal; `python generator.py still <name>` renders one into _work/ for review.
# Animations and exports wait until the user approves the base frame.
VARIANTS = {
  "1_flame_ring": {},
  "2_flame_head": { "flame_head":True },
  "3_wild_flames": { "flame_head":True, "head":BLUE_RING_HEAD, "front_tongues":True, "streaks":0.4, "wide_pupil":True },
  "4_blue_ring": { "flame_head":True, "head":BLUE_RING_HEAD, "streaks":0.45, "wide_pupil":True, "ring":BIG_TONGUE_RING },
  "5_fire_streaks": FIRE_HEAD,
  "6_no_border": { **FIRE_HEAD, "head":replace( BLUE_RING_HEAD, border=NO_BORDER ) },
  "7_shadow_arc": { **FIRE_HEAD, "head":replace( BLUE_RING_HEAD, border=SHADOW_ARC ) },
  "8_dashed_navy": { **FIRE_HEAD, "head":replace( BLUE_RING_HEAD, border=DASHED_NAVY ) },
  "9_glow_rim": { **FIRE_HEAD, "head":replace( BLUE_RING_HEAD, border=GLOW_RIM ) },
  "10_navy_line": { **FIRE_HEAD, "head":replace( BLUE_RING_HEAD, border=NAVY_LINE ) },
  "11_flame_core": { **FIRE_HEAD, "head":replace( BLUE_RING_HEAD, border=NO_BORDER ), "flame_core":True },
  "12_big_eye_bands": { **FIRE_HEAD, "head":replace( BLUE_RING_HEAD, border=NO_BORDER ), "big_eye":True },
  "13_flame_core_big_eye": { **FIRE_HEAD, "head":replace( BLUE_RING_HEAD, border=NO_BORDER ), "big_eye":True, "mixed":True },
  "14_cloudy": { **FIRE_HEAD, "head":replace( BLUE_RING_HEAD, border=NO_BORDER ), "big_eye":True, "cloudy":True, "ring":PEAK_RING },
  "15_dark_cloudy": { **FIRE_HEAD, "head":replace( BLUE_RING_HEAD, border=NO_BORDER ), "big_eye":True, "cloudy":True, "ring":PEAK_RING, "dark":True },
  "16_soft_dark": { **FIRE_HEAD, "head":replace( BLUE_RING_HEAD, border=NO_BORDER ), "big_eye":True, "cloudy":True, "ring":PEAK_RING, "dark":"soft" },
  "17_wild_edge": { **FIRE_HEAD, "head":replace( BLUE_RING_HEAD, border=NO_BORDER ), "big_eye":True, "cloudy":True, "ring":WILD_RING, "dark":True },
  "18_rising_tongues": { **FIRE_HEAD, "head":replace( BLUE_RING_HEAD, border=NO_BORDER ), "big_eye":True, "cloudy":True, "ring":PLACED_RING, "dark":True },
  "19_billows_6": { **SOFT_DARK, "ring":BILLOWS_6 },
  "20_billows_7_shaky": { **SOFT_DARK, "ring":BILLOWS_7 },
  "21_billows_5_wobbly": { **SOFT_DARK, "ring":BILLOWS_5 },
  "22_billows_8_lean": { **SOFT_DARK, "ring":BILLOWS_8 },
  "23_sparse_10": { **SOFT_DARK, "ring":SPARSE_10 },
  "24_sparse_12_curl": { **SOFT_DARK, "ring":SPARSE_12 },
  "25_sparse_9_rising": { **SOFT_DARK, "ring":SPARSE_9 },
  "26_sparse_11_long_short": { **SOFT_DARK, "ring":SPARSE_11 },
  "27_small_embers": { **SOFT_DARK, "ring":SMALL_PEAK_RING, "embers":EMBERS_LIGHT },
  "28_small_mixed_embers": { **SOFT_DARK, "ring":SMALL_PEAK_RING, "embers":EMBERS_MIXED },
  "29_tiny_embers": { **SOFT_DARK, "ring":TINY_PEAK_RING, "embers":EMBERS_MIXED },
  "30_shrink_1_tall": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_1 ), "ring":TALL_RING_1, "embers":EMBERS_MIXED },
  "31_shrink_2_tall": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":TALL_RING_2, "embers":EMBERS_MIXED },
  "32_light_1": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_1 ), "ring":PEAK_RING_1 },
  "33_light_2": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":PEAK_RING_2 },
  "34_light_1_shaky": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_1 ), "ring":SHAKY_RING_1 },
  "35_light_2_shaky": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":SHAKY_RING_2 },
  "36_circle_tongues_10": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=EDGE_ONLY ), "ring":CIRCLE_TONGUES_10 },
  "37_circle_tongues_8": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=EDGE_ONLY ), "ring":CIRCLE_TONGUES_8 },
  "38_circle_tongues_12": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=EDGE_ONLY ), "ring":CIRCLE_TONGUES_12 },
  "39_ghost_crown": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=EDGE_ONLY ), "ring":GHOST_CROWN },
  "40_ghost_trail": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=EDGE_ONLY ), "ring":GHOST_TRAIL },
  "41_ghost_candle": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=EDGE_ONLY ), "ring":GHOST_CANDLE },
  "42_steady_9": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=EDGE_ONLY ), "ring":STEADY_9 },
  "43_steady_placed": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=EDGE_ONLY ), "ring":STEADY_PLACED },
  "44_steady_8_round": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=EDGE_ONLY ), "ring":STEADY_8_ROUND },
  "45_balanced_1": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_1 ), "ring":BALANCED_1 },
  "46_balanced_2": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":BALANCED_2 },
  "47_balanced_2_thick": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":BALANCED_2_THICK },
  "48_noisy_near": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":BALANCED_2_NEAR, "noise":0.9 },
  "49_grainy_near": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":BALANCED_2_NEAR, "noise":1.5 },
  "50_noisy_round": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":BALANCED_2_ROUND, "noise":1.2 },
  "51_round_airy": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":ROUND_10, "noise":0.9, "speckle":0.3, "light_flames":True },
  "52_round_8_airy": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":ROUND_8, "noise":0.9, "speckle":0.45, "light_flames":True },
  "53_round_speckled": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":ROUND_10_SOFT, "noise":0.9, "speckle":0.35 },
  "54_47_rounded_noisy": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":ROUNDED_47, "bands":BAND_MATERIALS, "noise":0.9, "speckle":0.3 },
  "55_47_rounded_grainy": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":ROUNDED_47, "bands":BAND_MATERIALS, "noise":1.3, "speckle":0.45 },
  "56_47_rounder_ragged": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":ROUNDER_47, "bands":BAND_MATERIALS, "cloudy":False, "noise":0.9, "speckle":0.3 },
  "57_combined_12_gradient": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":COMBINED_RING, "bands":BAND_MATERIALS, "edge":BODY_EDGE },
  "58_combined_47_gradient": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":COMBINED_RING, "edge":BODY_EDGE },
  "59_combined_ragged_gradient": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":COMBINED_RING, "bands":BAND_MATERIALS, "cloudy":False, "edge":BODY_EDGE },
  "60_smooth_up": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":SMOOTH_RING_UP, "cloudy":False, "edge":BODY_EDGE, "limits":SMOOTH_LIMITS, "flames":SMOOTH_FLAMES },
  "61_smooth": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":SMOOTH_RING, "cloudy":False, "edge":BODY_EDGE, "limits":SMOOTH_LIMITS, "flames":SMOOTH_FLAMES },
  "62_smooth_up_cloudy": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":SMOOTH_RING_UP, "edge":BODY_EDGE, "limits":SMOOTH_LIMITS, "flames":SMOOTH_FLAMES },
  "63_47_colors_54_flames": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":CREST_RING },
  "64_47_colors_54_flames_narrow": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":CREST_RING_NARROW },
  "65_shifted": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":SHIFTED_CREST },
  "66_shifted_thin": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":THIN_CREST },
  "67_shifted_thin_short": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":SHORT_CREST },
  "68_lifted": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":LIFTED_CREST },
  "69_lifted_more": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":LIFTED_MORE_CREST },
  "70_lifted_less": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":LIFTED_LESS_CREST },
  "71_lifted_slight": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":LIFTED_SLIGHT_CREST },
  "72_glow_dotted": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":CHAOTIC_CREST, "outline":GLOW_EDGE, "open_gaps":True, "speckle":0.2 },
  "73_glow_transparent": { **SOFT_DARK, "head":replace( BLUE_RING_HEAD, border=SHRINK_2 ), "ring":CHAOTIC_CREST, "outline":GLOW_EDGE_SOFT, "open_gaps":True, "speckle":0.2, "flames":GLOW_FLAMES },
  "74_reference_palette": REFERENCE_LOOK,
  "75_reference_chaotic": { **REFERENCE_LOOK, "ring":CHAOTIC_CREST, "speckle":0.2 },
  "76_reference_dotted_edge": { **REFERENCE_LOOK, "outline":LIGHT_EDGE_DOTTED },
  "77_light_reference": { **REFERENCE_LOOK, "bands":LIGHT_REFERENCE_BANDS, "flames":LIGHT_REFERENCE_FLAMES },
  "78_light_chaotic": { **REFERENCE_LOOK, "bands":LIGHT_REFERENCE_BANDS, "flames":LIGHT_REFERENCE_FLAMES, "ring":CHAOTIC_CREST, "speckle":0.2 },
  "79_light_dotted_edge": { **REFERENCE_LOOK, "bands":LIGHT_REFERENCE_BANDS, "flames":LIGHT_REFERENCE_FLAMES, "outline":LIGHT_EDGE_DOTTED },
  "80_full_gradient_4": { **REFERENCE_LOOK, "gradient":GRADIENT_4 },
  "81_full_gradient_5": { **REFERENCE_LOOK, "gradient":GRADIENT_5 },
  "82_full_gradient_4_soft": { **REFERENCE_LOOK, "gradient":GRADIENT_4, "dither":0.08 },
  "83_inner_flames_4": { **REFERENCE_LOOK, "gradient":GRADIENT_4, "inner":INNER_FLAMES },
  "84_inner_flames_5": { **REFERENCE_LOOK, "gradient":GRADIENT_5, "inner":INNER_FLAMES },
  "85_inner_flames_wild": { **REFERENCE_LOOK, "gradient":GRADIENT_4, "inner":WILD_INNER_FLAMES },
  "86_light_rim": { **REFERENCE_LOOK, "gradient":INSIDE_TONES, "inner":WILD_INNER_FLAMES },
  "87_light_rim_dotted": { **REFERENCE_LOOK, "gradient":INSIDE_TONES, "inner":WILD_INNER_FLAMES, "outline":LIGHT_EDGE_DOTTED },
  "88_light_rim_lit_side": { **REFERENCE_LOOK, "gradient":INSIDE_TONES, "inner":WILD_INNER_FLAMES, "outline":LIT_EDGE },
  "89_random_turns": { **REFERENCE_LOOK, "gradient":INSIDE_TONES, "inner":RANDOM_INNER, "outline":LIT_EDGE },
  "90_random_turns_wild": { **REFERENCE_LOOK, "gradient":INSIDE_TONES, "inner":RANDOM_INNER_WILD, "outline":LIT_EDGE },
  "91_random_turns_other": { **REFERENCE_LOOK, "gradient":INSIDE_TONES, "inner":RANDOM_INNER_OTHER, "outline":LIT_EDGE },
  "92_random_outer": { **REFERENCE_LOOK, "gradient":INSIDE_TONES, "inner":WILD_INNER_FLAMES, "outline":LIT_EDGE, "upper_back_from_47":True, "random_flames":RANDOM_FLAMES },
  "93_random_outer_wild": { **REFERENCE_LOOK, "gradient":INSIDE_TONES, "inner":WILD_INNER_FLAMES, "outline":LIT_EDGE, "upper_back_from_47":True, "random_flames":RANDOM_FLAMES_WILD },
  "94_random_outer_other": { **REFERENCE_LOOK, "gradient":INSIDE_TONES, "inner":WILD_INNER_FLAMES, "outline":LIT_EDGE, "upper_back_from_47":True, "random_flames":RANDOM_FLAMES_OTHER },
  "95_calm_47_back": VARIANTS_95,
  "96_calm_gentle": { **REFERENCE_LOOK, "gradient":INSIDE_TONES, "inner":WILD_INNER_FLAMES, "outline":LIT_EDGE, "upper_back_from_47":True, "random_flames":GENTLE_FLAMES, "calm_top_right":True },
  "97_calm_lean": { **REFERENCE_LOOK, "gradient":INSIDE_TONES, "inner":WILD_INNER_FLAMES, "outline":LIT_EDGE, "upper_back_from_47":True, "random_flames":GENTLE_LEAN, "calm_top_right":True },
  "98_lower_back_47": { **VARIANTS_95, "lower_back":[ BALANCED_2_THICK ] },
  "99_lower_back_curl": { **VARIANTS_95, "lower_back":LOWER_BACK_CURL },
  "100_lower_back_short": { **VARIANTS_95, "lower_back":LOWER_BACK_SHORT },
  "101_squeezed_47": { **VARIANTS_95, "squeeze":SQUEEZE, "lower_back":[ BALANCED_2_THICK ] },
  "102_squeezed_four_round": { **VARIANTS_95, "squeeze":SQUEEZE, "lower_back":LOWER_BACK_FOUR_ROUND },
  "103_squeezed_four_peak": { **VARIANTS_95, "squeeze":SQUEEZE, "lower_back":LOWER_BACK_FOUR_PEAK },
  "104_edited_chaotic": { **VARIANTS_95, "silhouette":SILHOUETTE_101_2, "eye_at":RAISED_EYE, "inner":CHAOTIC_INNER, "tone_chaos":0.12 },
  "105_edited_more_chaotic": { **VARIANTS_95, "silhouette":SILHOUETTE_101_2, "eye_at":RAISED_EYE, "inner":CHAOTIC_INNER, "tone_chaos":0.22 },
  "106_edited_chaotic_other": { **VARIANTS_95, "silhouette":SILHOUETTE_101_2, "eye_at":RAISED_EYE, "inner":CHAOTIC_INNER_OTHER, "tone_chaos":0.15 },
  "107_nudged_calm": { **VARIANTS_95, "silhouette":SILHOUETTE_NUDGED, "eye_at":RAISED_EYE, "inner":CALM_INNER },
  "108_nudged_calm_soft": { **VARIANTS_95, "silhouette":SILHOUETTE_NUDGED, "eye_at":RAISED_EYE, "inner":CALM_INNER, "dither":0.06 },
  "109_nudged_smooth": { **VARIANTS_95, "silhouette":SILHOUETTE_NUDGED, "eye_at":RAISED_EYE, "inner":None, "dither":0.08 },
  "110_edited_107": EDITED_107,
  "111_edited_107_dark_rim": { **EDITED_107, "dark_rim":1 },
  "112_edited_107_darker_rim": { **EDITED_107, "dark_rim":2 },
  "113_edited_107_black": { **EDITED_107, "outline":True, "open_gaps":False },
  "114_edited_107_dark_rim_black": { **EDITED_107, "dark_rim":1, "outline":True, "open_gaps":False },
  "115_edited_107_darker_rim_black": { **EDITED_107, "dark_rim":2, "outline":True, "open_gaps":False },
  "116_white_double_border": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( WHITE_RIM, "all" ) },
  "117_gold_double_border": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( GOLD_RIM, "all" ) },
  "118_white_lit_rim": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( WHITE_RIM, "lit" ) },
  "119_gold_lit_rim": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( GOLD_RIM, "lit" ) },
  **{ f"{120 + index}_{name.split( "_", 1 )[ 1 ]}_shaded":{ **options, "shaded":True } for index, ( name, options ) in enumerate( SHADED_SOURCES.items() ) },
  **{ f"{130 + index}_{name.split( "_", 1 )[ 1 ]}_47_blues":{ **options, "colors_47":True } for index, ( name, options ) in enumerate( SHADED_SOURCES.items() ) },
  **{ f"{140 + index}_{name.split( "_", 1 )[ 1 ]}_47_flame":{ **options, "colors_47":True, "silhouette":SILHOUETTE_LEFT_47 } for index, ( name, options ) in enumerate( SHADED_SOURCES.items() ) },
  **{ f"{150 + index}_{name.split( "_", 1 )[ 1 ]}_outside":{ **options, "colors_47":True, "silhouette":SILHOUETTE_LEFT_47, "outer_rim":OUTER_RIMS[ name ] } for index, ( name, options ) in enumerate( SHADED_SOURCES.items() ) if name in OUTER_RIMS },
  **{ f"{160 + index * 2 + offset}_{name.split( "_", 2 )[ 1 ]}_rim_{style}":{ **SHADED_SOURCES[ name ], "colors_47":True, "silhouette":SILHOUETTE_LEFT_47, "outer_rim":rim } for index, name in enumerate( FADED_RIMS ) for offset, ( style, rim ) in enumerate( FADED_RIMS[ name ] ) },
  "164_white_to_blue": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( WHITE_TO_BLUE, "all" ) },
  "165_gold_to_blue": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( GOLD_TO_BLUE, "all" ) },
  "166_white_to_blue_47": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( WHITE_TO_BLUE, "all" ), "colors_47":True, "silhouette":SILHOUETTE_LEFT_47, "outer_rim":( "all", "w" ) },
  "167_gold_to_blue_47": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( GOLD_TO_BLUE, "all" ), "colors_47":True, "silhouette":SILHOUETTE_LEFT_47, "outer_rim":( "all", "w" ) },
  "168_gold_cream_blue": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( GOLD_CREAM_BLUE, "all" ) },
  "169_gold_cream_blue_47": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( GOLD_CREAM_BLUE, "all" ), "colors_47":True, "silhouette":SILHOUETTE_LEFT_47, "outer_rim":( "all", "w" ) },
  "170_gold_pale_yellow": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( GOLD_PALE_YELLOW, "all" ) },
  "171_gold_pale_yellow_47": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( GOLD_PALE_YELLOW, "all" ), "colors_47":True, "silhouette":SILHOUETTE_LEFT_47, "outer_rim":( "all", "w" ) },
  "172_white_to_blue_lit": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( WHITE_TO_BLUE, "lit", RIM_FADE ) },
  "173_white_to_blue_lit_47": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( WHITE_TO_BLUE, "lit" ), "colors_47":True, "silhouette":SILHOUETTE_LEFT_47, "outer_rim":( "lit", "w", RIM_FADE ) },
  "174_gold_yellow_lit": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( GOLD_PALE_YELLOW, "lit", RIM_FADE ) },
  "175_gold_yellow_lit_47": { **EDITED_107, "outline":True, "open_gaps":False, "highlight":( GOLD_PALE_YELLOW, "lit" ), "colors_47":True, "silhouette":SILHOUETTE_LEFT_47, "outer_rim":( "lit", "w", RIM_FADE ) },
  **{ f"{176 + index}_{name.split( "_", 1 )[ 1 ]}_from_47":{ **options, "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, **( { "outer_rim":OUTER_RIMS[ name ] } if name in OUTER_RIMS else {} ) } for index, ( name, options ) in enumerate( list( SHADED_SOURCES.items() )[ :6 ] ) },
  "182_smooth_178": { **SHADED_SOURCES[ "110_edited_107" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":SMOOTH_FLAT },
  "183_smooth_181": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "outer_rim":OUTER_RIMS[ "113_edited_107_black" ], "smooth":SMOOTH_FLAT },
  "184_smooth_shaded_178": { **SHADED_SOURCES[ "110_edited_107" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":SMOOTH_SHADED },
  "185_smooth_shaded_181": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "outer_rim":OUTER_RIMS[ "113_edited_107_black" ], "smooth":SMOOTH_SHADED },
  "186_fresh_navy_black": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":FRESH_NAVY },
  "187_fresh_dark_black": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":FRESH_DARK },
  "188_fresh_navy_open": { **SHADED_SOURCES[ "110_edited_107" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":FRESH_NAVY, "outline":False },
  "189_fresh_thin_dark": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":FRESH_THIN },
  "190_fresh_thinnest_dark": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":FRESH_THINNEST },
  "191_fresh_middle_dark": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":FRESH_MIDDLE },
  "192_fresh_middle_wide_dark": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":FRESH_MIDDLE_WIDE },
  "193_even_ramp": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":FRESH_EVEN },
  "194_even_ramp_soft": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":FRESH_EVEN_SOFT },
  "195_even_ramp_6": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":FRESH_EVEN_6 },
  "196_deeper_dark": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":FRESH_DEEPER },
  "197_deeper_volume": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":FRESH_VOLUME },
  "198_deeper_volume_strong": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":FRESH_VOLUME_STRONG },
  "199_dimmed_deeper": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":{ **FRESH_DEEPER, **DIMMED } },
  "200_dimmed_volume": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":{ **FRESH_VOLUME, **DIMMED } },
  "201_dimmed_volume_strong": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":{ **FRESH_VOLUME_STRONG, **DIMMED } },
  "202_bright_border": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":{ **FRESH_VOLUME_STRONG, **DIMMED, "border":BRIGHT_BORDER } },
  "203_bright_even": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":{ **FRESH_VOLUME_STRONG, "tones":EVEN_DIMMED_RAMP[ 1: ], "border":EVEN_DIMMED_RAMP[ 0 ] } },
  "204_dimmed_volume_strong_lit": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":{ **FRESH_VOLUME_STRONG, **DIMMED, "light":0.12 } },
  "205_bright_border_lit": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":{ **FRESH_VOLUME_STRONG, **DIMMED, "border":BRIGHT_BORDER, "light":0.12 } },
  "206_bright_even_lit": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":{ **FRESH_VOLUME_STRONG, "tones":EVEN_DIMMED_RAMP[ 1: ], "border":EVEN_DIMMED_RAMP[ 0 ], "light":0.12 } },
  "207_vibrant_volume_strong_lit": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":{ **FRESH_VOLUME_STRONG, **VIBRANT_DIMMED, "light":0.12 } },
  "208_vibrant_bright_border_lit": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":{ **FRESH_VOLUME_STRONG, **VIBRANT_BRIGHT, "light":0.12 } },
  "209_vibrant_bright_even_lit": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":{ **FRESH_VOLUME_STRONG, **VIBRANT_EVEN, "light":0.12 } },
  "210_vibrant_47_light": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":{ **FRESH_DEEPER, **VIBRANT_EVEN, **LIGHT_47 } },
  "211_vibrant_47_light_strong": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":{ **FRESH_DEEPER, **VIBRANT_EVEN, **LIGHT_47, "light_step":11 } },
  "212_vibrant_47_light_ball": { **SHADED_SOURCES[ "113_edited_107_black" ], "transfer_47":True, "silhouette":SILHOUETTE_LEFT_47, "smooth":{ **FRESH_DEEPER, **VIBRANT_EVEN, "light_point":( 4, 2 ), "light_step":9, "light_offset":0 } },
  "213_lit_like_47": LIT_47,
  "214_lit_like_47_vibrant": { **LIT_47, "ramp_47":VIBRANT_47_RAMP },
  "215_lit_like_47_rim": { **LIT_47, "outer_rim":( "lit", "l" ) },
  "216_lit_like_47_white_black": { **LIT_47, "outer_rim":( "all", "w" ), "highlight":( WHITE_RIM, "all" ) },
  "217_lit_like_47_no_border": { **LIT_47, "outline":False, "open_gaps":True },
  "218_lit_like_47_blue_border": { **LIT_47, "outer_rim":( "all", "t" ), "outline":False, "open_gaps":True },
  "219_lit_like_47_blue_glow": { **LIT_47, "outline":( 30, 80, 230, 170 ), "open_gaps":True },
  "220_lit_like_47_blue_glow_soft": { **LIT_47, "outline":( 30, 80, 230, 110 ), "open_gaps":True },
  "221_lit_like_47_blue_glow_deep": { **LIT_47, "outline":( 15, 45, 180, 210 ), "open_gaps":True },
  "222_lit_white_rim_outside": { **LIT_47, "outer_rim":( "lit", "w", RIM_FADE ), "highlight":( WHITE_TO_BLUE, "lit" ) },
  "223_lit_white_rim_inside": { **LIT_47, "highlight":( WHITE_TO_BLUE, "lit", RIM_FADE ) },
  "224_lit_white_rim_short": { **LIT_47, "outer_rim":( "lit", "w", ( 14, 24 ) ), "highlight":( WHITE_TO_BLUE, "lit" ) },
  "225_lit_gold_ring": { **LIT_47, "outer_rim":( "all", "w" ), "highlight":( GOLD_PALE_YELLOW, "all" ) },
  "226_lit_gold_rim_outside": { **LIT_47, "outer_rim":( "lit", "w", RIM_FADE ), "highlight":( GOLD_PALE_YELLOW, "lit" ) },
  "227_lit_gold_rim_inside": { **LIT_47, "highlight":( GOLD_PALE_YELLOW, "lit", RIM_FADE ) },
  "228_lit_gold_rim_short": { **LIT_47, "outer_rim":( "lit", "w", ( 14, 24 ) ), "highlight":( GOLD_PALE_YELLOW, "lit" ) },
  "229_rich_gold_ring": { **LIT_47, "outer_rim":( "all", "w" ), "highlight":( RICH_GOLD, "all" ) },
  "230_rich_gold_rim_outside": { **LIT_47, "outer_rim":( "lit", "w", RIM_FADE ), "highlight":( RICH_GOLD, "lit" ) },
  "231_rich_gold_rim_short": { **LIT_47, "outer_rim":( "lit", "w", ( 14, 24 ) ), "highlight":( RICH_GOLD, "lit" ) },
  "232_rich_gold_to_blue_rim": { **LIT_47, "outer_rim":( "lit", "w", RIM_FADE ), "highlight":( RICH_GOLD_TO_BLUE, "lit" ) },
  "233_gold_melts_to_blue": { **LIT_47, "outer_rim":( "lit", "w", RIM_FADE ), "highlight":( SMOOTH_GOLD_TO_BLUE, "lit" ) },
  "234_gold_melts_to_blue_slow": { **LIT_47, "outer_rim":( "lit", "w", RIM_FADE ), "highlight":( SLOW_GOLD_TO_BLUE, "lit" ) },
  "235_evolveye": { **LIT_47, "outer_rim":( "lit", "w", RIM_FADE ), "highlight":( WHITE_TO_BLUE, "lit" ), "flicker":{ "idle":IDLE_TIPS, "float":FLOAT_TIPS } },
  "236_evolveye_sparks": { **LIT_47, "outer_rim":( "lit", "w", RIM_FADE ), "highlight":( WHITE_TO_BLUE, "lit" ), "flow":{ "idle":IDLE_FLOW, "float":FLOAT_FLOW } },
  "237_evolveye_spin": { **LIT_47, "outer_rim":( "lit", "w", RIM_FADE ), "highlight":( WHITE_TO_BLUE, "lit" ), "spin":8, "animations":{ "idle":Animation( SPIN_IDLE, ms=180 ) } },
  "238_evolveye_spin_sparks": { **LIT_47, "outer_rim":( "lit", "w", RIM_FADE ), "highlight":( WHITE_TO_BLUE, "lit" ), "spin":8, "spin_sparks":True, "animations":{ "idle":Animation( SPIN_IDLE, ms=180 ) } },
  "239_evolveye_stream": { **LIT_47, "outer_rim":( "lit", "w", RIM_FADE ), "highlight":( WHITE_TO_BLUE, "lit" ), "spin":8, "spin_sparks":True, "stream":8, "animations":{ "idle":Animation( SPIN_IDLE, ms=180 ), "float":Animation( STREAM_FLOAT, ms=140 ) } },
  "240_evolveye_flat_front": { **LIT_47, "outer_rim":( "lit", "w", RIM_FADE ), "highlight":( WHITE_TO_BLUE, "lit" ), "spin":8, "spin_sparks":True, "stream":8, "stream_squash":0.85, "animations":{ "idle":Animation( SPIN_IDLE, ms=180 ), "float":Animation( STREAM_FLOAT, ms=140 ) } },
}
FINAL = VARIANTS[ "240_evolveye_flat_front" ]

# Idle: the tongues creep around the ring while the eye floats and blinks.
# Idle: tips flicker 1 px out and in, each tongue at its own time; a slow 1 px float; one blink.
IDLE_BOB = [ 0, 0, 0, 1, 1, 1, 1, 0 ]
IDLE = [ Frame( states={ "flames":f"idle{index}", "fire":f"idle{index}", "sparks":f"idle{index}" }, bob=IDLE_BOB[ index ] ) for index in range( 8 ) ]
IDLE = [ Frame( frame.offsets, { **frame.states, "pupil":"closed", "glint":"closed" }, frame.bob ) if index == 5 else frame for index, frame in enumerate( IDLE ) ]

# Float: a 2 px bob, the pupil looking 1 px ahead, the back tongues trailing longer and the front ones shorter.
FLOAT_BOB = [ 0, 1, 1, 2, 2, 1, 1, 0 ]
FLOAT_LOOK = { "pupil":( 1, 0 ), "glint":( 1, 0 ) }
FLOAT = [ Frame( FLOAT_LOOK, { "flames":f"float{index}", "fire":f"float{index}", "sparks":f"float{index}" }, FLOAT_BOB[ index ] ) for index in range( 8 ) ]
ANIMATIONS = {
  "idle": Animation( IDLE, ms=180 ),
  "float": Animation( FLOAT, ms=140 ),
}


def parts( facing:str, options:dict ):
  # Authored facing right; the engine mirrors and re-shades the left side.
  if options.get( "transfer_47" ): return transfer_47_parts( facing, options )
  if options.get( "flame_head" ): return flame_head_parts( options, facing )

  flame_states = { f"phase{index}":flame_grid( RING, index / 8 ) for index in range( 8 ) }

  return [
    Part( "pupil", PUPIL_GRID, ( 14, 7 ), { "x":PUPIL }, depth="face", states={ "closed":PUPIL_CLOSED } ),
    Part( "glint", GLINT_GRID, ( 17, 8 ), { "x":GLINT }, depth="face" ),
    Part( "flames", flame_grid( RING, 0 ), ( -CANVAS.margin_x, -CANVAS.top ), { "t":FLAME_TIP, "b":FLAME_BODY, "r":FLAME_ROOT }, depth="behind", states=flame_states ),
  ]


def flame_head_parts( options:dict, facing:str = "right" ):
  # The head core is a ball of fire with a smaller eye inside it; flame tongues lick out from behind the head.
  ring = options.get( "ring", TONGUE_RING )
  if options.get( "upper_back_from_47" ): ring = { **ring, "sectors":[ ( -175, -130, [ BALANCED_2_THICK ] ) ] + ring[ "sectors" ] }
  if options.get( "lower_back" ): ring = { **ring, "sectors":[ ( 95, 165, options[ "lower_back" ] ) ] + ring[ "sectors" ] }
  calm = [ sector for sector in ring.get( "sectors", [] ) if sector[ 0 ] >= -90 and sector[ 1 ] <= 25 ]
  if options.get( "random_flames" ): ring = with_random( ring, options[ "random_flames" ] )
  if options.get( "random_flames" ) and options.get( "calm_top_right" ): ring = { **ring, "sectors":calm + ring[ "sectors" ] }
  if options.get( "squeeze" ): ring = { "squeeze":options[ "squeeze" ], "source":ring }
  flame_states = { f"phase{index}":flame_grid( ring, index / 8 ) for index in range( 8 ) }
  flame_palette = { "t":FLAME_TIP, "b":FLAME_BODY, "r":FLAME_ROOT }
  eye_column, eye_row = SMALL_EYE_AT

  pupil = Part( "pupil", SMALL_PUPIL, ( eye_column + 5, eye_row + 3 ), { "x":PUPIL }, depth="face", states={ "closed":SMALL_PUPIL_CLOSED } )
  glint = Part( "glint", GLINT_GRID, ( eye_column + 7, eye_row + 4 ), { "x":GLINT }, depth="face" )
  if options.get( "wide_pupil" ): pupil = Part( "pupil", WIDE_PUPIL, ( eye_column + 4, eye_row + 3 ), { "x":PUPIL }, depth="face", states={ "closed":WIDE_PUPIL_CLOSED } )
  if options.get( "wide_pupil" ): glint = Part( "glint", GLINT_GRID, ( eye_column + 7, eye_row + 4 ), { "x":GLINT }, depth="face" )

  fire = Part( "fire", fire_grid( options.get( "streaks", 0.22 ), options.get( "glow", ( 1.5, 3.5 ) ) ), ( 0, 0 ), options.get( "fire", FIRE_MATERIALS ), depth="face" )
  if options.get( "flame_core" ): fire = Part( "fire", flame_core_grid(), ( 0, 0 ), flame_palette, depth="face" )
  if options.get( "big_eye" ) and options.get( "embers" ): return big_eye_parts( ring, flame_states, options.get( "mixed" ), options.get( "cloudy" ), options.get( "dark" ), options.get( "noise", 0 ), options.get( "speckle", 0 ), options.get( "light_flames" ), options.get( "bands" ), options.get( "edge" ), options.get( "limits" ), options.get( "flames" ) ) + [ embers_part( ring, options[ "embers" ] ) ]
  if options.get( "colors_47" ): return colors_47_parts( options, facing )
  if options.get( "gradient" ): return gradient_parts( ring, options )
  if options.get( "big_eye" ) and options.get( "outline" ): return outlined( big_eye_parts( ring, flame_states, options.get( "mixed" ), options.get( "cloudy" ), options.get( "dark" ), options.get( "noise", 0 ), options.get( "speckle", 0 ), options.get( "light_flames" ), options.get( "bands" ), options.get( "edge" ), options.get( "limits" ), options.get( "flames" ) ), options[ "outline" ] )
  if options.get( "big_eye" ): return big_eye_parts( ring, flame_states, options.get( "mixed" ), options.get( "cloudy" ), options.get( "dark" ), options.get( "noise", 0 ), options.get( "speckle", 0 ), options.get( "light_flames" ), options.get( "bands" ), options.get( "edge" ), options.get( "limits" ), options.get( "flames" ) )

  items = [
    fire,
    Part( "eye", eye_white_grid(), SMALL_EYE_AT, EYE_WHITE, depth="face" ),
    pupil,
    glint,
    Part( "flames", flame_grid( ring, 0 ), ( -CANVAS.margin_x, -CANVAS.top ), flame_palette, depth="behind", states=flame_states ),
  ]
  if options.get( "front_tongues" ): items.append( Part( "tongues", tongue_tips_grid( 0 ), ( -CANVAS.margin_x, -CANVAS.top ), flame_palette ) )

  return items


def transfer_47_parts( facing:str, options:dict ):
  # 47's own rendered blues moved onto the edited silhouette: every pixel takes the colour 47 has at the same share of
  # the way from the eye's edge to the outer edge, in the same direction, so 47's dark-centre-to-light-edge gradient
  # and its top-left light come along unchanged (sampled from 47's sprite for this facing, mirrored back to the right).
  shape = edited( options[ "silhouette" ], { point:( "." if symbol == "." else "x" ) for point, symbol in options.get( "edits", {} ).items() } )
  colors = sampled_47_colors( shape, options[ "eye_at" ], facing )
  if options.get( "smooth" ): colors = smooth_colors( shape, options[ "eye_at" ], options[ "smooth" ] )
  speck_tones = SPECK_47
  if options.get( "smooth", {} ).get( "ramp_specks" ): speck_tones = { "2":options[ "smooth" ][ "tones" ][ -1 ], "1":options[ "smooth" ][ "tones" ][ -2 ], "0":options[ "smooth" ][ "tones" ][ 0 ] }
  specks = { point:speck_tones[ symbol ] for point, symbol in options.get( "edits", {} ).items() if symbol != "." }
  colors = { **colors, **{ point:color for point, color in specks.items() if point in colors } }

  # The darker shaded-side edge, then a light rim outside the blue so the black outline goes around it.
  rim_steps = options.get( "dark_rim", 0 )
  edge = { ( column, row ) for column, row in colors if any( ( column + dx, row + dy ) not in colors for dx, dy in ( ( 1, 0 ), ( -1, 0 ), ( 0, 1 ), ( 0, -1 ) ) ) }
  for column, row in edge:
    if rim_steps and light_diagonal( column, row, facing ) > 26: colors[ ( column, row ) ] = tuple( round( channel * 0.8 ** rim_steps ) for channel in colors[ ( column, row ) ] )

  symbols = {}
  grid = [ [ "." ] * len( shape[ 0 ] ) for _ in shape ]
  for ( column, row ), color in colors.items(): grid[ row ][ column ] = symbols.setdefault( color, chr( 192 + len( symbols ) ) )

  body = [ "".join( line ) for line in grid ]
  outer = options.get( "outer_rim" )
  if outer: body = outer_rimmed( body, *outer, facing=facing )

  eye_column, eye_row = options[ "eye_at" ]
  core = [ line[ CANVAS.margin_x:CANVAS.margin_x + 25 ] for line in body[ CANVAS.top:CANVAS.top + 25 ] ]
  palette = { symbol:Material( [ color ], "flat" ) for color, symbol in symbols.items() }
  palette = { **palette, "l":Material( [ REFERENCE_BLUE ], "flat" ), **( { "w":options[ "highlight" ][ 0 ] } if options.get( "highlight" ) else {} ) }

  return [
    Part( "fire", core, ( 0, 0 ), palette, depth="face" ),
    Part( "eye", eye_white_grid( BIG_EYE ), options[ "eye_at" ], BIG_EYE_WHITE, depth="face" ),
    Part( "pupil", BIG_PUPIL, ( eye_column + 5, eye_row + 4 ), { "x":PUPIL }, depth="face", states={ "closed":BIG_PUPIL_CLOSED } ),
    Part( "glint", GLINT_GRID, ( eye_column + 8, eye_row + 5 ), { "x":GLINT }, depth="face" ),
    Part( "flames", body, ( -CANVAS.margin_x, -CANVAS.top ), palette, depth="behind", outline=options.get( "outline", True ) ),
  ]


def smooth_colors( shape:list, eye_at:tuple, smooth:dict ):
  # 47's blues as an even ramp from the eye to the flame tips, with no light direction: the share of the way out picks
  # the tone, the darkest only right by the white, 47's cloudy wobble keeps the band edges soft. `shade` then darkens
  # the outer band on the bottom-right side, more toward the very edge.
  center = ( CANVAS.margin_x + eye_at[ 0 ] + 6, CANVAS.top + eye_at[ 1 ] + 7 )
  pixels = [ ( column, row ) for row, line in enumerate( shape ) for column, symbol in enumerate( line ) if symbol != "." ]
  reach = directional_reach( pixels, center )
  limits = smooth[ "limits" ]
  tones = smooth.get( "tones", SMOOTH_TONES )

  colors = {}
  for column, row in pixels:
    x = column - center[ 0 ]
    y = row - center[ 1 ]
    angle = atan2( y, x )
    eye_reach = 1 / hypot( cos( angle ) / 6.5, sin( angle ) / 7.5 )
    share = ( hypot( x, y ) - eye_reach ) / max( 1, reach[ reach_bin( angle ) ] - eye_reach )
    share += smooth[ "wobble" ] * ( sin( x * 0.9 + y * 0.4 ) + sin( y * 1.1 - x * 0.5 + 1.3 ) + sin( ( x + y ) * 0.6 + 2 ) ) / 3
    tone = next( ( index for index, limit in enumerate( limits ) if share < limit ), len( limits ) )

    # Thin dark ring: the darkest tone only within `dark_px` pixels of the white, the other tones spread over the rest.
    if "dark_px" in smooth:
      gap = hypot( x, y ) - eye_reach + smooth.get( "dither", 0 ) * 4 * pixel_noise( column, row )
      rest = ( gap - smooth[ "dark_px" ] ) / max( 1, reach[ reach_bin( angle ) ] - eye_reach - smooth[ "dark_px" ] )

      # Volume: the lit top-left side runs lighter, the bottom-right darker, like a lit ball.
      rest += smooth.get( "volume", 0 ) * -( x + y ) / max( 1, hypot( x, y ) ) / 1.414
      tone = 0 if gap < smooth[ "dark_px" ] else 1 + next( ( index for index, limit in enumerate( smooth[ "rest_limits" ] ) if rest < limit ), len( smooth[ "rest_limits" ] ) )

    # Shaded border: past `start`, the bottom-right side steps darker toward the edge.
    shade = smooth.get( "shade" )
    if shade:
      facing_away = max( 0, ( x + y ) / max( 1, hypot( x, y ) ) / 1.414 )
      outward = max( 0, share - shade[ "start" ] ) / ( 1 - shade[ "start" ] )
      tone -= round( shade[ "steps" ] * facing_away * outward )

    colors[ ( column, row ) ] = tones[ max( 0, min( len( tones ) - 1, len( tones ) - 1 - tone ) ) ]

  # Light shading: the top-left third of the sprite a little brighter, the bottom-right third a little darker.
  light = smooth.get( "light" )
  if light:
    for ( column, row ), color in colors.items():
      head_x = column - CANVAS.margin_x - 12
      head_y = row - CANVAS.top - 12
      lit = -( head_x + head_y ) / max( 1, hypot( head_x, head_y ) ) / 1.414
      if lit > 0.35: colors[ ( column, row ) ] = tuple( round( channel + ( 255 - channel ) * light ) for channel in color )
      if lit < -0.35: colors[ ( column, row ) ] = tuple( round( channel * ( 1 - light ) ) for channel in color )

  # An optional 1 px border tone on the outermost pixels.
  if "border" in smooth:
    for column, row in pixels:
      if any( ( column + dx, row + dy ) not in colors for dx, dy in ( ( 1, 0 ), ( -1, 0 ), ( 0, 1 ), ( 0, -1 ) ) ): colors[ ( column, row ) ] = smooth[ "border" ]

  # 47's 3D: every pixel steps down the ramp with its distance from a light point at the top-left, so the tones bend
  # into round, ball-like bands instead of following the eye only.
  if "light_point" in smooth:
    ramp = [ smooth[ "border" ] ] + tones + extended_ramp( tones, smooth.get( "extra", 2 ) )
    light_x = CANVAS.margin_x + smooth[ "light_point" ][ 0 ]
    light_y = CANVAS.top + smooth[ "light_point" ][ 1 ]
    for point, color in colors.items():
      steps = int( hypot( point[ 0 ] - light_x, point[ 1 ] - light_y ) / smooth[ "light_step" ] ) - smooth.get( "light_offset", 1 )
      colors[ point ] = ramp[ max( 0, min( len( ramp ) - 1, ramp.index( color ) + steps ) ) ]

  return colors


def extended_ramp( tones:list, count:int ):
  # Darker tones past the end of a ramp, continuing its last step.
  step = [ dark - light for light, dark in zip( tones[ -2 ], tones[ -1 ] ) ]
  return [ tuple( max( 0, channel + delta * ( index + 1 ) ) for channel, delta in zip( tones[ -1 ], step ) ) for index in range( count ) ]


def sampled_47_colors( shape:list, eye_at:tuple, facing:str ):
  # Canvas point -> RGB for every blue pixel of `shape`, taken from 47 at the matching relative position.
  source = render( globals(), facing, Frame(), SOURCE_47 )
  if facing == "left": source = mirrored_sprite( source )

  source_center = ( CANVAS.margin_x + BIG_EYE_AT[ 0 ] + 6, CANVAS.top + BIG_EYE_AT[ 1 ] + 7 )
  target_center = ( CANVAS.margin_x + eye_at[ 0 ] + 6, CANVAS.top + eye_at[ 1 ] + 7 )
  is_blue = lambda color: color[ 3 ] and sum( color[ :3 ] ) > 60 and color[ 2 ] > color[ 0 ] + 40
  source_pixels = { ( x, y ):source.getpixel( ( x, y ) )[ :3 ] for x in range( source.width ) for y in range( source.height ) if is_blue( source.getpixel( ( x, y ) ) ) }
  target_pixels = [ ( column, row ) for row, line in enumerate( shape ) for column, symbol in enumerate( line ) if symbol != "." ]

  source_reach = directional_reach( source_pixels, source_center )
  target_reach = directional_reach( target_pixels, target_center )
  colors = {}
  for column, row in target_pixels:
    angle = atan2( row - target_center[ 1 ], column - target_center[ 0 ] )
    eye_reach = 1 / hypot( cos( angle ) / 6.5, sin( angle ) / 7.5 )
    share = ( hypot( column - target_center[ 0 ], row - target_center[ 1 ] ) - eye_reach ) / max( 1, target_reach[ reach_bin( angle ) ] - eye_reach )
    distance = eye_reach + max( 0, min( 1, share ) ) * ( source_reach[ reach_bin( angle ) ] - eye_reach )
    point = ( round( source_center[ 0 ] + cos( angle ) * distance ), round( source_center[ 1 ] + sin( angle ) * distance ) )
    nearest = lambda other: hypot( other[ 0 ] - point[ 0 ], other[ 1 ] - point[ 1 ] )
    colors[ ( column, row ) ] = source_pixels.get( point ) or source_pixels[ min( source_pixels, key=nearest ) ]

  return colors


def directional_reach( pixels:object, center:tuple ):
  # Farthest pixel per direction around `center`, widened to the neighbouring directions.
  reach = [ 0 ] * GRADIENT_BINS
  for column, row in pixels:
    index = reach_bin( atan2( row - center[ 1 ], column - center[ 0 ] ) )
    reach[ index ] = max( reach[ index ], hypot( column - center[ 0 ], row - center[ 1 ] ) )

  return [ max( reach[ ( index + offset ) % GRADIENT_BINS ] for offset in ( -1, 0, 1 ) ) for index in range( GRADIENT_BINS ) ]


def reach_bin( angle:float ):
  return int( ( angle + pi ) / ( 2 * pi ) * GRADIENT_BINS ) % GRADIENT_BINS


def mirrored_sprite( sprite:object ):
  # Undo the engine's mirror around the head centre, so a left-facing sprite lines up with right-facing coordinates.
  axis = 2 * ( CANVAS.margin_x + 12 )
  flipped = sprite.copy()
  for x in range( sprite.width ):
    for y in range( sprite.height ): flipped.putpixel( ( x, y ), sprite.getpixel( ( axis - x, y ) ) if 0 <= axis - x < sprite.width else ( 0, 0, 0, 0 ) )

  return flipped


def colors_47_body( shape:list, options:dict, facing:str = "right" ):
  # 47's blues on the edited silhouette: its cloudy bands around the eye (moved with the eye) on the body, and its
  # flame tones outside it: dark roots at the body, light tips at the edge, mid blue between, all shaded from the top-left.
  eye_column, eye_row = options[ "eye_at" ]
  bands = banded_core_grid( True )
  bands = bands[ BIG_EYE_AT[ 1 ] - eye_row: ] + [ bands[ -1 ] ] * ( BIG_EYE_AT[ 1 ] - eye_row )
  empty = lambda column, row: not ( 0 <= row < len( shape ) and 0 <= column < len( shape[ row ] ) ) or shape[ row ][ column ] == "."

  rows = []
  for row, line in enumerate( shape ):
    cells = ""
    for column, symbol in enumerate( line ):
      head_column = column - CANVAS.margin_x
      head_row = row - CANVAS.top
      distance = hypot( head_column - 12, head_row - 12 )
      tip = any( empty( column + dx, row + dy ) for dx, dy in ( ( 1, 0 ), ( -1, 0 ), ( 0, 1 ), ( 0, -1 ) ) )
      if symbol == ".": cells += "."
      elif distance <= BODY_EDGE: cells += bands[ head_row ][ head_column ]
      elif tip: cells += "t"
      elif options.get( "tongues_47" ) and flame_symbol( BALANCED_2_THICK, head_column - 12, head_row - 12, 0 ) != ".": cells += flame_symbol( BALANCED_2_THICK, head_column - 12, head_row - 12, 0 )
      elif distance - 9.8 < 1.2: cells += "r"
      else: cells += "b"

    rows.append( cells )

  # The user's dark specks keep their place, in 47's matching tones.
  specks = { point:{ "2":"n", "1":"d", "0":"b" }[ symbol ] for point, symbol in options.get( "edits", {} ).items() if symbol != "." and shape[ point[ 1 ] ][ point[ 0 ] ] != "." }
  highlight = options.get( "highlight" )
  outer = options.get( "outer_rim" )
  body = darker_rim( edited( rows, specks ), options.get( "dark_rim", 0 ), 0, DARKER_47, facing )
  body = outer_rimmed( body, *outer, facing=facing ) if outer else highlighted( body, highlight, facing )

  return body


def colors_47_parts( options:dict, facing:str = "right" ):
  # 47's colouring on the edited silhouette; with `flicker`, every flame state recolours the silhouette with its tips
  # grown or shrunk, so the rim and the outline follow the moving tips.
  shape = edited( options[ "silhouette" ], { point:( "." if symbol == "." else "x" ) for point, symbol in options.get( "edits", {} ).items() } )
  eye_column, eye_row = options[ "eye_at" ]
  highlight = options.get( "highlight" )
  body = colors_47_body( shape, options, facing )
  core_of = lambda grid: [ line[ CANVAS.margin_x:CANVAS.margin_x + 25 ] for line in grid[ CANVAS.top:CANVAS.top + 25 ] ]
  core = core_of( body )

  flicker = options.get( "flicker", {} )
  bodies = { f"{name}{index}":colors_47_body( flickered( shape, options[ "eye_at" ], steps, index ), options, facing ) for name, steps in flicker.items() for index in range( len( steps[ 0 ] ) ) }

  # `flow`: every tongue runs through the motion's cycle at its own moment and sheds sparks that drift away and fade.
  flows = { f"{name}{index}":flowed( shape, options[ "eye_at" ], motion, index ) for name, motion in options.get( "flow", {} ).items() for index in range( 8 ) }
  bodies = { **bodies, **{ state:colors_47_body( moved, options, facing ) for state, ( moved, _ ) in flows.items() } }
  sparks = { state:spark_grid( loose, bodies[ state ] ) for state, ( _, loose ) in flows.items() }

  # `spin`: the flame ring turns one tongue further over that many frames, each tongue taking the next one's shape.
  frames = options.get( "spin", 0 )
  bodies = { **bodies, **{ f"spin{index}":colors_47_body( rotated( shape, options[ "eye_at" ], index / frames ), options, facing ) for index in range( frames ) } }
  if options.get( "spin_sparks" ): sparks = { **sparks, **{ f"spin{index}":spark_grid( spun_sparks( shape, options[ "eye_at" ], frames, index ), bodies[ f"spin{index}" ] ) for index in range( frames ) } }

  # `stream`: over that many frames the tongues on the top and the bottom each move one tongue toward the back.
  frames = options.get( "stream", 0 )
  squash = options.get( "stream_squash", 1 )
  bodies = { **bodies, **{ f"stream{index}":colors_47_body( streamed( shape, options[ "eye_at" ], index / frames, squash ), options, facing ) for index in range( frames ) } }
  sparks = { **sparks, **{ f"stream{index}":spark_grid( streamed_sparks( shape, options[ "eye_at" ], frames, index, squash ), bodies[ f"stream{index}" ] ) for index in range( frames ) } }
  cores = { state:core_of( grid ) for state, grid in bodies.items() }

  palette = { **SOFT_DARK_BANDS, **SOFT_DARK_FLAMES, "l":Material( [ REFERENCE_BLUE ], "flat" ), **( { "w":highlight[ 0 ] } if highlight else {} ) }
  if options.get( "ramp_47" ): palette = { **palette, **{ symbol:replace( material, ramp=options[ "ramp_47" ] ) for symbol, material in { **SOFT_DARK_BANDS, **SOFT_DARK_FLAMES }.items() } }

  return [
    Part( "fire", core, ( 0, 0 ), palette, depth="face", states=cores ),
    Part( "eye", eye_white_grid( BIG_EYE ), options[ "eye_at" ], BIG_EYE_WHITE, depth="face" ),
    Part( "pupil", BIG_PUPIL, ( eye_column + 5, eye_row + 4 ), { "x":PUPIL }, depth="face", states={ "closed":BIG_PUPIL_CLOSED } ),
    Part( "glint", GLINT_GRID, ( eye_column + 8, eye_row + 5 ), { "x":GLINT }, depth="face", states={ "closed":[ "..", ".." ] } ),
    Part( "flames", body, ( -CANVAS.margin_x, -CANVAS.top ), palette, depth="behind", outline=options.get( "outline", True ), states=bodies ),
  ] + ( [ Part( "sparks", [ "." ], ( -CANVAS.margin_x, -CANVAS.top ), SPARKS, outline=False, states=sparks, edges=False ) ] if sparks else [] )


def rotated( shape:list, eye_at:tuple, share:float ):
  # The silhouette with every flame tongue `share` of the way to the next tongue clockwise, its length blending toward
  # that tongue's (so it grows or shrinks on the way). The silhouette is read as its outer radius per direction from
  # the eye; between two moved tips a direction takes both old segments' radius at the same fraction of their width.
  # Tips line up with tips, so they stay pointed halfway; share 0 is the silhouette with its few undercuts filled.
  center = ( CANVAS.margin_x + eye_at[ 0 ] + 6, CANVAS.top + eye_at[ 1 ] + 7 )
  tips = [ atan2( row - center[ 1 ], column - center[ 0 ] ) for column, row in flame_tips( shape, center ) ]
  angles = [ tips[ index % len( tips ) ] + 2 * pi * ( index // len( tips ) ) for index in range( len( tips ) + 2 ) ]
  moved = [ angles[ index ] + share * ( angles[ index + 1 ] - angles[ index ] ) for index in range( len( tips ) + 1 ) ]
  profile = outer_profile( tuple( shape ), center )
  reach = lambda turn: profile[ int( turn % ( 2 * pi ) / ( 2 * pi ) * PROFILE_BINS ) % PROFILE_BINS ]

  rows = []
  for row, line in enumerate( shape ):
    cells = ""
    for column in range( len( line ) ):
      radius = hypot( column - center[ 0 ], row - center[ 1 ] )
      angle = moved[ 0 ] + ( atan2( row - center[ 1 ], column - center[ 0 ] ) - moved[ 0 ] ) % ( 2 * pi )
      segment = next( index for index in range( len( tips ) ) if angle < moved[ index + 1 ] )
      fraction = ( angle - moved[ segment ] ) / ( moved[ segment + 1 ] - moved[ segment ] )
      before = angles[ segment ] + fraction * ( angles[ segment + 1 ] - angles[ segment ] )
      after = angles[ segment + 1 ] + fraction * ( angles[ segment + 2 ] - angles[ segment + 1 ] )
      cells += "x" if radius <= ( 1 - share ) * reach( before ) + share * reach( after ) + 0.01 else "."

    rows.append( cells )

  return rows


def spun_sparks( shape:list, eye_at:tuple, frames:int, index:int ):
  # Loose sparks at spin frame `index` ( canvas point -> age ): every tongue sheds one spark per loop at its own
  # moment, just past its tip where the tip is then, and the spark flies straight out from the eye 1 px a frame while
  # it fades, so they leave in every direction.
  center = ( CANVAS.margin_x + eye_at[ 0 ] + 6, CANVAS.top + eye_at[ 1 ] + 7 )
  tips = [ atan2( row - center[ 1 ], column - center[ 0 ] ) for column, row in flame_tips( shape, center ) ]
  angles = [ tips[ number % len( tips ) ] + 2 * pi * ( number // len( tips ) ) for number in range( len( tips ) + 1 ) ]
  profile = outer_profile( tuple( shape ), center )
  reach = lambda turn: profile[ int( turn % ( 2 * pi ) / ( 2 * pi ) * PROFILE_BINS ) % PROFILE_BINS ]

  sparks = {}
  for number in range( len( tips ) ):
    born = number * 3 % frames
    age = ( index - born ) % frames
    if age >= len( SPARKS ): continue

    share = born / frames
    turn = angles[ number ] + share * ( angles[ number + 1 ] - angles[ number ] )
    distance = ( 1 - share ) * reach( angles[ number ] ) + share * reach( angles[ number + 1 ] ) + 1 + age
    sparks[ ( round( center[ 0 ] + distance * cos( turn ) ), round( center[ 1 ] + distance * sin( turn ) ) ) ] = age

  return sparks


def streamed( shape:list, eye_at:tuple, share:float, squash:float = 1 ):
  # The silhouette with its flames flowing backward: the top and the bottom half are each a conveyor from the front
  # ( 0 ) to the back ( pi, measured from the eye ), every tongue `share` of the way to the next tongue behind it and
  # taking on its length. The front stretch grows the next tongue in; the last tongue sinks into the back. `squash`
  # below 1 presses the front half in horizontally, flattening the leading side.
  center = ( CANVAS.margin_x + eye_at[ 0 ] + 6, CANVAS.top + eye_at[ 1 ] + 7 )
  profile = outer_profile( tuple( shape ), center )
  reach = lambda turn: profile[ int( turn % ( 2 * pi ) / ( 2 * pi ) * PROFILE_BINS ) % PROFILE_BINS ]
  halves = conveyor_stops( shape, center )
  moved = { side:[ 0 ] + [ stops[ index ] + share * ( stops[ index + 1 ] - stops[ index ] ) for index in range( 1, len( stops ) - 1 ) ] + [ pi ] for side, stops in halves.items() }

  rows = []
  for row, line in enumerate( shape ):
    cells = ""
    for column in range( len( line ) ):
      ahead = ( column - center[ 0 ] ) / ( squash if column > center[ 0 ] else 1 )
      radius = hypot( ahead, row - center[ 1 ] )
      angle = atan2( row - center[ 1 ], ahead )
      side = -1 if angle < 0 else 1
      stops = halves[ side ]
      last = len( stops ) - 1
      segment = next( ( index for index in range( last ) if abs( angle ) < moved[ side ][ index + 1 ] ), last - 1 )
      fraction = ( abs( angle ) - moved[ side ][ segment ] ) / max( 1e-9, moved[ side ][ segment + 1 ] - moved[ side ][ segment ] )
      before = stops[ segment ] + fraction * ( stops[ segment + 1 ] - stops[ segment ] )
      after_start = stops[ 0 ] if segment == 0 else stops[ min( segment + 1, last ) ]
      after = after_start + fraction * ( stops[ min( segment + 2, last ) ] - after_start )
      cells += "x" if radius <= ( 1 - share ) * reach( side * before ) + share * reach( side * after ) + 0.01 else "."

    rows.append( cells )

  return rows


def streamed_sparks( shape:list, eye_at:tuple, frames:int, index:int, squash:float = 1 ):
  # Loose sparks at stream frame `index` ( canvas point -> age ): every tongue sheds two sparks per loop just past its
  # moving tip, and each drifts straight back 1 px a frame while it fades.
  center = ( CANVAS.margin_x + eye_at[ 0 ] + 6, CANVAS.top + eye_at[ 1 ] + 7 )
  profile = outer_profile( tuple( shape ), center )
  reach = lambda turn: profile[ int( turn % ( 2 * pi ) / ( 2 * pi ) * PROFILE_BINS ) % PROFILE_BINS ]

  sparks = {}
  for side, stops in conveyor_stops( shape, center ).items():
    for number in range( 1, len( stops ) - 1 ):
      for born in ( ( number * 3 + side + 1 ) % frames, ( number * 3 + side + 5 ) % frames ):
        age = ( index - born ) % frames
        if age >= len( SPARKS ): continue

        share = born / frames
        turn = side * ( stops[ number ] + share * ( stops[ number + 1 ] - stops[ number ] ) )
        distance = ( 1 - share ) * reach( side * stops[ number ] ) + share * reach( side * stops[ number + 1 ] ) + 1
        ahead = distance * cos( turn ) * ( squash if cos( turn ) > 0 else 1 )
        sparks[ ( round( center[ 0 ] + ahead ) - age, round( center[ 1 ] + distance * sin( turn ) ) ) ] = age

  return sparks


def conveyor_stops( shape:list, center:tuple ):
  # Tongue tips of the top ( -1 ) and bottom ( 1 ) half as angles from the front, between the fixed front and back.
  tips = [ atan2( row - center[ 1 ], column - center[ 0 ] ) for column, row in flame_tips( shape, center ) ]

  return { side:[ 0 ] + sorted( abs( tip ) for tip in tips if ( tip < 0 ) == ( side < 0 ) ) + [ pi ] for side in ( -1, 1 ) }


@cache
def outer_profile( shape:tuple, center:tuple ):
  # Farthest pixel centre per direction bin around `center`, each pixel covering the directions its square spans.
  profile = [ 0.0 ] * PROFILE_BINS
  for row, line in enumerate( shape ):
    for column, symbol in enumerate( line ):
      if symbol == ".": continue

      radius = hypot( column - center[ 0 ], row - center[ 1 ] )
      angle = atan2( row - center[ 1 ], column - center[ 0 ] )
      for step in range( -20, 21 ):
        index = int( ( angle + 0.5 / max( radius, 0.5 ) * step / 20 ) % ( 2 * pi ) / ( 2 * pi ) * PROFILE_BINS ) % PROFILE_BINS
        profile[ index ] = max( profile[ index ], radius )

  return profile


def flowed( shape:list, eye_at:tuple, motion:dict, index:int ):
  # The silhouette at one frame of a flame motion, and its loose sparks ( canvas point -> age ). Each tongue is "front",
  # "back" or "side" by where it points, takes its step from that role's cycle at its own moment, and sheds a spark
  # at every `born` moment: one pixel past the tip, drifting `drift` per frame while it fades.
  center = ( CANVAS.margin_x + eye_at[ 0 ] + 6, CANVAS.top + eye_at[ 1 ] + 7 )
  rows = [ list( line ) for line in shape ]
  filled = lambda column, row: 0 <= row < len( rows ) and 0 <= column < len( rows[ row ] ) and rows[ row ][ column ] != "."
  inside = lambda column, row: 0 <= row < len( rows ) and 0 <= column < len( rows[ row ] )

  sparks = {}
  for number, ( column, row ) in enumerate( flame_tips( shape, center ) ):
    angle = atan2( row - center[ 1 ], column - center[ 0 ] )
    outward = ( round( cos( angle ) ), round( sin( angle ) ) )
    role = "front" if cos( angle ) > 0.5 else "back" if cos( angle ) < -0.5 else "side"
    moment = ( index + motion[ "offset" ]( number, column ) ) % 8
    step = motion[ "cycles" ][ role ][ moment ]

    # Upright tongues bend their tip back a pixel, where it stays joined to the tongue.
    bend = motion.get( "bend", 0 ) if outward[ 0 ] == 0 and role == "side" else 0
    if bend and filled( column + bend, row - outward[ 1 ] ):
      rows[ row ][ column ] = "."
      column += bend
      rows[ row ][ column ] = "x"

    if step < 0: rows[ row ][ column ] = "."
    for grown in range( 1, step + 1 ):
      target = ( column + outward[ 0 ] * grown, row + outward[ 1 ] * grown )
      if inside( *target ): rows[ target[ 1 ] ][ target[ 0 ] ] = "x"

    if not motion[ "spark_from" ]( role, outward ): continue

    for born in motion[ "born" ]:
      age = ( moment - born ) % 8
      if age < len( SPARKS ): sparks[ ( column + outward[ 0 ] + motion[ "drift" ][ 0 ] * age, row + outward[ 1 ] + motion[ "drift" ][ 1 ] * age ) ] = age

  return [ "".join( line ) for line in rows ], sparks


def spark_grid( sparks:dict, body:list ):
  # Sparks as a canvas grid of ages: none over the body, and none of the fading ones next to it, where they would
  # replace the outline with a see-through pixel.
  occupied = lambda column, row: 0 <= row < len( body ) and 0 <= column < len( body[ row ] ) and body[ row ][ column ] != "."
  near = lambda column, row: any( occupied( column + dx, row + dy ) for dx, dy in ( ( 1, 0 ), ( -1, 0 ), ( 0, 1 ), ( 0, -1 ) ) )
  rows = [ [ "." ] * len( body[ 0 ] ) for _ in body ]

  for ( column, row ), age in sparks.items():
    if not ( 0 <= row < len( body ) and 0 <= column < len( body[ 0 ] ) ): continue
    if occupied( column, row ) or ( age > 1 and near( column, row ) ): continue

    rows[ row ][ column ] = str( age )

  return [ "".join( line ) for line in rows ]


def flame_tips( shape:list, center:tuple ):
  # The outermost pixel of each flame tongue: farthest from the eye in its direction and at least 20 degrees from a
  # farther tip, one per tongue, ordered clockwise from the left.
  pixels = [ ( column, row ) for row, line in enumerate( shape ) for column, symbol in enumerate( line ) if symbol != "." ]
  distance = lambda point: hypot( point[ 0 ] - center[ 0 ], point[ 1 ] - center[ 1 ] )
  angle = lambda point: atan2( point[ 1 ] - center[ 1 ], point[ 0 ] - center[ 0 ] )
  apart = lambda first, second: abs( ( angle( first ) - angle( second ) + pi ) % ( 2 * pi ) - pi )

  tips = []
  for point in sorted( pixels, key=distance, reverse=True ):
    if distance( point ) < 12: break
    if all( apart( point, tip ) > radians( 20 ) for tip in tips ): tips.append( point )

  return sorted( tips, key=angle )


def flickered( shape:list, eye_at:tuple, steps:list, index:int ):
  # The silhouette with each flame tip grown outward ( > 0 ) or shrunk ( < 0 ) by `steps[ tip ][ index ]` pixels; tips
  # past the listed ones repeat the list.
  center = ( CANVAS.margin_x + eye_at[ 0 ] + 6, CANVAS.top + eye_at[ 1 ] + 7 )
  rows = [ list( line ) for line in shape ]
  inside = lambda column, row: 0 <= row < len( rows ) and 0 <= column < len( rows[ row ] )

  for number, ( column, row ) in enumerate( flame_tips( shape, center ) ):
    step = steps[ number % len( steps ) ][ index ]
    angle = atan2( row - center[ 1 ], column - center[ 0 ] )
    outward = ( round( cos( angle ) ), round( sin( angle ) ) )
    if step < 0: rows[ row ][ column ] = "."

    for grown in range( 1, step + 1 ):
      target = ( column + outward[ 0 ] * grown, row + outward[ 1 ] * grown )
      if inside( *target ): rows[ target[ 1 ] ][ target[ 0 ] ] = "x"

  return [ "".join( line ) for line in rows ]


def gradient_parts( ring:dict, options:dict ):
  # One gradient over the whole blue area: darkest at the eye, lightest at the outer edge of the flames, measured along
  # each ray from the eye so a tongue runs through every tone up to its tip.
  tones = options[ "gradient" ]
  palette = { str( index ):Material( tones, level=index, light=FLAME_LIGHT, step=GRADIENT_STEP ) for index in range( len( tones ) ) }

  # 47's shading: each tone darkens toward the bottom-right in steps of 13 px, down the reference ramp.
  if options.get( "shaded" ): palette = { str( index ):Material( FIRE, level=FIRE.index( tones[ index ] ), light=FLAME_LIGHT, step=13 ) for index in range( len( tones ) ) }
  highlight = options.get( "highlight" )
  if highlight: palette[ "w" ] = highlight[ 0 ]
  eye_at = options.get( "eye_at", BIG_EYE_AT )
  eye_column, eye_row = eye_at
  shape = lambda phase: options.get( "silhouette" ) or flame_grid( ring, phase )
  tone_grid = lambda phase: gradient_grid( shape( phase ), len( tones ), options.get( "dither", 0 ), options.get( "inner" ), eye_at, options.get( "tone_chaos", 0 ) )
  finish = lambda grid: highlighted( darker_rim( edited( grid, options.get( "edits", {} ) ), options.get( "dark_rim", 0 ), len( tones ) ), highlight )
  states = { f"phase{index}":finish( tone_grid( index / 8 ) ) for index in range( 8 ) }
  body = finish( tone_grid( 0 ) )
  core = [ line[ CANVAS.margin_x:CANVAS.margin_x + 25 ] for line in body[ CANVAS.top:CANVAS.top + 25 ] ]

  return [
    Part( "fire", core, ( 0, 0 ), palette, depth="face" ),
    Part( "eye", eye_white_grid( BIG_EYE ), eye_at, BIG_EYE_WHITE, depth="face" ),
    Part( "pupil", BIG_PUPIL, ( eye_column + 5, eye_row + 4 ), { "x":PUPIL }, depth="face", states={ "closed":BIG_PUPIL_CLOSED } ),
    Part( "glint", GLINT_GRID, ( eye_column + 8, eye_row + 5 ), { "x":GLINT }, depth="face" ),
    Part( "flames", body, ( -CANVAS.margin_x, -CANVAS.top ), palette, depth="behind", outline=options.get( "outline", True ), states=states ),
  ]


def edited( grid:list, edits:dict ):
  # Hand edits on a tone grid: canvas ( column, row ) -> tone index as text, or "." to remove the pixel.
  rows = [ list( line ) for line in grid ]
  for ( column, row ), symbol in edits.items(): rows[ row ][ column ] = symbol

  return [ "".join( line ) for line in rows ]


def highlighted( grid:list, highlight:tuple, facing:str = "right" ):
  # A 1 px inner rim in the highlight material along the edge (all round, or only the lit top-left side), inside the
  # outline like the EE head's light ring. A third item ( start, end ) dithers the lit-side rim out between diagonals.
  if not highlight: return grid

  side = highlight[ 1 ]
  fade = highlight[ 2 ] if len( highlight ) > 2 else None
  inside = lambda column, row: 0 <= row < len( grid ) and 0 <= column < len( grid[ row ] ) and grid[ row ][ column ] != "."
  rows = [ list( line ) for line in grid ]
  for row, line in enumerate( grid ):
    for column, symbol in enumerate( line ):
      lit_side = light_diagonal( column, row, facing ) < 26
      edge = not all( inside( column + dx, row + dy ) for dx, dy in ( ( 1, 0 ), ( -1, 0 ), ( 0, 1 ), ( 0, -1 ) ) )
      diagonal = light_diagonal( column, row, facing )
      kept = not fade or diagonal < fade[ 0 ] or ( diagonal < fade[ 1 ] and pixel_noise( column, row ) < 2 * ( fade[ 1 ] - diagonal ) / ( fade[ 1 ] - fade[ 0 ] ) - 1 )
      if symbol != "." and edge and ( side == "all" or lit_side or fade ) and kept: rows[ row ][ column ] = "w"

  return [ "".join( line ) for line in rows ]


def outer_rimmed( grid:list, side:str, symbol:str, fade:tuple = None, middle:str = None, facing:str = "right" ):
  # A 1 px rim outside the blue (all round, or only on the lit top-left side), so the black outline then goes around
  # the rim and the character keeps every blue pixel. `fade` ( start, end ) eases the lit-side rim out between those
  # diagonals: dithered away, or through the `middle` symbol first.
  inside = lambda column, row: 0 <= row < len( grid ) and 0 <= column < len( grid[ row ] ) and grid[ row ][ column ] != "."
  rows = [ list( line ) for line in grid ]
  for row, line in enumerate( grid ):
    for column, cell in enumerate( line ):
      lit_side = light_diagonal( column, row, facing ) < 26
      touches = any( inside( column + dx, row + dy ) for dx, dy in ( ( 1, 0 ), ( -1, 0 ), ( 0, 1 ), ( 0, -1 ) ) )
      if cell == "." and touches and ( side == "all" or lit_side ) and not fade: rows[ row ][ column ] = symbol
      if cell != "." or not touches or not fade: continue

      diagonal = light_diagonal( column, row, facing )
      start, end = fade
      share = ( end - diagonal ) / ( end - start )
      if diagonal < start: rows[ row ][ column ] = symbol
      elif diagonal < end and middle: rows[ row ][ column ] = symbol if pixel_noise( column, row ) < 2 * share - 1 else middle
      elif diagonal < end: rows[ row ][ column ] = symbol if pixel_noise( column, row ) < 2 * share - 1 else "."
      elif middle and diagonal < end + ( end - start ) and pixel_noise( column + 5, row + 3 ) < 2 * ( end + ( end - start ) - diagonal ) / ( end - start ) - 1: rows[ row ][ column ] = middle

  return [ "".join( line ) for line in rows ]


def light_diagonal( column:int, row:int, facing:str ):
  # Head column plus head row of a canvas pixel in the final sprite: small toward the top-left light. A left-facing
  # grid is mirrored afterwards, so its pixel ends up on the other side of the head centre.
  head_column = column - CANVAS.margin_x

  return ( 24 - head_column if facing == "left" else head_column ) + row - CANVAS.top


def darker_rim( grid:list, steps:int, count:int, darken:dict = None, facing:str = "right" ):
  # Shade the outermost pixels on the bottom-right (the side away from the light) `steps` tones darker; `darken` maps
  # symbol tones (47's colours) to the next darker one instead of counting tone indices.
  if not steps: return grid

  inside = lambda column, row: 0 <= row < len( grid ) and 0 <= column < len( grid[ row ] ) and grid[ row ][ column ] != "."
  rows = [ list( line ) for line in grid ]
  for row, line in enumerate( grid ):
    for column, symbol in enumerate( line ):
      shaded_side = light_diagonal( column, row, facing ) > 26
      if symbol == "." or not shaded_side or all( inside( column + dx, row + dy ) for dx, dy in ( ( 1, 0 ), ( -1, 0 ), ( 0, 1 ), ( 0, -1 ) ) ): continue

      rows[ row ][ column ] = str( min( count - 1, int( symbol ) + steps ) ) if not darken else symbol
      for _ in range( steps if darken else 0 ): rows[ row ][ column ] = darken.get( rows[ row ][ column ], rows[ row ][ column ] )

  return [ "".join( line ) for line in rows ]


def gradient_grid( shape:list, count:int, dither:float, inner:dict = None, eye_at:tuple = BIG_EYE_AT, chaos:float = 0 ):
  # Tone index per pixel of a canvas-sized shape: 0 (lightest) at the silhouette, count - 1 (darkest) at the eye.
  # `inner` turns each border between two tones into flame tongues of its own, leaning its own way; `chaos` moves
  # scattered pixels one tone up or down, like the flicker in the pixel reference.
  center_x = CANVAS.margin_x + eye_at[ 0 ] + 6
  center_y = CANVAS.top + eye_at[ 1 ] + 7
  pixels = [ ( column, row ) for row, line in enumerate( shape ) for column, symbol in enumerate( line ) if symbol != "." ]
  bin_of = lambda column, row: int( ( atan2( row - center_y, column - center_x ) + pi ) / ( 2 * pi ) * GRADIENT_BINS ) % GRADIENT_BINS

  # Farthest blue pixel per direction, widened to the neighbouring directions so single rays don't streak.
  reach = [ 0 ] * GRADIENT_BINS
  for column, row in pixels: reach[ bin_of( column, row ) ] = max( reach[ bin_of( column, row ) ], hypot( column - center_x, row - center_y ) )
  reach = [ max( reach[ ( index + offset ) % GRADIENT_BINS ] for offset in ( -1, 0, 1 ) ) for index in range( GRADIENT_BINS ) ]

  grid = [ [ "." ] * len( line ) for line in shape ]
  for column, row in pixels:
    x = column - center_x
    y = row - center_y
    angle = atan2( y, x )
    eye_reach = 1 / hypot( cos( angle ) / 6.5, sin( angle ) / 7.5 )
    share = ( hypot( x, y ) - eye_reach ) / max( 1, reach[ bin_of( column, row ) ] - eye_reach )
    share += dither * pixel_noise( column, row )

    tone = count - 1 - int( share * count )
    if inner: tone = count - 1 - sum( 1 for border in range( 1, count ) if share > border / count + inner_tongue( inner, border, angle, share ) )
    if chaos and pixel_noise( column + 17, row + 5 ) > 1 - 2 * chaos: tone += 1 if pixel_noise( column + 2, row + 29 ) > 0 else -1

    grid[ row ][ column ] = str( max( 0, min( count - 1, tone ) ) )

  return [ "".join( line ) for line in grid ]


def inner_tongue( inner:dict, border:int, angle:float, share:float ):
  # How far a darker tone licks out past this border here: pointed tongues, a different count, turn and lean per border.
  tongues = inner[ "tongues" ][ ( border - 1 ) % len( inner[ "tongues" ] ) ]
  lean = inner[ "lean" ] * ( 1 if border % 2 else -1 )
  height = inner[ "height" ]
  position = angle / ( 2 * pi ) * tongues + border * 0.37

  # Random turns: each tongue gets its own lean, offset and height from a repeatable noise value.
  if "random" in inner:
    seed = inner[ "random" ]
    tongue = int( position // 1 )
    lean = inner[ "lean" ] * pixel_noise( tongue + seed, border * 7 + seed )
    position += inner.get( "jitter", 0 ) * pixel_noise( tongue + seed * 3, border + 11 )
    height *= 1 + 0.3 * pixel_noise( tongue + seed * 5, border + 23 )

  sweep = ( position + lean * share ) % 1

  return height * ( 1 - abs( 2 * sweep - 1 ) ) ** 2 - inner[ "height" ] * 0.35


def outlined( items:list, outline:object ):
  # Give the flames another edge than solid black.
  for item in items:
    if item.name == "flames": item.outline = outline

  return items


def big_eye_parts( ring:dict, flame_states:dict, mixed:bool = False, cloudy:bool = False, dark:object = False, noise:float = 0, speckle:float = 0, light_flames:bool = False, bands:dict = None, edge:float = None, limits:list = None, flames_override:dict = None ):
  # A larger eye in fire that darkens toward it in ragged bands, like the reference; outer flames in the same light
  # tones. Mixed keeps the tongue-shaped core and outer flames of the flame core with only the bands by the eye.
  seams = ring if "seams" in ring else None
  eye_column, eye_row = BIG_EYE_AT
  fire = Part( "fire", banded_core_grid( cloudy ), ( 0, 0 ), BAND_MATERIALS, depth="face" )
  flames = Part( "flames", flame_grid( ring, 0 ), ( -CANVAS.margin_x, -CANVAS.top ), SOFT_FLAMES, depth="behind", states=flame_states )
  band_materials, flame_materials = ( SOFT_DARK_BANDS, SOFT_DARK_FLAMES ) if dark == "soft" else ( DARK_BAND_MATERIALS, { "t":FLAME_TIP, "b":FLAME_BODY, "r":FLAME_ROOT } )
  if light_flames: flame_materials = LIGHT_FLAMES
  if bands: band_materials = bands
  if flames_override: flame_materials = flames_override
  if dark: fire = Part( "fire", speckled( banded_core_grid( cloudy, seams, noise, edge, limits ), speckle ), ( 0, 0 ), band_materials, depth="face" )
  if dark: flames = Part( "flames", flame_grid( ring, 0 ), ( -CANVAS.margin_x, -CANVAS.top ), flame_materials, depth="behind", states=flame_states )
  if mixed: fire = Part( "fire", mixed_core_grid(), ( 0, 0 ), { **BAND_MATERIALS, "t":FLAME_TIP, "b":FLAME_BODY, "r":FLAME_ROOT }, depth="face" )
  if mixed: flames = Part( "flames", flame_grid( ring, 0 ), ( -CANVAS.margin_x, -CANVAS.top ), { "t":FLAME_TIP, "b":FLAME_BODY, "r":FLAME_ROOT }, depth="behind", states=flame_states )

  return [
    fire,
    Part( "eye", eye_white_grid( BIG_EYE ), BIG_EYE_AT, BIG_EYE_WHITE, depth="face" ),
    Part( "pupil", BIG_PUPIL, ( eye_column + 5, eye_row + 4 ), { "x":PUPIL }, depth="face", states={ "closed":BIG_PUPIL_CLOSED } ),
    Part( "glint", GLINT_GRID, ( eye_column + 8, eye_row + 5 ), { "x":GLINT }, depth="face" ),
    flames,
  ]


def embers_part( ring:dict, embers:list ):
  # Single pixels that never touch the flames' outline: walk out from the head centre along each angle to the first
  # free spot, then a little further.
  flames = flame_grid( ring, 0 )
  occupied = {
    ( column - CANVAS.margin_x, row - CANVAS.top )
    for row, line in enumerate( flames ) for column, symbol in enumerate( line ) if symbol != "."
  } | { ( column, row ) for column in range( 25 ) for row in range( 25 ) if hypot( column - 12, row - 12 ) <= min( 12.5, ring[ "radius" ] + 1 ) }
  blocked = { ( column + dx, row + dy ) for column, row in occupied for dx in range( -2, 3 ) for dy in range( -2, 3 ) if abs( dx ) + abs( dy ) <= 2 }
  last_column = 24 + CANVAS.margin_x - 1
  last_row = 24 + CANVAS.bottom - 1

  grid = [ [ "." ] * ( 25 + 2 * CANVAS.margin_x ) for _ in range( 25 + CANVAS.top + CANVAS.bottom ) ]
  for angle, extra, symbol in embers:
    for step in range( 120 ):
      distance = 12 + step / 8
      column = round( 12 + cos( radians( angle ) ) * distance )
      row = round( 12 + sin( radians( angle ) ) * distance )
      if ( column, row ) in blocked: continue

      column = round( 12 + cos( radians( angle ) ) * ( distance + extra ) )
      row = round( 12 + sin( radians( angle ) ) * ( distance + extra ) )
      if -CANVAS.margin_x < column <= last_column and -CANVAS.top < row <= last_row: grid[ row + CANVAS.top ][ column + CANVAS.margin_x ] = symbol
      break

  return Part( "embers", [ "".join( line ) for line in grid ], ( -CANVAS.margin_x, -CANVAS.top ), { "e":EMBER, "d":EMBER_DARK }, outline=False )


def flame_grid( ring:dict, phase:float ):
  # Pixels around the head inside the flame radius: dark roots by the head, lighter tongue tips outside.
  rows = []
  for row in range( -CANVAS.top, 25 + CANVAS.bottom ):
    line = ""
    for column in range( -CANVAS.margin_x, 25 + CANVAS.margin_x ):
      outer = column in ( -CANVAS.margin_x, 24 + CANVAS.margin_x ) or row in ( -CANVAS.top, 24 + CANVAS.bottom )
      line += "." if outer else flame_symbol( ring, column - 12, row - 12, phase )

    rows.append( line )

  return rows


def flame_symbol( ring:dict, x:float, y:float, phase:float ):
  if "tongue_list" in ring: return placed_flame_symbol( ring, x, y )
  if "sectors" in ring: return sector_flame_symbol( ring, x, y, phase )
  if "lift" in ring: return lifted_symbol( ring, x, y, phase )
  if "chaos" in ring: return chaotic_symbol( ring, x, y, phase )
  if "squeeze" in ring: return flame_symbol( ring[ "source" ], x - ( ring[ "squeeze" ][ 0 ] if x < 0 else 0 ), y + ( ring[ "squeeze" ][ 1 ] if y > 0 else 0 ), phase )
  if "shift" in ring: return flame_symbol( ring[ "source" ], x - ring[ "shift" ][ 0 ], y - ring[ "shift" ][ 1 ], phase )

  distance = hypot( x, y )
  angle = atan2( y, x )
  depth = distance - ring[ "radius" ]

  # Tongues are a sawtooth around the ring, swirled outward so their tips curl.
  sweep = ( angle / ( 2 * pi ) * ring[ "tongues" ] - depth * ring[ "swirl" ] + phase + ring.get( "offset", 0 ) ) % 1
  height = ring[ "height" ]

  # Random turns: every tongue gets its own lean and length, so the ring stops looking like a saw blade.
  if "random" in ring:
    chance = ring[ "random" ]
    position = angle / ( 2 * pi ) * ring[ "tongues" ] + phase + ring.get( "offset", 0 )
    tongue = int( position // 1 ) % ring[ "tongues" ]
    lean = chance[ "lean" ] * pixel_noise( tongue * 13 + chance[ "seed" ], chance[ "seed" ] * 7 )
    sweep = ( position - depth * ( ring[ "swirl" ] + lean ) ) % 1
    height *= 1 + chance[ "length" ] * pixel_noise( tongue * 29 + chance[ "seed" ], chance[ "seed" ] + 3 )

  profile = ( 1 - abs( 2 * sweep - 1 ) ) ** ring.get( "sharp", 2 ) if ring.get( "peak" ) else ( 1 - sweep ) ** 2
  if ring.get( "round" ): profile = sin( pi * sweep ) ** ring.get( "sharp", 1 )
  thickness = ring[ "front" ] + ( ring[ "back" ] - ring[ "front" ] ) * ( 1 - cos( angle ) ) / 2 + height * profile

  # Uneven tongue lengths and a lift on the top half make the edge read as live fire.
  if "lengths" in ring:
    tongue = int( ( angle / ( 2 * pi ) * ring[ "tongues" ] - depth * ring[ "swirl" ] + phase + ring.get( "offset", 0 ) ) // 1 ) % ring[ "tongues" ]
    thickness = ring[ "front" ] + ( ring[ "back" ] - ring[ "front" ] ) * ( 1 - cos( angle ) ) / 2 + ring[ "height" ] * ring[ "lengths" ][ tongue ] * profile + ring.get( "rise", 0 ) * max( 0, -y / max( distance, 1 ) )

  # Shake: a slow wobble along the ring so the billows are uneven without getting spiky.
  if "shake" in ring: thickness += ring[ "shake" ] * ( sin( angle * 3 + 1 ) + sin( angle * 5 + 2.3 ) + sin( angle * 7 + 0.7 ) ) / 3
  if depth > thickness: return "."

  if depth < 1.2: return "r"
  if depth > thickness - 1.2: return "t"
  return "b"


def with_random( ring:dict, chance:dict ):
  # The same ring layout with random turns on every flame source inside it.
  if "sectors" in ring: return { **ring, "default":[ with_random( source, chance ) for source in ring[ "default" ] ], "sectors":[ ( start, end, [ with_random( source, chance ) for source in sources ] ) for start, end, sources in ring[ "sectors" ] ] }
  if "source" in ring: return { **ring, "source":with_random( ring[ "source" ], chance ) }

  return { **ring, "random":chance }


def chaotic_symbol( ring:dict, x:float, y:float, phase:float ):
  # Scatter tones through the flames: some pixels jump a tone lighter or darker, so the fire flickers like the reference.
  symbol = flame_symbol( ring[ "source" ], x, y, phase )
  if symbol == "." or pixel_noise( int( x ) + 40, int( y ) + 9 ) < 1 - 2 * ring[ "chaos" ]: return symbol

  return { "r":"b", "b":"t" if pixel_noise( int( x ) + 3, int( y ) + 51 ) > 0 else "r", "t":"b" }[ symbol ]


def lifted_symbol( ring:dict, x:float, y:float, phase:float ):
  # Curl tongues up: sample the source lower down the farther out the pixel is, within the flames' reach only.
  depth = hypot( x, y ) - ring[ "source" ][ "radius" ]
  if depth > LIFT_REACH: return "."

  return flame_symbol( ring[ "source" ], x, y + ring[ "lift" ] * min( max( 0, depth ), LIFT_REACH - 1 ) ** 2, phase )


def sector_flame_symbol( ring:dict, x:float, y:float, phase:float ):
  # The first ring in the pixel's sector that has a flame there wins, so a body ring fills in under borrowed tongues.
  angle = atan2( y, x ) * 180 / pi
  sources = next( ( sources for start, end, sources in ring[ "sectors" ] if start <= angle < end ), ring[ "default" ] )
  return next( ( symbol for symbol in ( flame_symbol( source, x, y, phase ) for source in sources ) if symbol != "." ), "." )


def placed_flame_symbol( ring:dict, x:float, y:float ):
  # A base band around the head (thicker on top and at the back if asked), then tapered tongues whose centre lines
  # curve upward and, with bend_x, back.
  distance = hypot( x, y )
  depth = distance - ring[ "radius" ]
  base = ring[ "base" ] + ring.get( "base_top", 0 ) * max( 0, -y / max( distance, 1 ) ) + ring.get( "base_back", 0 ) * max( 0, -x / max( distance, 1 ) )
  if depth < base: return ( "r" if depth < 1.2 else "b" ) if depth >= -1 else "."

  for angle, length, half_width in ring[ "tongue_list" ]:
    direction_x = cos( radians( angle ) )
    direction_y = sin( radians( angle ) )
    base_x = direction_x * ring[ "radius" ]
    base_y = direction_y * ring[ "radius" ]

    # Walk along the tongue: its centre at step t is pushed up by bend·t², the width tapers to a point.
    for step in range( 0, int( length * 4 ) + 1 ):
      along = step / 4
      center_x = base_x + direction_x * along - ring.get( "bend_x", 0 ) * along ** 2
      center_y = base_y + direction_y * along - ring[ "bend" ] * along ** 2
      width = half_width * ( 1 - along / length )
      if hypot( x - center_x, y - center_y ) > width + 0.35: continue

      if along > length * 0.55: return "t"
      return "r" if depth < 1.2 else "b"

  return "."


def tongue_tips_grid( phase:float ):
  # Only the tongue tips that reach past the head's outline, drawn in front so they break the round silhouette.
  rows = flame_grid( TONGUE_TIPS, phase )
  return [
    "".join( symbol if symbol != "." and hypot( column - CANVAS.margin_x - 12, row - CANVAS.top - 12 ) > 11.4 else "." for column, symbol in enumerate( line ) )
    for row, line in enumerate( rows )
  ]


def fire_grid( streaks:float, glow:tuple ):
  # The face as fire around the eye: a dark glow hugging the eye, then swirling streaks fading to light flames.
  eye_column, eye_row = SMALL_EYE_AT
  center_x = eye_column + 5
  center_y = eye_row + 5.5
  rows = []
  for row in range( 25 ):
    line = ""
    for column in range( 25 ):
      x = column - center_x
      y = row - center_y
      gap = ( hypot( x / 5.5, y / 6 ) - 1 ) * 5.75
      sweep = ( atan2( y, x ) / ( 2 * pi ) * 7 - gap * 0.22 ) % 1

      if gap < glow[ 0 ]: line += "r"
      elif gap < glow[ 1 ] or sweep < streaks: line += "b"
      else: line += "t"

    rows.append( line )

  return rows


def flame_core_grid( center:tuple = ( SMALL_EYE_AT[ 0 ] + 5, SMALL_EYE_AT[ 1 ] + 5.5 ), radii:tuple = ( 5.5, 6 ) ):
  # The face in the same style as the outer flames: tongues rising from the eye's rim with dark roots, mid bodies
  # and light tips, a dark seam between neighbouring tongues.
  center_x, center_y = center
  radius_x, radius_y = radii
  rows = []
  for row in range( 25 ):
    line = ""
    for column in range( 25 ):
      x = column - center_x
      y = row - center_y
      gap = ( hypot( x / radius_x, y / radius_y ) - 1 ) * ( radius_x + radius_y ) / 2
      sweep = ( atan2( y, x ) / ( 2 * pi ) * CORE_TONGUES - gap * CORE_SWIRL ) % 1
      length = CORE_BASE + CORE_HEIGHT * ( 1 - sweep ) ** 2

      if gap < 1: line += "r"
      elif gap <= length - 1.2: line += "b"
      elif gap <= length: line += "t"
      elif gap <= length + 1: line += "r"
      else: line += "b"

    rows.append( line )

  return rows


def banded_core_grid( cloudy:bool = False, seams:dict = None, noise:float = 0, edge:float = None, limits:list = None ):
  # Distance from the eye's edge picks the band; a swirling wobble makes the band edges ragged like flames.
  center_x = BIG_EYE_AT[ 0 ] + 6
  center_y = BIG_EYE_AT[ 1 ] + 7
  rows = []
  for row in range( 25 ):
    line = ""
    for column in range( 25 ):
      x = column - center_x
      y = row - center_y
      gap = ( hypot( x / 6.5, y / 7.5 ) - 1 ) * 7
      sweep = ( atan2( y, x ) / ( 2 * pi ) * 9 - gap * 0.3 ) % 1
      wobble = gap + 2.2 * ( sweep - 0.5 )
      if cloudy: wobble = gap + CLOUD_WOBBLE * ( sin( x * 0.9 + y * 0.4 ) + sin( y * 1.1 - x * 0.5 + 1.3 ) + sin( ( x + y ) * 0.6 + 2 ) ) / 2

      # Pixel noise dithers the dark bands into a grainy gradient, strongest below the eye.
      if noise: wobble += noise * ( 1 + max( 0, y ) / 7 ) * pixel_noise( column, row )

      symbol = next( ( symbol for limit, symbol in BAND_LIMITS if wobble < limit ), "t" )

      # Relative bands: the share of the way from the eye to the body edge picks the tone, so a thin side still runs
      # through every tone instead of staying dark.
      if edge:
        room = max( 0.5, edge - hypot( column - 12, row - 12 ) )
        share = max( 0, gap ) / ( max( 0, gap ) + room ) + ( wobble - gap ) * 0.12
        symbol = next( ( symbol for limit, symbol in limits or RELATIVE_LIMITS if share < limit ), "t" )
      if seams and symbol in "tb" and is_seam( seams, column - 12, row - 12 ): symbol = "m"

      line += symbol

    rows.append( line )

  return rows


def is_seam( ring:dict, x:float, y:float ):
  # Inside the head's rim, the line where two outer tongues meet, continued inward with the same lean.
  distance = hypot( x, y )
  depth = distance - ring[ "radius" ]
  if depth < -ring[ "seams" ]: return False

  sweep = ( atan2( y, x ) / ( 2 * pi ) * ring[ "tongues" ] - depth * ring[ "swirl" ] ) % 1
  return sweep < 0.12 or sweep > 0.9


def speckled( grid:list, amount:float ):
  # Scatter lighter pixels through the dark bands (two tones lighter) so they read as flickering fire, not a flat fill.
  lighter = { "n":"m", "d":"b" }
  return [
    "".join( lighter[ symbol ] if symbol in lighter and pixel_noise( column + 31, row + 17 ) > 1 - 2 * amount else symbol for column, symbol in enumerate( line ) )
    for row, line in enumerate( grid )
  ]


def pixel_noise( column:int, row:int ):
  # Repeatable pseudo-random value in -1..1 for a pixel.
  return ( ( column * 73856093 ^ row * 19349663 ) % 1000 ) / 500 - 1


def mixed_core_grid():
  # Flame tongues of the core around the big eye, with the ragged navy and dark bands hugging the white.
  core = flame_core_grid( ( BIG_EYE_AT[ 0 ] + 6, BIG_EYE_AT[ 1 ] + 7 ), ( 6.5, 7.5 ) )
  bands = banded_core_grid()

  return [ "".join( band if band in "nd" else flame for band, flame in zip( band_line, flame_line ) ) for band_line, flame_line in zip( bands, core ) ]


def eye_white_grid( shape:list = SMALL_EYE ):
  # White eye with a pale blue rim on its shaded left, top and bottom edges; the lit right edge stays white.
  inside = lambda x, y: 0 <= y < len( shape ) and 0 <= x < len( shape[ y ] ) and shape[ y ][ x ] == "x"
  big = shape is not SMALL_EYE
  rows = []
  for y, line in enumerate( shape ):
    cells = ""
    for x, symbol in enumerate( line ):
      rim = not all( inside( x + dx, y + dy ) for dx, dy in ( ( -1, 0 ), ( 0, -1 ), ( 0, 1 ) ) )
      if symbol == ".": cells += "."
      elif big and not inside( x + 1, y ): cells += "l"
      elif rim: cells += "e"
      elif big and not all( inside( x + dx, y + dy ) for dx, dy in ( ( -2, 0 ), ( 0, -2 ), ( 0, 2 ) ) ): cells += "m"
      elif not inside( x - 2, y ): cells += "l"
      else: cells += "w"

    rows.append( cells )

  return rows


run( globals() )
