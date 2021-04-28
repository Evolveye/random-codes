import ProjectBase from "https://evolveye.github.io/projectBase.js"
import { Point, Rect, random } from "../utils.js"

import Gif from "./classes.js"

ProjectBase.projectClass = class Project extends ProjectBase {
  constructor() {
    super()

    const gif = new Gif( { w:`FF FF FF`, r:`FF 00 00`, b:`00 00 FF`, k:`00 00 00` }, [
      [
        [ `r`,`r`,`r`,`r`,`r`,`b`,`b`,`b`,`b`,`b` ],
        [ `r`,`r`,`r`,`r`,`r`,`b`,`b`,`b`,`b`,`b` ],
        [ `r`,`r`,`r`,`r`,`r`,`b`,`b`,`b`,`b`,`b` ],
        [ `r`,`r`,`r`,`w`,`w`,`w`,`w`,`b`,`b`,`b` ],
        [ `r`,`r`,`r`,`w`,`w`,`w`,`w`,`b`,`b`,`b` ],
        [ `b`,`b`,`b`,`w`,`w`,`w`,`w`,`r`,`r`,`r` ],
        [ `b`,`b`,`b`,`w`,`w`,`w`,`w`,`r`,`r`,`r` ],
        [ `b`,`b`,`b`,`b`,`b`,`r`,`r`,`r`,`r`,`r` ],
        [ `b`,`b`,`b`,`b`,`b`,`r`,`r`,`r`,`r`,`r` ],
        [ `b`,`b`,`b`,`b`,`b`,`r`,`r`,`r`,`r`,`r` ],
      ], [
        [ `r`,`r`,`r`,`r`,`r`,`b`,`b`,`b`,`b`,`b` ],
        [ `r`,`r`,`r`,`r`,`r`,`b`,`b`,`b`,`b`,`b` ],
        [ `r`,`r`,`r`,`r`,`r`,`b`,`b`,`b`,`b`,`b` ],
        [ `r`,`r`,`r`,`k`,`k`,`k`,`k`,`b`,`b`,`b` ],
        [ `r`,`r`,`r`,`k`,`k`,`k`,`k`,`b`,`b`,`b` ],
        [ `b`,`b`,`b`,`k`,`k`,`k`,`k`,`r`,`r`,`r` ],
        [ `b`,`b`,`b`,`k`,`k`,`k`,`k`,`r`,`r`,`r` ],
        [ `b`,`b`,`b`,`b`,`b`,`r`,`r`,`r`,`r`,`r` ],
        [ `b`,`b`,`b`,`b`,`b`,`r`,`r`,`r`,`r`,`r` ],
        [ `b`,`b`,`b`,`b`,`b`,`r`,`r`,`r`,`r`,`r` ],
      ]
    ] )

    const div = document.createElement( `div` )
    const p = document.createElement( `p` )
    const img = gif.getImgTag( 100, 100 )

    p.style = `
      position: absolute;
      left: calc( 50% - 100px );
      top: 50%;
      transform: translateY( -50% );
      font-size: 10px;
      font-family: monospace;
    `
    p.innerHTML += `
      const gif = new Gif( { w:"FF FF FF", r:"FF 00 00", b:"00 00 FF", k:"00 00 00" }, [
        [
          [ "r","r","r","r","r","b","b","b","b","b" ],
          [ "r","r","r","r","r","b","b","b","b","b" ],
          [ "r","r","r","r","r","b","b","b","b","b" ],
          [ "r","r","r","w","w","w","w","b","b","b" ],
          [ "r","r","r","w","w","w","w","b","b","b" ],
          [ "b","b","b","w","w","w","w","r","r","r" ],
          [ "b","b","b","w","w","w","w","r","r","r" ],
          [ "b","b","b","b","b","r","r","r","r","r" ],
          [ "b","b","b","b","b","r","r","r","r","r" ],
          [ "b","b","b","b","b","r","r","r","r","r" ],
        ], [
          [ "r","r","r","r","r","b","b","b","b","b" ],
          [ "r","r","r","r","r","b","b","b","b","b" ],
          [ "r","r","r","r","r","b","b","b","b","b" ],
          [ "r","r","r","k","k","k","k","b","b","b" ],
          [ "r","r","r","k","k","k","k","b","b","b" ],
          [ "b","b","b","k","k","k","k","r","r","r" ],
          [ "b","b","b","k","k","k","k","r","r","r" ],
          [ "b","b","b","b","b","r","r","r","r","r" ],
          [ "b","b","b","b","b","r","r","r","r","r" ],
          [ "b","b","b","b","b","r","r","r","r","r" ],
        ]
      ]
    `.replace( /\n/g, `<br>` ).replace( / /g, `&nbsp;` )

    img.style = `
      position: absolute;
      left: calc( 50% - 200px );
      top: 50%;
      image-rendering: pixelated;
      transform: translateY( -50% );
      font-size: 10px;
    `

    div.appendChild( p )
    div.appendChild( img )

    this.wrapper.appendChild( div )

    // * Node.js code
    // fs.writeFileSync( `test.gif`, Buffer.from( gif.bufferData, `hex` ) )
    // console.log( new Png( fs.readFileSync( `test.png` ) ).data )
  }
}