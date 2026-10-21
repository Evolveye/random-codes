import { createPixelIntro, playPixelIntro, type PixelIntroOptions } from "./pixel-intro"

const base:PixelIntroOptions = {
  src: `/cactus.png`,
  background: `black`,
}

const video = document.querySelector<HTMLVideoElement>( `#video` )!
const stage = document.querySelector<HTMLDivElement>( `#stage` )!

document.querySelector( `#compare` )!.addEventListener( `click`, async() => {
  stage.replaceChildren()

  const intro = createPixelIntro({ ...base, container:stage, timing:{ delay:800 } })
  await intro.ready

  video.currentTime = 0
  video.play()
  await intro.play()
} )

document.querySelector( `#fullscreen` )!.addEventListener( `click`, () => {
  playPixelIntro( base )
} )
