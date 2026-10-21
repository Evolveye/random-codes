/**
 * Pixel Intro — a framework-agnostic splash effect.
 *
 * An image materialises cell by cell on a coarse grid (random order) in a bright,
 * glowing, slightly enlarged state, settles into its real colours and size,
 * then dissolves cell by cell again.
 *
 * Tint and glow are derived from the image's own local colours, so every part of
 * the image brightens and blooms in its own hue.
 *
 * Zero dependencies; works with vanilla JS, React, Svelte, Vue, ...
 */

export type PixelIntroTiming = {
  /** Empty screen before anything appears. */
  delay: number
  /** Cells popping in. */
  reveal: number
  /** Fully revealed, still bright & glowing. */
  hold: number
  /** Tint, glow and zoom fade back to the original image. */
  settle: number
  /** Idle time between `enter()` and `leave()` when using `play()`. */
  idle: number
  /** Cells dissolving away. */
  dissolve: number
  /** Overlay background fade-out after the dissolve. */
  fade: number
}

export type PixelIntroOptions = {
  /** Image URL or an already created <img>. */
  src: string | HTMLImageElement
  /** Where the full-screen overlay is attached. Default: document.body. */
  container?: HTMLElement
  /** Overlay background. Default: '#000'. */
  background?: string
  /** Size of the whole effect (image at peak zoom + glow) as a fraction of the container (0..1). Default: 1. */
  size?: number
  /** Number of grid cells along the longer image side. Default: 60. */
  cells?: number
  /** How much the image brightens toward lighter versions of its own colours (0..1). Default: 0.3. */
  tintStrength?: number
  /** Halo radius as a fraction of the drawn image height. Default: 0.2. */
  glowSize?: number
  /** Halo intensity (0..2). Default: 1. */
  glowStrength?: number
  /** Extra scale at the peak of the reveal (0.08 = +8%). Default: 0.08. */
  zoom?: number
  /** Timings in milliseconds. */
  timing?: Partial<PixelIntroTiming>
  /** Overlay z-index. Default: 2147483647. */
  zIndex?: number
  /** Replace the effect with a plain fade when the user prefers reduced motion. Default: true. */
  respectReducedMotion?: boolean
  /** Seed for the random cell order (same seed → same pattern). */
  seed?: number
}

export type PixelIntro = ReturnType<typeof createPixelIntro>

export const defaultTiming:PixelIntroTiming = {
  delay: 300,
  reveal: 1500,
  hold: 100,
  settle: 350,
  idle: 500,
  dissolve: 400,
  fade: 300,
}

type Frame = {
  /** 0..1 – cells with revealThreshold < reveal are shown. */
  reveal: number
  /** 0..1 – cells with dissolveThreshold < dissolve are hidden. */
  dissolve: number
  /** 0..1 – brightening amount. */
  bright: number
  /** 0..1 – halo amount. */
  glow: number
  /** Image scale, 1 = rest size. */
  scale: number
}

/** [time in ms, value] */
type Keyframe = [ms:number, value:number]

type Bloom = { canvas: HTMLCanvasElement, ctx: CanvasRenderingContext2D, radius: number, alpha: number, downscale: number, margin: number }

function easeOut( t:number, power = 2.5 ) {
  return 1 - Math.pow( 1 - t, power )
}

function easeIn( t:number, power = 2 ) {
  return Math.pow( t, power )
}

function easeInOut( t:number ) {
  return t < 0.5 ? 2 * t * t : 1 - Math.pow( -2 * t + 2, 2 ) / 2
}

function clamp01( value:number ) {
  return Math.min( 1, Math.max( 0, value ) )
}

/** 0..1 progress of `ms` through a segment starting at `start`; zero-length segments jump straight to 1. */
function progress( ms:number, start:number, duration:number ) {
  return duration > 0 ? clamp01( (ms - start) / duration ) : Number( ms >= start )
}

/** Linear interpolation over keyframes sorted by time; holds the first/last value outside the range. */
function interpolate( keys:Keyframe[], ms:number ) {
  const next = keys.findIndex( ([ time ]) => time > ms )
  if (next === -1) return keys[ keys.length - 1 ][ 1 ]
  if (next === 0) return keys[ 0 ][ 1 ]

  const [ startTime, startValue ] = keys[ next - 1 ]
  const [ endTime, endValue ] = keys[ next ]

  return startValue + (endValue - startValue) * (ms - startTime) / (endTime - startTime)
}

function mulberry32( seed:number ) {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0
    let hash = Math.imul( seed ^ (seed >>> 15), 1 | seed )
    hash = (hash + Math.imul( hash ^ (hash >>> 7), 61 | hash )) ^ hash

    return ((hash ^ (hash >>> 14)) >>> 0) / 4294967296
  }
}

function loadImage( src:string | HTMLImageElement ) {
  const img = typeof src === `string` ? new Image() : src
  if (typeof src === `string`) img.src = src
  if (img.complete && img.naturalWidth) return Promise.resolve( img )

  return img.decode().then( () => img )
}

function wait( ms:number ) {
  return new Promise<void>( resolve => setTimeout( resolve, ms ) )
}

function canvas2d( width = 1, height = 1 ) {
  const canvas = document.createElement( `canvas` )
  canvas.width = width
  canvas.height = height

  return { canvas, ctx:canvas.getContext( `2d` )! }
}

export function createPixelIntro( options:PixelIntroOptions ) {
  const opts = {
    container: document.body,
    background: `#f00`,
    size: 1,
    cells: 60,
    tintStrength: 0.7,
    glowSize: 0.2,
    glowStrength: 1,
    zoom: 0.08,
    zIndex: 2147483647,
    respectReducedMotion: true,
    seed: (Math.random() * 2 ** 31) | 0,
    ...options,
  }
  const timing:PixelIntroTiming = { ...defaultTiming, ...options.timing }
  const reducedMotion = opts.respectReducedMotion && window.matchMedia?.( `(prefers-reduced-motion: reduce)` ).matches

  // ---- DOM -----------------------------------------------------------------
  const overlay = document.createElement( `div` )
  overlay.setAttribute( `aria-hidden`, `true` )
  Object.assign( overlay.style, {
    position: opts.container === document.body ? `fixed` : `absolute`,
    inset: `0`,
    background: opts.background,
    zIndex: `${opts.zIndex}`,
    transition: `opacity ${timing.fade}ms ease`,
  } satisfies Partial<CSSStyleDeclaration> )

  const { canvas, ctx } = canvas2d()
  Object.assign( canvas.style, { position:`absolute`, inset:`0`, width:`100%`, height:`100%` } )

  overlay.appendChild( canvas )
  opts.container.appendChild( overlay )

  // Offscreen buffers: `layer` holds the masked + brightened image, `copy` is scratch for self-blending.
  const layer = canvas2d()
  const copy = canvas2d()

  const filterSupported = `filter` in ctx
  const blooms:Bloom[] = [
    { ...canvas2d(), radius:0.2, alpha:0.9, downscale:4, margin:0 },
    { ...canvas2d(), radius:1, alpha:1.1, downscale:4, margin:0 },
  ]

  // ---- State ---------------------------------------------------------------
  // undefined = not started, Promise = loading, null = failed, element = loaded
  let image:HTMLImageElement | Promise<HTMLImageElement> | null | undefined
  let gridWidth = 0
  let gridHeight = 0
  let occupied = new Uint8Array( 0 ) // 1 if the cell contains visible pixels
  let revealThresholds = new Float32Array( 0 ) // per-cell random thresholds
  let dissolveThresholds = new Float32Array( 0 )

  // layout in device pixels
  let pixelRatio = 1
  let centerX = 0
  let centerY = 0
  let drawWidth = 0
  let drawHeight = 0
  let layerX = 0
  let layerY = 0

  let frame:Frame = { reveal:0, dissolve:0, bright:1, glow:0, scale:1 }
  let animationFrame = 0
  let destroyed = false

  /** Build the grid and find which cells contain non-transparent pixels. */
  const analyse = (img:HTMLImageElement) => {
    const imageWidth = img.naturalWidth
    const imageHeight = img.naturalHeight
    const cellSize = Math.max( imageWidth, imageHeight ) / opts.cells

    gridWidth = Math.ceil( imageWidth / cellSize )
    gridHeight = Math.ceil( imageHeight / cellSize )
    occupied = new Uint8Array( gridWidth * gridHeight ).fill( 1 )

    const random = mulberry32( opts.seed )
    revealThresholds = new Float32Array( gridWidth * gridHeight ).map( () => random() )
    dissolveThresholds = new Float32Array( gridWidth * gridHeight ).map( () => random() )

    // Sample at 4×4 per cell to find empty cells.
    const sample = canvas2d( gridWidth * 4, gridHeight * 4 )
    sample.ctx.drawImage( img, 0, 0, (imageWidth / cellSize) * 4, (imageHeight / cellSize) * 4 )

    try {
      const pixels = sample.ctx.getImageData( 0, 0, gridWidth * 4, gridHeight * 4 ).data
      occupied.fill( 0 )

      for (let i = 3;  i < pixels.length;  i += 4) {
        if (pixels[ i ] <= 12) continue

        const pixelIndex = (i - 3) / 4
        const x = pixelIndex % (gridWidth * 4)
        const y = (pixelIndex - x) / (gridWidth * 4)
        occupied[ (y >> 2) * gridWidth + (x >> 2) ] = 1
      }
    } catch {
      // Cross-origin image without CORS: keep every cell.
    }
  }

  const layout = () => {
    if (!(image instanceof HTMLImageElement)) return

    pixelRatio = Math.min( window.devicePixelRatio || 1, 2 )
    const overlayWidth = overlay.clientWidth
    const overlayHeight = overlay.clientHeight

    canvas.width = Math.round( overlayWidth * pixelRatio )
    canvas.height = Math.round( overlayHeight * pixelRatio )

    // Fit the whole effect inside `size` of the container: the image at peak zoom (`peakScale`)
    // plus the widest glow, which reaches 2 × radius beyond the layer on every side.
    const imageWidth = image.naturalWidth
    const imageHeight = image.naturalHeight
    const peakScale = 1 + opts.zoom + 0.02
    const glowExtent = 2 * opts.glowSize * Math.max( ...blooms.map( bloom => bloom.radius ) )
    const fitScale = Math.min(
      (overlayWidth * opts.size) / (imageWidth * peakScale + imageHeight * glowExtent),
      (overlayHeight * opts.size) / (imageHeight * (peakScale + glowExtent)),
    )

    drawWidth = imageWidth * fitScale * pixelRatio
    drawHeight = imageHeight * fitScale * pixelRatio

    centerX = canvas.width / 2
    centerY = canvas.height / 2

    // The layer fits the image at its largest scale; it sits on whole device pixels so cells never leave seams.
    layer.canvas.width = copy.canvas.width = Math.ceil( drawWidth * peakScale )
    layer.canvas.height = copy.canvas.height = Math.ceil( drawHeight * peakScale )
    layerX = Math.round( centerX - layer.canvas.width / 2 )
    layerY = Math.round( centerY - layer.canvas.height / 2 )

    for (const bloom of blooms) {
      const radius = drawHeight * opts.glowSize * bloom.radius

      // Without ctx.filter, blur by down-sampling harder and letting bilinear upscaling soften it.
      bloom.downscale = filterSupported ? 4 : Math.max( 4, Math.round( radius / 3 ) )
      bloom.margin = Math.ceil( radius * 2 )
      bloom.canvas.width = Math.ceil( (layer.canvas.width + bloom.margin * 2) / bloom.downscale )
      bloom.canvas.height = Math.ceil( (layer.canvas.height + bloom.margin * 2) / bloom.downscale )
    }
  }

  /** Draws the visible cells of the (scaled, brightened) image into `layer`. Returns false when nothing is visible. */
  const drawLayer = (img:HTMLImageElement) => {
    const { reveal, dissolve, bright, scale } = frame
    const layerCtx = layer.ctx
    const layerWidth = layer.canvas.width
    const layerHeight = layer.canvas.height

    layerCtx.globalCompositeOperation = `source-over`
    layerCtx.globalAlpha = 1
    layerCtx.clearRect( 0, 0, layerWidth, layerHeight )

    const scaledWidth = drawWidth * scale
    const scaledHeight = drawHeight * scale
    const imageX = centerX - layerX - scaledWidth / 2
    const imageY = centerY - layerY - scaledHeight / 2
    const cellSize = Math.max( scaledWidth, scaledHeight ) / opts.cells

    if (reveal < 1 || dissolve > 0) {
      let anyVisible = false
      layerCtx.beginPath()

      for (let y = 0;  y < gridHeight;  y++) {
        const top = Math.round( imageY + y * cellSize )
        const bottom = Math.round( imageY + (y + 1) * cellSize )

        for (let x = 0;  x < gridWidth;  x++) {
          const cellIndex = y * gridWidth + x
          if (!occupied[ cellIndex ] || revealThresholds[ cellIndex ] >= reveal || dissolveThresholds[ cellIndex ] < dissolve) continue

          const left = Math.round( imageX + x * cellSize )
          layerCtx.rect( left, top, Math.round( imageX + (x + 1) * cellSize ) - left, bottom - top )
          anyVisible = true
        }
      }

      if (!anyVisible) return false

      layerCtx.fillStyle = `#000`
      layerCtx.fill()
      layerCtx.globalCompositeOperation = `source-in`
    }

    layerCtx.imageSmoothingQuality = `high`
    layerCtx.drawImage( img, imageX, imageY, scaledWidth, scaledHeight )

    // Brighten every pixel toward a lighter version of its own colour: screening the image onto itself
    // three times gives up to 1 - (1 - c)^4, which keeps the local hue (green stays green, red stays red).
    const amount = bright * opts.tintStrength
    if (amount <= 0.001) return true

    copy.ctx.clearRect( 0, 0, layerWidth, layerHeight )
    copy.ctx.drawImage( layer.canvas, 0, 0 )

    layerCtx.globalCompositeOperation = `screen`
    layerCtx.globalAlpha = amount

    for (let pass = 0;  pass < 3;  pass++) layerCtx.drawImage( copy.canvas, 0, 0 )

    // Screen thickens semi-transparent edges; restore the original alpha.
    layerCtx.globalCompositeOperation = `destination-in`
    layerCtx.globalAlpha = 1
    layerCtx.drawImage( copy.canvas, 0, 0 )

    return true
  }

  const render = () => {
    if (destroyed || !(image instanceof HTMLImageElement)) return

    ctx.globalCompositeOperation = `source-over`
    ctx.globalAlpha = 1
    ctx.clearRect( 0, 0, canvas.width, canvas.height )

    if (!drawLayer( image )) return

    // Halo: blurred copies of the layer itself, so the glow takes the local colour of the image under it.
    const glowAmount = frame.glow * opts.glowStrength
    if (glowAmount > 0.01) {
      ctx.globalCompositeOperation = `lighter`

      for (const bloom of blooms) {
        const { canvas:bloomCanvas, ctx:bloomCtx, downscale, margin } = bloom

        bloomCtx.clearRect( 0, 0, bloomCanvas.width, bloomCanvas.height )
        if (filterSupported) bloomCtx.filter = `blur(${((drawHeight * opts.glowSize * bloom.radius) / downscale / 2).toFixed( 1 )}px)`
        bloomCtx.drawImage( layer.canvas, margin / downscale, margin / downscale, layer.canvas.width / downscale, layer.canvas.height / downscale )

        ctx.globalAlpha = Math.min( 1, glowAmount * bloom.alpha )
        ctx.drawImage( bloomCanvas, layerX - margin, layerY - margin, bloomCanvas.width * downscale, bloomCanvas.height * downscale )
      }
    }

    ctx.globalCompositeOperation = `source-over`
    ctx.globalAlpha = 1
    ctx.drawImage( layer.canvas, layerX, layerY )
  }

  /** Run `update(t)` with t going 0→1 over `duration` ms. */
  const animate = (duration:number, update:( t:number ) => void) => {
    cancelAnimationFrame( animationFrame )

    return new Promise<void>( resolve => {
      if (destroyed) return resolve()

      const start = performance.now()
      const tick = (now:number) => {
        if (destroyed) return resolve()

        const t = duration > 0 ? clamp01( (now - start) / duration ) : 1

        update( t )
        render()

        if (t < 1) animationFrame = requestAnimationFrame( tick )
        else resolve()
      }

      animationFrame = requestAnimationFrame( tick )
    } )
  }

  const onResize = () => {
    layout()
    render()
  }

  image = loadImage( opts.src )
  const ready = image
    .then( img => {
      image = img
      analyse( img )
      layout()
      render()
    } )
    .catch( () => {
      image = null
    } )

  window.addEventListener( `resize`, onResize )

  const enter = async() => {
    await ready
    if (!image) return

    if (reducedMotion) {
      frame = { reveal:1, dissolve:0, bright:0, glow:0, scale:1 }

      canvas.style.opacity = `0`
      canvas.style.transition = `opacity 400ms ease`

      render()
      canvas.getBoundingClientRect()
      canvas.style.opacity = `1`

      return wait( 400 )
    }

    const { reveal, hold, settle } = timing
    const settleStart = reveal + hold
    const total = settleStart + settle

    // Zoom track for the whole enter: [ms from reveal start, fraction of `zoom`], linear between keys.
    const zoomKeys:Keyframe[] = [
      [ 0, 0 ],
      [ reveal * 0.6, 1 ],
      [ settleStart, 0.3 ],
      [ total, 0 ],
    ]

    frame = { reveal:0, dissolve:0, bright:1, glow:0, scale:1 }
    render()

    await wait( timing.delay )

    // One continuous animation, so zoom never jumps between phases.
    await animate( total, t => {
      const ms = t * total
      const revealProgress = easeOut( progress( ms, 0, reveal ) )
      const brightness = 1 - easeInOut( progress( ms, settleStart, settle ) )

      frame = {
        reveal: revealProgress,
        dissolve: 0,
        bright: brightness,
        glow: revealProgress * brightness,
        scale: 1 + opts.zoom * interpolate( zoomKeys, ms ),
      }
    } )
  }

  const leave = async() => {
    await ready

    if (image && !reducedMotion) {
      await animate( timing.dissolve, t => {
        // flare up and swell while holes start appearing, then fall apart faster and faster
        const flare = easeOut( clamp01( t / 0.35 ), 2 )
        const dissolve = easeIn( t, 1.8 )

        frame = { reveal:1, dissolve, bright:flare, glow:flare * (1 - dissolve), scale:1 + opts.zoom * 0.5 * Math.sin( Math.PI * t ) }
      } )
    }

    overlay.style.opacity = `0`
    await wait( timing.fade )
    destroy()
  }

  const play = async() => {
    await enter()
    await wait( timing.idle )
    await leave()
  }

  const destroy = () => {
    if (destroyed) return

    destroyed = true
    cancelAnimationFrame( animationFrame )
    window.removeEventListener( `resize`, onResize )
    overlay.remove()
  }

  return {
    /** The overlay element (already in the DOM). */
    element: overlay,
    /** Resolves once the image is loaded (or failed to load). */
    ready,
    /** delay → reveal → hold → settle. Resolves when the image sits still. */
    enter,
    /** dissolve → overlay fade → destroy. */
    leave,
    /** enter → idle → leave. */
    play,
    /** Remove everything immediately. */
    destroy,
  }
}

/** One-shot helper: show the intro, then remove it. */
export function playPixelIntro( options:PixelIntroOptions ) {
  return createPixelIntro( options ).play()
}
