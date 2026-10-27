"""Everybody Edits character engine: a 25 px round head core plus addon parts, exported as stills, previews,
a spritesheet and GIFs. A character is a `generator.py` module that defines CANVAS, HEAD, parts(), FINAL, VARIANTS and
ANIMATIONS, then calls run( globals() ). Everything is authored facing right; the left-facing sprite is the mirror,
re-shaded so the light still comes from the top-left."""

import shutil
import sys
from dataclasses import dataclass, field
from math import hypot
from pathlib import Path
from PIL import Image, ImageFilter

# EE head core: 25 px circle outline, matching the game's smiley shape.
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
HEAD_SIZE = 25
HEAD_CENTER = 12

BLACK = ( 14, 9, 5 )
EYE_BLACK = ( 10, 6, 4 )
STEAM = ( 240, 240, 240 )
PICKER_BACKGROUND = ( 51, 51, 51 )

# Gold skin of the default EE smiley, light to dark.
GOLD = [ ( 252, 216, 124 ), ( 238, 188, 78 ), ( 218, 156, 44 ), ( 184, 122, 28 ), ( 146, 92, 20 ) ]

PREVIEW_SCALE = 12
COMPARE_SCALE = 8
SHADOW_ALPHA = 150
STEAM_FADE = [ 0.45, 0.75 ]
STEAM_PUFF = 0.3
SHEET_GAP = 1
# Approval stages, in order; each one is exported to the character folder when the user approves it.
STAGES = ( "look", "directions", "idle", "move" )


@dataclass
class Canvas:
  # Frame size around the head: side margins are equal so the mirrored sprite fits the same frame.
  margin_x:int = 3
  top:int = 1
  bottom:int = 3

  @property
  def width( self ): return HEAD_SIZE + 2 * self.margin_x

  @property
  def height( self ): return self.top + HEAD_SIZE + self.bottom


@dataclass
class Material:
  # How a part's pixels are coloured. shading: radial (distance from a light point, top-left of the part unless
  # `light` gives head coordinates), flat (ramp[ level ]), edge (lit top/left rim, shaded bottom/right rim),
  # rows (one ramp step per row from the part's top). `ring` tints the head's light ring (white by default).
  # `border( column, row, kind )` restyles the head's border pixels (kind "black" or "ring", head coordinates as seen
  # on the final sprite): None keeps the pixel, "fill" turns it into face fill, an RGB paints it that colour,
  # "clear" removes it so the head shrinks and parts behind can show there, "edge" makes it face fill that turns black
  # only where it borders empty space after all parts are drawn.
  ramp:list
  shading:str = "radial"
  level:int = 0
  step:float = 2.0
  light:tuple = None
  contour:tuple = None
  ring:tuple = None
  border:object = None
  alpha:int = 255

  def contour_color( self ):
    return self.contour or tuple( round( channel * 0.62 ) for channel in self.ramp[ -1 ] )


@dataclass
class Part:
  # A grid of symbols placed in head coordinates (column, row of the grid's top-left; the head spans 0..24).
  # depth: face (painted on the face only), behind (clipped by the head), front (over the head).
  # outline: True (black), False, an RGB/RGBA colour, or a function( column, row ) in head coordinates returning a
  # colour or None (no outline there), for dotted or glowing edges. edges=False skips outline and contour entirely,
  # for loose pixels (sparks, embers) painted over whatever is there.
  name:str
  grid:list
  at:tuple
  palette:dict
  depth:str = "front"
  outline:bool = True
  states:dict = field( default_factory=dict )
  edges:bool = True


@dataclass
class Wisp:
  # Steam or smoke rising from a part: path from bottom to top in head coordinates, moving with `anchor`.
  anchor:str
  path:list
  alpha:int = 238


@dataclass
class Frame:
  # Part offsets (dx > 0 is always forward, toward the facing side), part states (e.g. closed eyes),
  # whole-sprite bob in rows (only for characters that float) and the phase of rising steam.
  offsets:dict = field( default_factory=dict )
  states:dict = field( default_factory=dict )
  bob:int = 0
  phase:int = None


@dataclass
class Animation:
  frames:list
  ms:int = 140
  frames_left:list = None


def run( character:dict ):
  # Command line of a character's generator.py: still <variant> [facing], variants [right|left|both],
  # preview <variant> [animation], export [look|directions|idle|move], diff <png> [variant] [facing], clean.
  # Without a command it exports every stage, so only run it bare once all stages are approved.
  command, *arguments = sys.argv[ 1: ] or [ "export" ]
  folder = Path( character[ "__file__" ] ).resolve().parent
  if command == "still": return save_still( character, folder / "_work", *arguments )
  if command == "export": return export( character, folder, *arguments )
  if command == "variants": return save_variants( character, folder / "_work", *arguments )
  if command == "preview": return save_animations( character, folder / "_work", character[ "VARIANTS" ][ arguments[ 0 ] ], f"{arguments[ 0 ]}_", arguments[ 1: ] )
  if command == "diff": return print_diff( character, *arguments )
  if command == "clean": return shutil.rmtree( folder / "_work", ignore_errors=True )

  raise SystemExit( f"unknown command {command}" )


def export( character:dict, folder:Path, stage:str = None ):
  # Approved assets of one stage, or of all of them: look (right still), directions (left still), idle (its GIFs and
  # a spritesheet of the idle rows), move (all animation GIFs and the full spritesheet).
  if stage not in ( None, *STAGES ): raise SystemExit( f"unknown stage {stage}, use one of {', '.join( STAGES )}" )

  options = character[ "FINAL" ]
  facings = { "look":[ "right" ], "directions":[ "left" ], None:[ "right", "left" ] }.get( stage, [] )
  for facing in facings:
    still = render( character, facing, Frame(), options )
    still.save( folder / f"idle_{facing}.png" )
    preview( still ).save( folder / f"idle_{facing}-preview.png" )

  if stage in ( "look", "directions" ): return

  rows = save_animations( character, folder, options, "", [ "idle" ] if stage == "idle" else [] )
  sheet( rows ).save( folder / "spritesheet.png" )


def save_animations( character:dict, folder:Path, options:dict, prefix:str, names:list = () ):
  # One GIF per animation and facing on the EE picker background; returns the frame rows for the spritesheet.
  # A variant's own "animations" option replaces the character's ANIMATIONS; `names` limits which are rendered.
  folder.mkdir( exist_ok=True )
  rows = []
  for name, animation in options.get( "animations", character[ "ANIMATIONS" ] ).items():
    if names and name not in names: continue

    for facing in ( "right", "left" ):
      frames = animation.frames_left if facing == "left" and animation.frames_left else animation.frames
      images = [ render( character, facing, frame, options ) for frame in frames ]
      previews = [ preview( image, PICKER_BACKGROUND ).convert( "RGB" ) for image in images ]
      previews[ 0 ].save( folder / f"{prefix}{name}_{facing}.gif", save_all=True, append_images=previews[ 1: ], duration=animation.ms, loop=0 )
      rows.append( images )

  return rows


def save_still( character:dict, folder:Path, variant:str, facing:str = "right" ):
  # One proposal: the still, its preview, and a sheet with it enlarged plus 1x and 2x copies to judge at game size.
  folder.mkdir( exist_ok=True )
  image = render( character, facing, Frame(), character[ "VARIANTS" ][ variant ] )
  image.save( folder / f"{variant}_{facing}.png" )
  preview( image ).save( folder / f"{variant}_{facing}_preview.png" )
  compare_sheet( [ ( variant, [ image ] ) ] ).save( folder / f"{variant}_{facing}_view.png" )


def save_variants( character:dict, folder:Path, facing:str = "right" ):
  # Every numbered try as its own still and preview, plus one comparison sheet with 1x and 2x copies.
  folder.mkdir( exist_ok=True )
  facings = [ "right", "left" ] if facing == "both" else [ facing ]
  tiles = []
  for name, options in character[ "VARIANTS" ].items():
    pair = []
    for facing in facings:
      image = render( character, facing, Frame(), options )
      image.save( folder / f"{name}_{facing}.png" )
      preview( image ).save( folder / f"{name}_{facing}_preview.png" )
      pair.append( image )
    tiles.append( ( name, pair ) )

  compare_sheet( tiles ).save( folder / "compare.png" )


def compare_sheet( tiles:list ):
  # Rows of variants: each facing enlarged, then 1x and 2x copies to judge them at game size.
  width, height = tiles[ 0 ][ 1 ][ 0 ].size
  tile_width = width * COMPARE_SCALE + 8
  row_height = height * COMPARE_SCALE + 8
  facings = len( tiles[ 0 ][ 1 ] )

  image = Image.new( "RGBA", ( tile_width * facings + width * 3 + 24, row_height * len( tiles ) ), ( *PICKER_BACKGROUND, 255 ) )
  for row, ( _, pair ) in enumerate( tiles ):
    top = row * row_height + 4
    for column, sprite in enumerate( pair ):
      image.alpha_composite( sprite.resize( ( width * COMPARE_SCALE, height * COMPARE_SCALE ), Image.NEAREST ), ( column * tile_width + 4, top ) )

    small_x = tile_width * facings + 8
    image.alpha_composite( pair[ 0 ], ( small_x, top ) )
    image.alpha_composite( pair[ 0 ].resize( ( width * 2, height * 2 ), Image.NEAREST ), ( small_x, top + height + 8 ) )

  return image


def print_diff( character:dict, path:str, variant:str = None, facing:str = "right" ):
  # Pixels where a (hand-edited) PNG differs from the generator, in head coordinates, to reproduce edits exactly.
  options = character[ "VARIANTS" ][ variant ] if variant else character[ "FINAL" ]
  mine = render( character, facing, Frame(), options )
  theirs = Image.open( path ).convert( "RGBA" )
  canvas = character[ "CANVAS" ]

  differences = [
    ( x - canvas.margin_x, y - canvas.top, mine.getpixel( ( x, y ) ), theirs.getpixel( ( x, y ) ) )
    for x in range( mine.width ) for y in range( mine.height )
    if mine.getpixel( ( x, y ) ) != theirs.getpixel( ( x, y ) )
  ]
  for column, row, before, after in differences: print( f"head ( {column}, {row} ): {before} -> {after}" )

  print( f"{len( differences )} differing pixels" )


def render( character:dict, facing:str, frame:Frame, options:dict ):
  canvas = character[ "CANVAS" ]
  items = character[ "parts" ]( facing, options )
  parts = [ item for item in items if isinstance( item, Part ) ]
  wisps = [ item for item in items if isinstance( item, Wisp ) ]

  cells = compose( canvas, options.get( "head", character[ "HEAD" ] ), parts, frame, facing )
  if not options.get( "open_gaps" ): close_gaps( cells, canvas )
  if facing == "left": cells = mirror( cells, canvas )

  sprite = paint( cells, canvas )
  for wisp in wisps: draw_wisp( sprite, wisp, frame, canvas, facing )

  return shift( sprite, frame.bob )


def compose( canvas:Canvas, head_material:Material, parts:list, frame:Frame, facing:str = "right" ):
  # Cells map a canvas point to ( kind, value, part ): "black", "ring", "mat" (a Material) or "color" (an RGB).
  cells, edges = head_cells( canvas, head_material, facing )
  head = set( cells )
  face = { point for point, cell in cells.items() if cell[ 0 ] == "mat" }

  for part in [ part for part in parts if part.depth == "face" ]:
    for point, material in part_pixels( part, frame, canvas ).items():
      if point in face: cells[ point ] = ( "mat", material, part.name )

  for depth in ( "behind", "front" ):
    for part in [ part for part in parts if part.depth == depth ]:
      pixels = part_pixels( part, frame, canvas )
      if depth == "behind": pixels = { point:material for point, material in pixels.items() if point not in head }

      for point, material in pixels.items(): cells[ point ] = ( "mat", material, part.name )

      if part.edges: add_edges( cells, pixels, part, head if depth == "behind" else set(), canvas )

  # "edge" border pixels turn black only where nothing covers the outside of the head.
  for point in edges:
    if cells[ point ][ 0 ] == "mat" and any( neighbor not in cells for neighbor in neighbors( point ) ): cells[ point ] = ( "black", None, "head" )

  return cells


def head_cells( canvas:Canvas, material:Material, facing:str = "right" ):
  # Black circle, a light ring along its inside, and the face fill.
  cells = {}
  for row, line in enumerate( HEAD_CIRCLE ):
    columns = [ column for column, symbol in enumerate( line ) if symbol == "#" ]
    for column in range( min( columns ), max( columns ) + 1 ):
      point = ( canvas.margin_x + column, canvas.top + row )
      cells[ point ] = ( "black", None, "head" ) if line[ column ] == "#" else ( "mat", material, "head" )

  ring = [ point for point, cell in cells.items() if cell[ 0 ] == "mat" and any( cells.get( neighbor, ( None, ) )[ 0 ] == "black" for neighbor in neighbors( point ) ) ]
  for point in ring: cells[ point ] = ( "ring", material.ring, "head" )

  edges = restyle_border( cells, canvas, material, facing ) if material.border else set()

  return cells, edges


def restyle_border( cells:dict, canvas:Canvas, material:Material, facing:str ):
  # The border hook sees head coordinates of the final sprite, so the left side is asked about its mirrored pixel.
  edges = set()
  for point, ( kind, _, _ ) in list( cells.items() ):
    if kind not in ( "black", "ring" ): continue

    column = point[ 0 ] - canvas.margin_x
    row = point[ 1 ] - canvas.top
    style = material.border( 2 * HEAD_CENTER - column if facing == "left" else column, row, kind )
    if style is None: continue

    if style == "clear":
      del cells[ point ]
      continue

    if style == "edge": edges.add( point )

    cells[ point ] = ( "mat", material, "head" ) if style in ( "fill", "edge" ) else ( "color", style, "head" )

  return edges


def part_pixels( part:Part, frame:Frame, canvas:Canvas ):
  grid = part.states.get( frame.states.get( part.name ), part.grid )
  dx, dy = frame.offsets.get( part.name, ( 0, 0 ) )
  column, row = part.at

  return {
    ( canvas.margin_x + column + dx + x, canvas.top + row + dy + y ):part.palette[ symbol ]
    for y, line in enumerate( grid ) for x, symbol in enumerate( line ) if symbol != "."
  }


def add_edges( cells:dict, pixels:dict, part:Part, skip:set, canvas:Canvas ):
  # A contour where the part meets anything already drawn, a black outline where it meets empty space.
  contour = next( iter( pixels.values() ) ).contour_color() if pixels else BLACK
  for point in { neighbor for point in pixels for neighbor in neighbors( point ) } - set( pixels ):
    if point in skip or not inside( point, canvas ): continue

    existing = cells.get( point )
    if existing and existing[ 0 ] == "black": continue

    if existing:
      cells[ point ] = ( "color", contour, part.name )
      continue

    if part.outline is True: cells[ point ] = ( "black", None, part.name )
    elif callable( part.outline ):
      color = part.outline( point[ 0 ] - canvas.margin_x, point[ 1 ] - canvas.top )
      if color: cells[ point ] = ( "color", color, part.name )
    elif part.outline: cells[ point ] = ( "color", part.outline, part.name )


def close_gaps( cells:dict, canvas:Canvas ):
  # Single empty pixels pinched between outlines turn black, so no hole shows through the silhouette.
  gaps = [
    ( x, y )
    for x in range( canvas.width ) for y in range( canvas.height )
    if ( x, y ) not in cells and sum( 1 for neighbor in neighbors( ( x, y ) ) if neighbor in cells ) >= 3
  ]
  for point in gaps: cells[ point ] = ( "black", None, "gap" )


def mirror( cells:dict, canvas:Canvas ):
  axis = 2 * ( canvas.margin_x + HEAD_CENTER )
  return { ( axis - x, y ):cell for ( x, y ), cell in cells.items() }


def paint( cells:dict, canvas:Canvas ):
  # Colours are picked after mirroring, so lit and shaded sides always follow the top-left light.
  boxes = part_boxes( cells )
  sprite = Image.new( "RGBA", ( canvas.width, canvas.height ), ( 0, 0, 0, 0 ) )
  for point, ( kind, value, part ) in cells.items():
    if kind == "black": color = BLACK
    elif kind == "ring": color = ring_color( point, canvas, value )
    elif kind == "color": color = value
    else: color = ( *shade( value, point, boxes[ part ], cells, part, canvas ), value.alpha )

    sprite.putpixel( point, color if len( color ) == 4 else ( *color, 255 ) )

  return sprite


def part_boxes( cells:dict ):
  boxes = {}
  for ( x, y ), ( kind, _, part ) in cells.items():
    if kind != "mat": continue

    x0, y0, x1, y1 = boxes.get( part, ( x, y, x, y ) )
    boxes[ part ] = ( min( x0, x ), min( y0, y ), max( x1, x ), max( y1, y ) )

  return boxes


def shade( material:Material, point:tuple, box:tuple, cells:dict, part:str, canvas:Canvas ):
  x, y = point
  x0, y0, x1, y1 = box
  level = material.level

  if material.shading == "radial":
    light_x, light_y = ( canvas.margin_x + material.light[ 0 ], canvas.top + material.light[ 1 ] ) if material.light else ( x0 + ( x1 - x0 ) * 0.3, y0 + ( y1 - y0 ) * 0.3 )
    level += int( hypot( x - light_x, y - light_y ) / material.step )

  if material.shading == "rows": level += y - y0

  if material.shading == "edge":
    same = lambda neighbor: cells.get( neighbor, ( None, None, None ) )[ 2 ] == part
    if not same( ( x - 1, y ) ) or not same( ( x, y - 1 ) ): level -= 1
    elif not same( ( x + 1, y ) ) or not same( ( x, y + 1 ) ): level += 1

  return material.ramp[ max( 0, min( level, len( material.ramp ) - 1 ) ) ]


def ring_color( point:tuple, canvas:Canvas, tint:tuple = None ):
  # Bright on the top-left, grey on the bottom-right; a tint colours it the same way.
  direction_x = point[ 0 ] - canvas.margin_x - HEAD_CENTER
  direction_y = point[ 1 ] - canvas.top - HEAD_CENTER
  light = -( direction_x + direction_y ) / ( hypot( direction_x, direction_y ) * 1.414 + 0.001 )
  value = int( 200 + light * 55 )
  if tint: return tuple( round( channel * value / 255 ) for channel in tint )

  return ( value, value, value )


def draw_wisp( sprite:Image.Image, wisp:Wisp, frame:Frame, canvas:Canvas, facing:str ):
  # The bottom pixel stays on its source; the side-to-side wave travels up a row per frame so pixels seem to rise and
  # swap sides. The top fades out and on odd frames a faint puff breaks off above. A still frame draws the plain path.
  dx, dy = frame.offsets.get( wisp.anchor, ( 0, 0 ) )
  axis = 2 * ( canvas.margin_x + HEAD_CENTER )
  points = []
  for column, row in wisp.path:
    x = canvas.margin_x + column + dx
    points.append( ( axis - x if facing == "left" else x, canvas.top + row + dy ) )

  if frame.phase is None:
    for point in points: paint_steam( sprite, point, wisp.alpha / 255 )
    return

  base_x = min( x for x, _ in points )
  wave = [ x - base_x for x, _ in points[ :4 ] ]
  rising = [ ( base_x + wave[ ( index - frame.phase ) % len( wave ) ], y ) for index, ( _, y ) in enumerate( points ) ]

  for index, point in enumerate( rising ):
    from_top = len( rising ) - 1 - index
    paint_steam( sprite, point, wisp.alpha / 255 * ( STEAM_FADE[ from_top ] if from_top < len( STEAM_FADE ) else 1 ) )

  top_y = rising[ -1 ][ 1 ]
  if frame.phase % 2: paint_steam( sprite, ( base_x + wave[ ( len( rising ) - frame.phase ) % len( wave ) ], top_y - 2 ), wisp.alpha / 255 * STEAM_PUFF )


def paint_steam( sprite:Image.Image, point:tuple, amount:float ):
  if not ( 0 <= point[ 0 ] < sprite.width and 0 <= point[ 1 ] < sprite.height ): return

  *under, under_alpha = sprite.getpixel( point )
  if not under_alpha: return sprite.putpixel( point, ( *STEAM, round( amount * 255 ) ) )

  mixed = tuple( round( base * ( 1 - amount ) + top * amount ) for base, top in zip( under, STEAM ) )
  sprite.putpixel( point, ( *mixed, under_alpha ) )


def shift( sprite:Image.Image, rows:int ):
  if not rows: return sprite

  shifted = Image.new( "RGBA", sprite.size, ( 0, 0, 0, 0 ) )
  shifted.paste( sprite, ( 0, rows ) )

  return shifted


def preview( sprite:Image.Image, background:tuple = None ):
  # Drop shadow like the EE smiley picker, on a transparent background unless one is given.
  width = sprite.width + 4
  height = sprite.height + 4

  shadow = Image.new( "RGBA", ( width, height ), ( 0, 0, 0, 0 ) )
  shadow.paste( ( 0, 0, 0, SHADOW_ALPHA ), ( 3, 3 ), sprite.getchannel( "A" ) )
  shadow = shadow.filter( ImageFilter.GaussianBlur( 0.8 ) )

  canvas = Image.new( "RGBA", ( width, height ), ( *background, 255 ) if background else ( 0, 0, 0, 0 ) )
  canvas.alpha_composite( shadow )
  canvas.alpha_composite( sprite, ( 1, 1 ) )

  return canvas.resize( ( width * PREVIEW_SCALE, height * PREVIEW_SCALE ), Image.NEAREST )


def sheet( rows:list ):
  # One row per animation and facing, frames left to right, with a transparent gap between frames.
  width, height = rows[ 0 ][ 0 ].size
  frame_count = max( len( frames ) for frames in rows )

  image = Image.new( "RGBA", ( frame_count * ( width + SHEET_GAP ) - SHEET_GAP, len( rows ) * ( height + SHEET_GAP ) - SHEET_GAP ), ( 0, 0, 0, 0 ) )
  for row, frames in enumerate( rows ):
    for column, frame in enumerate( frames ): image.paste( frame, ( column * ( width + SHEET_GAP ), row * ( height + SHEET_GAP ) ) )

  return image


def blink( frames:list, part:str, state:str = "closed", at:int = 5 ):
  # Close the eyes on one frame of the loop.
  return [ Frame( frame.offsets, { **frame.states, part:state }, frame.bob, frame.phase ) if index == at else frame for index, frame in enumerate( frames ) ]


def make_ramp( base:tuple, steps:int = 5 ):
  # Light-to-dark ramp around a base colour, for new items and clothes.
  factors = [ 1.25, 1.1, 1.0, 0.82, 0.64 ][ :steps ]
  return [ tuple( min( 255, round( channel * factor ) ) for channel in base ) for factor in factors ]


def blob( spans:dict ):
  # Grid from { row:( first_column, last_column ) }, rows relative to the grid's top-left.
  width = max( last for _, last in spans.values() ) + 1
  return [ "".join( "x" if first <= column <= last else "." for column in range( width ) ) for row, ( first, last ) in sorted( spans.items() ) ]


def neighbors( point:tuple ):
  x, y = point
  return [ ( x + 1, y ), ( x - 1, y ), ( x, y + 1 ), ( x, y - 1 ) ]


def inside( point:tuple, canvas:Canvas ):
  return 0 <= point[ 0 ] < canvas.width and 0 <= point[ 1 ] < canvas.height
