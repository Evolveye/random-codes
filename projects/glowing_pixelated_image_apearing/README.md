# Pixel Intro

Recreates the effect from `cactus-intro-2.mp4`: an image appears on a grid of cells in random order, bright, glowing and slightly enlarged. It then settles into its real colours and size, and dissolves cell by cell. The tint and glow come from the image's own local colours, so each part brightens and blooms in its own hue.

The whole effect is one dependency-free file, [`src/pixel-intro.ts`](src/pixel-intro.ts). It draws on a `<canvas>`; the halo is a blurred copy of the visible image itself. It also handles HiDPI screens, resizing and `prefers-reduced-motion`.

```bash
npm install
npm run dev      # demo: original video next to the re-creation, plus a full-screen intro
```

## API

```ts
import { createPixelIntro, playPixelIntro } from "./pixel-intro"

// one-shot: shows the overlay, plays everything, removes itself
await playPixelIntro( { src: `/cactus.png` } )

// or control it yourself, e.g. keep the logo up until the app has loaded
const intro = createPixelIntro( { src: `/cactus.png` } )
await intro.enter()   // delay → reveal → hold → settle
await intro.leave()   // dissolve → fade overlay → destroy
```

| option | default | |
|---|---|---|
| `src` | — | image URL or `<img>` (transparent PNG/SVG works best) |
| `container` | `document.body` | overlay is `fixed` on body, `absolute` elsewhere |
| `background` | `#000` | overlay colour |
| `size` | `1` | size of the whole effect (image at peak zoom + glow), as a fraction of the container |
| `cells` | `60` | grid cells along the image's longer side |
| `tintStrength` | `0.3` | how far each pixel brightens toward a lighter version of its own colour |
| `glowSize` / `glowStrength` | `0.2` / `1` | halo radius (as a fraction of image height) and intensity |
| `zoom` | `0.08` | extra scale at the peak of the reveal (+8%) |
| `timing` | `{ delay: 300, reveal: 1600, hold: 600, settle: 350, idle: 500, dissolve: 650, fade: 300 }` | ms |
| `seed` | random | same seed gives the same cell pattern |

## Launch intro: mount the app under the overlay, then dissolve

### Vanilla
```ts
const intro = createPixelIntro( { src: `/cactus.png` } )
await Promise.all( [intro.enter(), loadStuff()] )
renderApp( document.getElementById( `app` )! )
await intro.leave()
```

### React (`main.tsx`)
```tsx
const intro = createPixelIntro( { src: `/cactus.png` } )
await intro.enter()
createRoot( document.getElementById( `root` )! ).render( <App /> )
intro.leave()
```

### Svelte 5 (`main.ts`)
```ts
const intro = createPixelIntro( { src: `/cactus.png` } )
await intro.enter()
const app = mount( App, { target: document.getElementById( `app` )! } )
intro.leave()
export default app
```

Starting it from the entry file, before the framework boots, means the intro appears as soon as the JS runs. For it to show even before that, put `<body style="background:#000">` in `index.html` so the page doesn't flash white.
