from math import hypot
from pathlib import Path
from PIL import Image, ImageFilter

# EE head core: 25px black circle with a light ring inside it.
HEAD_CIRCLE = [
  ".........#######.........",
  ".......###.....###.......",
  ".....###.........###.....",
  "....##.............##....",
  "...##...............##...",
  "..##.................##..",
  "..#...................#..",
  ".##...................##.",
  ".#.....................#.",
  "##.....................##",
  "#.......................#",
  "#.......................#",
  "#.......................#",
  "#.......................#",
  "#.......................#",
  "##.....................##",
  ".#.....................#.",
  ".##...................##.",
  "..#...................#..",
  "..##.................##..",
  "...##...............##...",
  "....##.............##....",
  ".....###.........###.....",
  ".......###.....###.......",
  ".........#######.........",
]
HEAD_CENTER = 12

# Canvas leaves room for the hand, feet and mug poking out of the head.
WIDTH = 31
HEIGHT = 29
OFFSET_X = 2
# Left-facing sprites are mirrored across the whole canvas, which moves the head right.
MIRRORED_OFFSET_X = WIDTH - 1 - OFFSET_X - 24
OFFSET_Y = 0
PREVIEW_SCALE = 12
# Assets are written next to this script.
OUTPUT_DIR = Path( __file__ ).parent

# Face band with the grin under it, shifted down per column: [ ( last_column, row_shift ) ].
BAND_TOP = 10
BAND_SHAPES = {
  "rising": [ ( 6, 1 ), ( 22, 0 ) ],
  "falling": [ ( 7, -1 ), ( 15, 0 ), ( 22, 1 ) ],
  "falling_steep": [ ( 4, -1 ), ( 9, 0 ), ( 15, 1 ), ( 22, 2 ) ],
  "falling_low": [ ( 6, 0 ), ( 15, 1 ), ( 22, 2 ) ],
  "arc": [ ( 6, -1 ), ( 10, 0 ), ( 15, 1 ), ( 22, 2 ) ],
  # Curved like an equator seen from above: steep on the left, flat under the eyes.
  "round_2": [ ( 4, -1 ), ( 6, 0 ), ( 9, 1 ), ( 22, 2 ) ],
  "round_3": [ ( 3, -1 ), ( 5, 0 ), ( 7, 1 ), ( 10, 2 ), ( 22, 3 ) ],
  "round_2_right_low": [ ( 4, -1 ), ( 6, 0 ), ( 9, 1 ), ( 14, 2 ), ( 22, 3 ) ],
}

# Eyes in head coordinates: ( symbol, { row:( first_column, last_column ) } ). "e" softens corners.
BIG_EYE = { 7:( 12, 13 ), 8:( 11, 14 ), 9:( 11, 14 ), 10:( 11, 14 ), 11:( 11, 14 ), 12:( 11, 14 ), 13:( 12, 13 ) }
BIG_EYE_LOW = { row + 1:span for row, span in BIG_EYE.items() }
EYES = {
  "original": [ ( "E", BIG_EYE ), ( "E", { 9:( 17, 18 ), 10:( 16, 18 ), 11:( 16, 18 ), 12:( 16, 18 ), 13:( 17, 18 ) } ) ],
  "even": [ ( "E", BIG_EYE ), ( "E", { 9:( 17, 18 ), 10:( 16, 19 ), 11:( 16, 19 ), 12:( 16, 19 ), 13:( 17, 18 ) } ) ],
  "even_low": [ ( "E", BIG_EYE_LOW ), ( "E", { 10:( 17, 18 ), 11:( 16, 19 ), 12:( 16, 19 ), 13:( 16, 19 ), 14:( 17, 18 ) } ) ],
  "even_tall_up": [ ( "E", BIG_EYE_LOW ), ( "E", { 9:( 17, 18 ), 10:( 16, 19 ), 11:( 16, 19 ), 12:( 16, 19 ), 13:( 16, 19 ), 14:( 17, 18 ) } ) ],
  "even_tall_down": [ ( "E", BIG_EYE_LOW ), ( "E", { 10:( 17, 18 ), 11:( 16, 19 ), 12:( 16, 19 ), 13:( 16, 19 ), 14:( 16, 19 ), 15:( 17, 18 ) } ) ],
  # Blink frame for the lidded eyes: lid lines on the gold just above the band, so they stay visible.
  "lidded_closed": [ ( "E", { 11:( 11, 14 ) } ), ( "E", { 12:( 16, 19 ) } ) ],
  # Hand-tuned in 35.png: both eyes open into the band at the bottom.
  "lidded": [
    ( "E", { 8:( 12, 13 ), 9:( 11, 14 ), 10:( 11, 14 ), 11:( 11, 14 ), 12:( 11, 14 ) } ),
    ( "E", { 13:( 11, 11 ) } ),
    ( "E", { 13:( 14, 14 ) } ),
    ( "E", { 9:( 17, 18 ), 10:( 16, 19 ), 11:( 16, 19 ), 12:( 16, 19 ), 13:( 16, 19 ) } ),
    ( "E", { 14:( 16, 16 ) } ),
    ( "E", { 14:( 19, 19 ) } ),
  ],
  # The far eye is narrower, as it turns away with the head.
  "depth": [
    ( "E", BIG_EYE_LOW ),
    ( "E", { 10:( 16, 18 ), 11:( 16, 18 ), 12:( 16, 18 ), 13:( 16, 18 ), 14:( 16, 18 ) } ),
    ( "e", { 10:( 16, 16 ), 14:( 16, 16 ) } ),
    ( "e", { 10:( 18, 18 ), 14:( 18, 18 ) } ),
  ],
}

# Extra parts, painted back to front. Feet sit behind the head, hand and mug in front of it.
EXTRAS = [
  ( "foot", True, { 22:( 14, 18 ), 23:( 13, 19 ), 24:( 13, 19 ), 25:( 14, 18 ) } ),
  ( "foot", True, { 21:( 3, 5 ), 22:( 2, 10 ), 23:( 2, 12 ), 24:( 3, 12 ), 25:( 4, 11 ) } ),
  ( "hand", False, { 15:( 1, 6 ), 16:( 0, 7 ), 17:( 0, 7 ), 18:( 0, 7 ), 19:( 1, 6 ) } ),
]
MUG = { 13:( 22, 26 ), 14:( 22, 26 ), 15:( 21, 26 ), 16:( 20, 26 ), 17:( 20, 26 ), 18:( 21, 26 ), 19:( 22, 26 ), 20:( 22, 26 ) }

# Where the mug sits: column shift and row drop, whether it hides behind the head, the small right hand holding it,
# how far the big hand moves toward it (columns, rows), whether the big hand is painted over the mug, and whether it steams.
MUG_PLACE_DEFAULTS = { "shift":0, "drop":0, "behind":False, "holding_hand":None, "hand_shift":0, "hand_drop":0, "hand_over_mug":False, "steam":True }
MUG_PLACES = {
  "front": {},
  # Behind the head the handle is hidden, so the far hand holding it is implied.
  "behind": { "shift":1, "behind":True },
  # Fingers wrapped around the handle, reaching onto the mug's left side.
  "held": { "holding_hand":{ 15:( 20, 21 ), 16:( 19, 22 ), 17:( 19, 22 ), 18:( 20, 21 ) } },
  # Palm under the mug, fingers over its bottom row.
  "held_under": { "holding_hand":{ 20:( 21, 24 ), 21:( 21, 25 ) } },
  # In front of the body near the centre, the big hand gripping the handle. Steam would run over the eyes, so none.
  "held_center": { "shift":-11, "drop":2, "hand_shift":3, "hand_drop":1, "hand_over_mug":True, "steam":False },
}
MUG_HOLE = { ( 21, 16 ), ( 21, 17 ) }
STEAM_PIXELS = [ ( 25, 12 ), ( 26, 11 ), ( 26, 10 ), ( 25, 9 ), ( 25, 8 ), ( 26, 7 ), ( 26, 6 ) ]

# Border of each extra part outside the head, the contours where the hand or mug meet the face,
# the band shape, whether the band's dark bottom row merges into the hand contour,
# whether the band is lit from the top-left with the grin running its full length, the eye shapes,
# whether the head's light ring sits inside or outside its black line, and whether the mug drops its edge above the rim.
DEFAULT_STYLE = {
  "contour":"gold", "mug_contour":"gold", "band":"rising", "band_at_hand":"plain", "band_light":"flat", "eyes":"original", "ring":"inside",
  "mug_rim":"edge", "mug_corner":"plain", "mug_border":"plain", "mug_top":"flat",
  "mug_place":"front", "steam_alpha":190, "shift_y":0, "facing":"right", "feet_light":"flat", "foot_toe":"on", "back_hand":"off", "close_gaps":"off", "steam_path":None,
  "foot_dx":( 0, 0 ), "foot_lift":( 0, 0 ), "hand_dx":0, "hand_dy":0, "back_hand_dx":0, "back_hand_dy":0, "cup_dx":0, "cup_dy":0, "steam_phase":None,
}
ARC_STYLE = { "band":"arc", "band_light":"shaded", "eyes":"even" }
ROUND_STYLE = { "foot":"black", "hand":"black", "mug":"dark", "mug_contour":"black", "band_light":"shaded", "band_at_hand":"merge", "mug_rim":"clean" }
# 35.png as hand-edited: 30 centred one row lower, with lidded eyes, a red mug top and stronger steam.
BASE_35 = { **ROUND_STYLE, "band":"round_2_right_low", "eyes":"lidded", "mug_top":"user_35", "steam_alpha":238, "shift_y":1 }
VARIANTS = {
  "1_double": { "foot":"double", "hand":"double", "mug":"double" },
  "2_white": { "foot":"white", "hand":"white", "mug":"white" },
  "3_none": { "foot":"none", "hand":"none", "mug":"none" },
  "4_self_dark": { "foot":"dark", "hand":"dark", "mug":"dark" },
  "5_white_mug_only": { "foot":"none", "hand":"none", "mug":"white" },
  "6_dark_body_white_mug": { "foot":"dark", "hand":"dark", "mug":"white" },
  "7_black_hand_feet": { "foot":"black", "hand":"black", "mug":"dark" },
  "8_black_hand": { "foot":"dark", "hand":"black", "mug":"dark" },
  "9_black_feet": { "foot":"black", "hand":"dark", "mug":"dark" },
  "10_black_hand_feet_contour": { "foot":"black", "hand":"black", "mug":"dark", "contour":"black", "mug_contour":"black" },
  "11_band_falling": { "foot":"dark", "hand":"dark", "mug":"dark", "band":"falling" },
  "12_band_falling_steep": { "foot":"dark", "hand":"dark", "mug":"dark", "band":"falling_steep" },
  "13_band_falling_black_hand_feet": { "foot":"black", "hand":"black", "mug":"dark", "band":"falling" },
  "14_band_low_black_handle": { "foot":"black", "hand":"black", "mug":"dark", "mug_contour":"black", "band":"falling_low", "band_at_hand":"merge" },
  "15_band_low_black_contours": { "foot":"black", "hand":"black", "mug":"dark", "contour":"black", "mug_contour":"black", "band":"falling_low", "band_at_hand":"merge" },
  "16_band_low_black_handle_ring_outside": { "foot":"black", "hand":"black", "mug":"dark", "mug_contour":"black", "band":"falling_low", "band_at_hand":"merge", "ring":"outside" },
  "17_arc_black_hand_feet": { "foot":"black", "hand":"black", "mug":"dark", **ARC_STYLE },
  "18_arc_black_handle": { "foot":"black", "hand":"black", "mug":"dark", "mug_contour":"black", **ARC_STYLE },
  "19_arc_black_contours": { "foot":"black", "hand":"black", "mug":"dark", "contour":"black", "mug_contour":"black", **ARC_STYLE },
  "20_round_band_2": { **ROUND_STYLE, "band":"round_2", "eyes":"even_low" },
  "21_round_band_3": { **ROUND_STYLE, "band":"round_3", "eyes":"even_low" },
  "22_round_band_2_depth_eyes": { **ROUND_STYLE, "band":"round_2", "eyes":"depth" },
  "23_round_band_3_depth_eyes": { **ROUND_STYLE, "band":"round_3", "eyes":"depth" },
  "24_band_right_low": { **ROUND_STYLE, "band":"round_2_right_low", "eyes":"even_low", "mug_corner":"dark" },
  "25_band_right_low_eye_up": { **ROUND_STYLE, "band":"round_2_right_low", "eyes":"even_tall_up", "mug_corner":"dark" },
  "26_band_right_low_eye_down": { **ROUND_STYLE, "band":"round_2_right_low", "eyes":"even_tall_down", "mug_corner":"dark" },
  "27_mug_side_dark": { **ROUND_STYLE, "band":"round_2_right_low", "eyes":"even_tall_up", "mug_corner":"dark_side" },
  "28_mug_border_top": { **ROUND_STYLE, "band":"round_2_right_low", "eyes":"even_tall_up", "mug_border":"top" },
  "29_mug_border_top_right": { **ROUND_STYLE, "band":"round_2_right_low", "eyes":"even_tall_up", "mug_border":"top_right" },
  "30_plain_mug": { **ROUND_STYLE, "band":"round_2_right_low", "eyes":"even_tall_up" },
  "31_natural_mug_top": { **ROUND_STYLE, "band":"round_2_right_low", "eyes":"even_tall_up", "mug_top":"natural" },
  "32_mug_top_red_rim": { **ROUND_STYLE, "band":"round_2_right_low", "eyes":"even_tall_up", "mug_top":"red_rim" },
  "33_mug_top_inner_shadow": { **ROUND_STYLE, "band":"round_2_right_low", "eyes":"even_tall_up", "mug_top":"inner_shadow" },
  "34_mug_top_red_coffee": { **ROUND_STYLE, "band":"round_2_right_low", "eyes":"even_tall_up", "mug_top":"red_coffee" },
  "36_mug_behind_head": { **BASE_35, "mug_place":"behind" },
  "37_mug_held_by_handle": { **BASE_35, "mug_place":"held" },
  "38_mug_held_from_below": { **BASE_35, "mug_place":"held_under" },
  "39_facing_left": { **BASE_35, "facing":"left" },
  "40_facing_left_cup_held": { **BASE_35, "facing":"left", "mug_place":"held_center" },
  "41_facing_left_cup_held_feet_shaded": { **BASE_35, "facing":"left", "mug_place":"held_center", "feet_light":"shadowed", "foot_toe":"off" },
  "42_facing_left_back_hand": { **BASE_35, "facing":"left", "mug_place":"held_center", "back_hand":"on" },
  "43_facing_left_back_hand_feet_shaded": { **BASE_35, "facing":"left", "mug_place":"held_center", "back_hand":"on", "feet_light":"shadowed", "foot_toe":"off" },
  "44_facing_left_back_hand_hidden": { **BASE_35, "facing":"left", "mug_place":"held_center", "back_hand":"hidden" },
  "45_facing_left_back_hand_low": { **BASE_35, "facing":"left", "mug_place":"held_center", "back_hand":"hidden_low" },
  "46_back_hand_hidden_no_gap": { **BASE_35, "facing":"left", "mug_place":"held_center", "back_hand":"hidden", "close_gaps":"on" },
  "47_back_hand_low_narrow": { **BASE_35, "facing":"left", "mug_place":"held_center", "back_hand":"low_narrow", "close_gaps":"on" },
  "48_back_hand_low_short": { **BASE_35, "facing":"left", "mug_place":"held_center", "back_hand":"low_short", "close_gaps":"on" },
  "49_back_hand_mid_narrow": { **BASE_35, "facing":"left", "mug_place":"held_center", "back_hand":"mid_narrow", "close_gaps":"on" },
  "50_cup_held_steam_between_eyes": { **BASE_35, "facing":"left", "mug_place":"held_center", "back_hand":"low_narrow", "close_gaps":"on", "steam_path":"between_eyes" },
  "51_cup_held_steam_right": { **BASE_35, "facing":"left", "mug_place":"held_center", "back_hand":"low_narrow", "close_gaps":"on", "steam_path":"right" },
  "52_cup_held_steam_right_short": { **BASE_35, "facing":"left", "mug_place":"held_center", "back_hand":"low_narrow", "close_gaps":"on", "steam_path":"right_short" },
  "53_cup_held_steam_over_eye": { **BASE_35, "facing":"left", "mug_place":"held_center", "back_hand":"low_narrow", "close_gaps":"on", "steam_path":"over_eye" },
  "54_cup_held_steam_over_eye_soft": { **BASE_35, "facing":"left", "mug_place":"held_center", "back_hand":"low_narrow", "close_gaps":"on", "steam_path":"over_eye", "steam_alpha":160 },
  "55_cup_held_steam_over_eye_tall": { **BASE_35, "facing":"left", "mug_place":"held_center", "back_hand":"low_narrow", "close_gaps":"on", "steam_path":"over_eye_tall" },
}
# Final sprites and their walk cycle: front foot (toward the facing side) and back foot column shifts,
# the passing foot lifted 1px off the ground while the body stays level,
# the arms swinging against the legs, the cup moving with the hand that holds it, and the steam rising off it.
FINAL = { "right":"36_mug_behind_head", "left":"54_cup_held_steam_over_eye_soft" }
# Walk with the cup only bobbing with the body: no sway, and the hand holding it stays still too.
WALK_FRAMES = {
  "right": [
    { "foot_dx":( 1, -1 ), "hand_dx":1, "steam_phase":0 },
    { "foot_lift":( 0, 1 ), "steam_phase":1 },
    { "foot_dx":( -1, 1 ), "hand_dx":-1, "steam_phase":2 },
    { "foot_lift":( 1, 0 ), "steam_phase":3 },
  ],
  # The offhand tucks 1px further behind the head for half the cycle, against the legs.
  "left": [
    { "foot_dx":( 1, -1 ), "steam_phase":0 },
    { "foot_lift":( 0, 1 ), "steam_phase":1 },
    { "foot_dx":( -1, 1 ), "back_hand_dx":-1, "steam_phase":2 },
    { "foot_lift":( 1, 0 ), "back_hand_dx":-1, "steam_phase":3 },
  ],
}
# Idle: the body and feet stay put, the steam rises, and he blinks once per loop.
BLINK_FRAME = 5
IDLE = [ { "steam_phase":index % 4 } for index in range( 8 ) ]
IDLE_FRAMES = { "right":IDLE, "left":IDLE }
IDLE_FRAME_MS = 180
# Transparent gap between frames on the spritesheets.
SHEET_GAP = 1
# How much the top steam pixels fade, from the very top down, and the faint puff that breaks off above on odd frames.
STEAM_FADE = [ 0.45, 0.75 ]
STEAM_PUFF = 0.3
WALK_FRAME_MS = 140

# Steam for the centred cup, as seen in the left-facing sprite: ( column, row ) in head coordinates after mirroring.
STEAM_PATHS = {
  # Straight up through the gap between the eyes.
  "between_eyes": [ ( 9, 13 ), ( 9, 12 ), ( 9, 11 ), ( 9, 10 ) ],
  # Rising from the cup's right side and curling over the cheek beside the big eye.
  "right": [ ( 14, 14 ), ( 14, 13 ), ( 15, 12 ), ( 15, 11 ), ( 14, 10 ), ( 14, 9 ), ( 15, 8 ) ],
  "right_short": [ ( 14, 14 ), ( 15, 13 ), ( 15, 12 ), ( 14, 11 ) ],
  # Straight up from the middle of the cup, in front of the big eye.
  "over_eye": [ ( 11, 13 ), ( 12, 12 ), ( 12, 11 ), ( 11, 10 ), ( 11, 9 ), ( 12, 8 ), ( 12, 7 ) ],
  "over_eye_tall": [ ( 11, 13 ), ( 11, 12 ), ( 12, 11 ), ( 12, 10 ), ( 11, 9 ), ( 10, 8 ), ( 10, 7 ), ( 11, 6 ), ( 11, 5 ) ],
}
# The far hand, peeking out from behind the head on the side opposite the big hand (head coordinates, before mirroring).
BACK_HAND = { 14:( 23, 25 ), 15:( 23, 26 ), 16:( 23, 26 ), 17:( 23, 26 ), 18:( 23, 25 ) }
BACK_HANDS = {
  "on": BACK_HAND,
  # Tucked 1px further behind the head and 1px lower.
  "hidden": { row + 1:( first - 1, last - 1 ) for row, ( first, last ) in BACK_HAND.items() },
  "hidden_low": { row + 2:( first - 1, last - 1 ) for row, ( first, last ) in BACK_HAND.items() },
  # Smaller offhands: one more column behind the head, or the top row dropped.
  "low_narrow": { row + 2:( first - 2, last - 2 ) for row, ( first, last ) in BACK_HAND.items() },
  "low_short": { row + 2:( first - 1, last - 1 ) for row, ( first, last ) in BACK_HAND.items() if row > 14 },
  "mid_narrow": { row + 1:( first - 2, last - 2 ) for row, ( first, last ) in BACK_HAND.items() },
}
# Replacement pixels for the mug's top row (head coordinates), lit from the top-left.
MUG_TOPS = {
  # Lit rim on the left, coffee catching light on its left, a light front lip under it.
  "natural": {
    ( 22, 13 ):"R", ( 23, 13 ):"c", ( 24, 13 ):"C", ( 25, 13 ):"C", ( 26, 13 ):"D",
    ( 23, 14 ):"l", ( 24, 14 ):"l", ( 25, 14 ):"l",
  },
  # No coffee showing, just the lit top of the rim.
  "red_rim": { ( 22, 13 ):"L", ( 23, 13 ):"R", ( 24, 13 ):"R", ( 25, 13 ):"R", ( 26, 13 ):"D" },
  # The inside of the mug in shadow, still red.
  "inner_shadow": { ( 22, 13 ):"R", ( 23, 13 ):"X", ( 24, 13 ):"X", ( 25, 13 ):"X", ( 26, 13 ):"D" },
  # Coffee tinted toward the mug's red.
  "red_coffee": { ( 22, 13 ):"R", ( 23, 13 ):"D", ( 24, 13 ):"r", ( 25, 13 ):"r", ( 26, 13 ):"D" },
  # Hand-tuned in 35.png.
  "user_35": { ( 22, 13 ):"R", ( 23, 13 ):"D", ( 24, 13 ):"D", ( 25, 13 ):"D", ( 26, 13 ):"D" },
}
# Mug pixels in head coordinates that turn darker on the top-right, away from the light.
MUG_DARK_CORNERS = {
  "dark": [ ( 26, 13 ), ( 26, 14 ), ( 25, 13 ) ],
  "dark_side": [ ( 26, 13 ), ( 26, 14 ), ( 26, 15 ) ],
}
# Darker pixels on the mug's 2px right border (its dark red column and the edge outside it), in head coordinates.
MUG_BORDER_SHADES = {
  "top": [ ( 26, 13 ), ( 27, 13 ) ],
  "top_right": [ ( 26, 13 ), ( 27, 13 ), ( 27, 14 ), ( 27, 15 ) ],
}

HEAD_RAMP = [ ( 252, 216, 124 ), ( 238, 188, 78 ), ( 218, 156, 44 ), ( 184, 122, 28 ), ( 146, 92, 20 ) ]
COLORS = {
  "#": ( 14, 9, 5 ),
  "q": ( 92, 56, 14 ),
  "m": ( 92, 56, 14 ),
  "B": ( 128, 98, 56 ),
  "b": ( 98, 74, 40 ),
  "d": ( 66, 48, 26 ),
  "E": ( 10, 6, 4 ),
  "e": ( 128, 86, 34 ),
  "W": ( 250, 248, 244 ),
  "w": ( 192, 186, 178 ),
  "C": ( 74, 34, 16 ),
  "c": ( 112, 60, 30 ),
  "l": ( 240, 74, 64 ),
  "r": ( 104, 26, 18 ),
  "L": ( 255, 108, 92 ),
  "R": ( 222, 34, 30 ),
  "D": ( 146, 14, 14 ),
  "X": ( 96, 6, 6 ),
  "Z": ( 58, 4, 4 ),
}
DARK_EDGE = { "foot":( 120, 74, 14 ), "hand":( 120, 74, 14 ), "mug":( 104, 8, 8 ) }
STEAM = ( 240, 240, 240 )
BACKGROUND = ( 51, 51, 51 )


def main():
  # Still sprites, plus previews with their drop shadow on a transparent background.
  for facing, variant in FINAL.items():
    sprite = draw( VARIANTS[ variant ] )
    sprite.save( OUTPUT_DIR / f"idle_{facing}.png" )
    preview( sprite ).save( OUTPUT_DIR / f"idle_{facing}-preview.png" )

  idle = save_animation( "idle", with_blink( IDLE_FRAMES, 1 ), IDLE_FRAME_MS )
  walk = save_animation( "walk", with_blink( WALK_FRAMES, 2 ), WALK_FRAME_MS )

  # Everything in one sheet: idle right, idle left, walk right, walk left.
  sheet( [ *idle.values(), *walk.values() ] ).save( OUTPUT_DIR / "spritesheet.png" )


def with_blink( frames_by_facing:dict, loops:int ):
  # Repeat the cycle so a single blink does not come around too often, and close the eyes on one frame.
  return {
    facing:[ { **frame, "eyes":"lidded_closed" } if index == BLINK_FRAME else frame for index, frame in enumerate( frames * loops ) ]
    for facing, frames in frames_by_facing.items()
  }


def save_animation( name:str, frames_by_facing:dict, frame_ms:int ):
  # GIF previews per direction on the EE picker background; returns the frames for the spritesheet.
  rows = { facing:[ draw( { **VARIANTS[ variant ], **frame } ) for frame in frames_by_facing[ facing ] ] for facing, variant in FINAL.items() }

  for facing, frames in rows.items():
    previews = [ preview( frame, BACKGROUND ).convert( "RGB" ) for frame in frames ]
    previews[ 0 ].save( OUTPUT_DIR / f"{name}_{facing}.gif", save_all=True, append_images=previews[ 1: ], duration=frame_ms, loop=0 )

  return rows


def sheet( rows:list ):
  frame_count = max( len( frames ) for frames in rows )
  width = frame_count * ( WIDTH + SHEET_GAP ) - SHEET_GAP
  height = len( rows ) * ( HEIGHT + SHEET_GAP ) - SHEET_GAP

  image = Image.new( "RGBA", ( width, height ), ( 0, 0, 0, 0 ) )
  for row, frames in enumerate( rows ):
    for column, frame in enumerate( frames ): image.paste( frame, ( column * ( WIDTH + SHEET_GAP ), row * ( HEIGHT + SHEET_GAP ) ) )

  return image


def draw( variant:dict ):
  styles = { **DEFAULT_STYLE, **variant }
  grid, edges = build_grid( styles )
  if styles[ "facing" ] == "left": grid, edges = mirror( grid ), mirror( edges )

  return shift_down( render( grid, edges, styles ), styles[ "shift_y" ] )


def build_grid( styles:dict ):
  grid = {}

  # Head: black circle, light ring along its inside, face fill.
  for row, line in enumerate( HEAD_CIRCLE ):
    columns = [ column for column, symbol in enumerate( line ) if symbol == "#" ]
    for column in range( min( columns ), max( columns ) + 1 ):
      grid[ to_canvas( column, row ) ] = "#" if line[ column ] == "#" else "h"

  for point in [ point for point, symbol in grid.items() if symbol == "h" ]:
    if any( grid.get( neighbor ) == "#" for neighbor in neighbors( point ) ): grid[ point ] = "o"

  head = set( grid )

  paint_band( grid, styles )

  face = dict( grid )
  for symbol, spans in EYES[ styles[ "eyes" ] ]:
    for point in span_points( spans ):
      # Soft corners only blend into the face, on the band they would read as light dots.
      if symbol == "e" and face.get( point ) != "h":
        grid[ point ] = face[ point ]
        continue

      grid[ point ] = symbol

  # Extras get a dark contour where they meet the face or each other, and a styled edge outside.
  place = mug_place( styles )
  mug_shift = place[ "shift" ] + styles[ "cup_dx" ]
  mug_drop = place[ "drop" ] + styles[ "cup_dy" ]
  mug_behind = place[ "behind" ]
  holding_hand = place[ "holding_hand" ]

  *feet, ( _, _, hand_spans ) = EXTRAS
  if styles[ "foot_toe" ] == "off": feet[ 1 ] = ( "foot", True, { row:span for row, span in feet[ 1 ][ 2 ].items() if row != 21 } )

  feet = [
    ( part, behind, lift_up( { row:( first + dx, last + dx ) for row, ( first, last ) in spans.items() }, lift ) )
    for ( part, behind, spans ), dx, lift in zip( feet, styles[ "foot_dx" ], styles[ "foot_lift" ] )
  ]

  hand_shift = place[ "hand_shift" ] + styles[ "hand_dx" ]
  hand_drop = place[ "hand_drop" ] + styles[ "hand_dy" ]
  big_hand = ( "hand", False, { row + hand_drop:( first + hand_shift, last + hand_shift ) for row, ( first, last ) in hand_spans.items() } )
  mug = ( "mug", mug_behind, { row + mug_drop:( first + mug_shift, last + mug_shift ) for row, ( first, last ) in MUG.items() } )

  back_hand_spans = BACK_HANDS.get( styles[ "back_hand" ] )
  if back_hand_spans:
    back_dx = styles[ "back_hand_dx" ]
    back_hand_spans = { row + styles[ "back_hand_dy" ]:( first + back_dx, last + back_dx ) for row, ( first, last ) in back_hand_spans.items() }
  back_hand = [ ( "hand", True, back_hand_spans ) ] if back_hand_spans else []
  extras = [ *back_hand, *feet, mug, big_hand ] if place[ "hand_over_mug" ] else [ *back_hand, *feet, big_hand, mug ]
  if holding_hand: extras.append( ( "hand", False, holding_hand ) )

  edges = {}
  for part, behind_head, spans in extras:
    fill = { point for point in span_points( spans ) if not ( behind_head and point in head ) }
    if part == "mug": fill -= { to_canvas( column + mug_shift, row + mug_drop ) for column, row in MUG_HOLE }

    for point in fill:
      grid[ point ] = "G" if spans is holding_hand else "J" if spans is back_hand_spans else part_symbol( part, point, mug_shift, mug_drop, styles[ "facing" ] )
      edges.pop( point, None )

    for point in { neighbor for point in fill for neighbor in neighbors( point ) } - fill:
      if behind_head and point in head: continue
      if grid.get( point ) == "#": continue

      if point in grid:
        grid[ point ] = "m" if part == "mug" else "q"
        continue

      if part == "mug" and styles[ "mug_rim" ] == "clean" and point[ 1 ] < min( y for _, y in fill ): continue

      edges[ point ] = part

  for point in MUG_DARK_CORNERS.get( styles[ "mug_corner" ], [] ): grid[ to_canvas( *point ) ] = "X"

  for ( column, row ), symbol in MUG_TOPS.get( styles[ "mug_top" ], {} ).items():
    lit_column = column if styles[ "facing" ] == "right" else 48 - column
    point = to_canvas( lit_column + mug_shift, row + mug_drop )
    if not ( mug_behind and point in head ): grid[ point ] = symbol

  # Let the hand contour act as the band's bottom line instead of stacking two dark rows.
  if styles[ "band_at_hand" ] == "merge":
    for ( x, y ), symbol in list( grid.items() ):
      if symbol == "d" and grid.get( ( x, y + 1 ) ) == "q": grid[ ( x, y ) ] = "b"

  return grid, edges


def paint_band( grid:dict, styles:dict ):
  shape = BAND_SHAPES[ styles[ "band" ] ]
  shaded = styles[ "band_light" ] == "shaded"

  for column in range( 2, 23 ):
    shift = next( row_shift for last_column, row_shift in shape if column <= last_column )
    top = BAND_TOP + shift

    # Light stays on the top-left, so a mirrored sprite picks its lit pixels from the other side.
    lit_column = column if styles[ "facing" ] == "right" else 24 - column
    body = "d" if lit_column >= 20 else "b"
    grin = "w" if lit_column >= 18 else "W"

    # Three band rows, a darker bottom row, then the grin. The right side turns away into shadow.
    rows = {
      top:"B" if shaded and lit_column <= 12 else body,
      top + 1:body,
      top + 2:body,
      top + 3:"d",
      top + 4:grin if shaded or column > 6 else "d",
    }
    for row, symbol in rows.items():
      point = to_canvas( column, row )
      if grid.get( point ) == "h": grid[ point ] = symbol


def render( grid:dict, edges:dict, styles:dict ):
  place = mug_place( styles )
  offset_x = OFFSET_X if styles[ "facing" ] == "right" else MIRRORED_OFFSET_X
  hand_shift = place[ "hand_shift" ] + styles[ "hand_dx" ]
  hand_light_column = 2 + hand_shift if styles[ "facing" ] == "right" else 18 - hand_shift
  hand_light = ( hand_light_column, 15 + place[ "hand_drop" ] + styles[ "hand_dy" ] )

  sprite = Image.new( "RGBA", ( WIDTH, HEIGHT ), ( 0, 0, 0, 0 ) )
  for ( x, y ), symbol in grid.items():
    color = back_hand_color( grid, x, y ) if symbol == "J" else pixel_color( symbol, x, y, offset_x, hand_light )
    if symbol == "F" and styles[ "feet_light" ] == "shadowed": color = foot_color( grid, x, y )
    if symbol == "q" and styles[ "contour" ] == "black": color = COLORS[ "#" ]
    if symbol == "m" and styles[ "mug_contour" ] == "black": color = COLORS[ "#" ]

    # Swapped head border: light ring outside, black line inside.
    if styles[ "ring" ] == "outside" and symbol == "#": color = ring_color( x, y, offset_x )
    if styles[ "ring" ] == "outside" and symbol == "o": color = COLORS[ "#" ]

    sprite.putpixel( ( x, y ), ( *color, 255 ) )

  edge_colors = { "dark":lambda part, point: DARK_EDGE[ part ], "black":lambda part, point: COLORS[ "#" ] }
  for point, part in edges.items():
    style = styles[ part ]
    if style == "none": continue

    color = edge_colors[ style ]( part, point ) if style in edge_colors else ring_color( *point, offset_x )
    sprite.putpixel( point, ( *color, 255 ) )

  # Double edges add a black line around the light one, like the head itself.
  double = [ point for point, part in edges.items() if styles[ part ] == "double" ]
  for point in { neighbor for point in double for neighbor in neighbors( point ) }:
    if point in grid or point in edges or not inside( point ): continue
    sprite.putpixel( point, ( *COLORS[ "#" ], 255 ) )

  for column, row in MUG_BORDER_SHADES.get( styles[ "mug_border" ], [] ):
    sprite.putpixel( to_canvas( column, row ), ( *COLORS[ "X" if column <= 26 else "Z" ], 255 ) )

  if styles[ "close_gaps" ] == "on": close_gaps( sprite )

  # Steam follows the cup. Side steam is listed in head coordinates before mirroring, face steam after it.
  facing_dx = styles[ "cup_dx" ] if styles[ "facing" ] == "right" else -styles[ "cup_dx" ]
  side_steam = []
  for x, y in STEAM_PIXELS if place[ "steam" ] else []:
    point = to_canvas( x + place[ "shift" ] + styles[ "cup_dx" ], y + styles[ "cup_dy" ] )
    if styles[ "facing" ] == "left": point = ( WIDTH - 1 - point[ 0 ], point[ 1 ] )
    side_steam.append( point )

  face_steam = [ ( column + offset_x + facing_dx, row + OFFSET_Y + styles[ "cup_dy" ] ) for column, row in STEAM_PATHS.get( styles[ "steam_path" ], [] ) ]

  if styles[ "steam_phase" ] is not None:
    draw_rising_steam( sprite, [ *side_steam, *face_steam ], styles[ "steam_phase" ], styles[ "steam_alpha" ] )
    return sprite

  for point in side_steam: sprite.putpixel( point, ( *STEAM, styles[ "steam_alpha" ] ) )

  # Steam drawn over the face blends into what is under it instead of punching a see-through hole.
  for point in face_steam: sprite.putpixel( point, blend( sprite.getpixel( point ), STEAM, styles[ "steam_alpha" ] / 255 ) )

  return sprite


def pixel_color( symbol:str, x:int, y:int, offset_x:int, hand_light:tuple ):
  column = x - offset_x
  row = y - OFFSET_Y

  # Round parts are lit from the top-left.
  if symbol == "h": return ramp( hypot( column - 8, row - 5 ) / 4.6 )
  if symbol == "H": return ramp( hypot( column - hand_light[ 0 ], row - hand_light[ 1 ] ) / 2.0 )
  if symbol == "F": return ramp( 2 if row < 24 else 3 )
  if symbol == "G": return ramp( 1 + hypot( column - 20, row - 16 ) / 1.6 )
  if symbol == "o": return ring_color( x, y, offset_x )

  return COLORS[ symbol ]


def foot_color( grid:dict, x:int, y:int ):
  # In the head's shadow at the top, on the ground at the bottom, lit on each foot's left side between.
  if grid.get( ( x, y - 1 ) ) != "F" or grid.get( ( x, y + 1 ) ) != "F": return HEAD_RAMP[ 4 ]
  if grid.get( ( x - 1, y ) ) != "F": return HEAD_RAMP[ 2 ]

  return HEAD_RAMP[ 3 ]


def lift_up( spans:dict, rows:int ):
  # Raise a whole foot off the ground; its top slips further behind the head.
  return { row - rows:span for row, span in spans.items() }


def back_hand_color( grid:dict, x:int, y:int ):
  # Mostly in the head's shadow, catching a little light on its outer side.
  return HEAD_RAMP[ 2 if grid.get( ( x - 1, y ) ) != "J" else 3 ]


def mug_place( styles:dict ):
  return { **MUG_PLACE_DEFAULTS, **MUG_PLACES[ styles[ "mug_place" ] ] }


def part_symbol( part:str, point:tuple, mug_shift:int, mug_drop:int, facing:str ):
  if part == "foot": return "F"
  if part == "hand": return "H"

  column = point[ 0 ] - OFFSET_X - mug_shift
  row = point[ 1 ] - OFFSET_Y - mug_drop
  lit_column, shaded_column = ( 22, 26 ) if facing == "right" else ( 26, 22 )

  if row == 13: return "C" if 23 <= column <= 25 else "D"
  if column <= 21: return "D"
  if column == lit_column: return "L"
  if column == shaded_column or row == 20: return "D"

  return "R"


def draw_rising_steam( sprite:Image.Image, wisp:list, phase:int, alpha:int ):
  # The bottom pixel stays on the cup; the wisp's side-to-side wave travels up a row each frame, so pixels seem to rise
  # and swap sides. The top fades out, and on odd frames a faint puff breaks off above it.
  base_x = min( x for x, _ in wisp )
  wave = [ x - base_x for x, _ in wisp[ :4 ] ]
  rising = [ ( base_x + wave[ ( index - phase ) % len( wave ) ], y ) for index, ( _, y ) in enumerate( wisp ) ]

  for index, point in enumerate( rising ):
    from_top = len( rising ) - 1 - index
    paint_steam( sprite, point, alpha / 255 * ( STEAM_FADE[ from_top ] if from_top < len( STEAM_FADE ) else 1 ) )

  top_x, top_y = rising[ -1 ]
  if phase % 2: paint_steam( sprite, ( base_x + wave[ ( len( rising ) - phase ) % len( wave ) ], top_y - 2 ), alpha / 255 * STEAM_PUFF )


def paint_steam( sprite:Image.Image, point:tuple, amount:float ):
  if not inside( point ): return

  under = sprite.getpixel( point )
  sprite.putpixel( point, ( *STEAM, round( amount * 255 ) ) if not under[ 3 ] else blend( under, STEAM, amount ) )


def blend( under:tuple, color:tuple, amount:float ):
  *under_color, under_alpha = under
  mixed = tuple( round( base * ( 1 - amount ) + top * amount ) for base, top in zip( under_color, color ) )

  return ( *mixed, max( under_alpha, round( amount * 255 ) ) )


def close_gaps( sprite:Image.Image ):
  # Fill single empty pixels pinched between outlines, so no hole shows through the silhouette.
  alpha = sprite.getchannel( "A" ).load()
  gaps = [
    ( x, y )
    for x in range( WIDTH ) for y in range( HEIGHT )
    if not alpha[ x, y ] and sum( 1 for point in neighbors( ( x, y ) ) if inside( point ) and alpha[ point ] ) >= 3
  ]
  for point in gaps: sprite.putpixel( point, ( *COLORS[ "#" ], 255 ) )


def mirror( pixels:dict ):
  return { ( WIDTH - 1 - x, y ):value for ( x, y ), value in pixels.items() }


def shift_down( sprite:Image.Image, rows:int ):
  if not rows: return sprite

  shifted = Image.new( "RGBA", sprite.size, ( 0, 0, 0, 0 ) )
  shifted.paste( sprite, ( 0, rows ) )

  return shifted


def ring_color( x:int, y:int, offset_x:int ):
  # Bright on the top-left, grey on the bottom-right.
  direction_x = x - offset_x - HEAD_CENTER
  direction_y = y - OFFSET_Y - HEAD_CENTER
  light = -( direction_x + direction_y ) / ( hypot( direction_x, direction_y ) * 1.414 + 0.001 )
  value = int( 200 + light * 55 )

  return ( value, value, value )


def ramp( shade:float ):
  return HEAD_RAMP[ min( int( shade ), len( HEAD_RAMP ) - 1 ) ]


def span_points( spans:dict ):
  return { to_canvas( column, row ) for row, ( first, last ) in spans.items() for column in range( first, last + 1 ) }


def to_canvas( column:int, row:int ):
  return ( column + OFFSET_X, row + OFFSET_Y )


def neighbors( point:tuple ):
  x, y = point
  return [ ( x + 1, y ), ( x - 1, y ), ( x, y + 1 ), ( x, y - 1 ) ]


def inside( point:tuple ):
  return 0 <= point[ 0 ] < WIDTH and 0 <= point[ 1 ] < HEIGHT


def preview( sprite:Image.Image, background:tuple = None ):
  # Drop shadow like the EE smiley picker, on a transparent background unless one is given.
  canvas_width = WIDTH + 4
  canvas_height = HEIGHT + 4
  alpha = sprite.getchannel( "A" )

  shadow = Image.new( "RGBA", ( canvas_width, canvas_height ), ( 0, 0, 0, 0 ) )
  shadow.paste( ( 0, 0, 0, 150 ), ( 3, 3 ), alpha )
  shadow = shadow.filter( ImageFilter.GaussianBlur( 0.8 ) )

  canvas = Image.new( "RGBA", ( canvas_width, canvas_height ), ( *background, 255 ) if background else ( 0, 0, 0, 0 ) )
  canvas.alpha_composite( shadow )
  canvas.alpha_composite( sprite, ( 1, 1 ) )

  return canvas.resize( ( canvas_width * PREVIEW_SCALE, canvas_height * PREVIEW_SCALE ), Image.NEAREST )


main()
