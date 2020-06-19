import ProjectBase from "https://evolveye.github.io/projectBase.js"
import { Point } from "../utils.js"

ProjectBase.projectClass = class Project extends ProjectBase {
  constructor() {
    super()

    /** @type {CanvasRenderingContext2D} */
    this.ctx = this.createRenderingContext()

    this.mouse = { downX:0, downY:0, x:0, y:0, pressed:false }

    this.rectSideLength = 3
    this.lines = [ { pointA:new Point( 150, 100 ), pointB:new Point( 400, 200 ) } ]

    this.setUi()
    this.setEvents()
    this.draw()
  }

  setUi() {
    this.createInput( `button`, `Clear`, { onclick:() => {
      this.lines.splice( 0 )
      this.redraw()
    } } )

    this.createInput( `number`, `Resolution`, { min:1, max:20, value:this.rectSideLength, onchange:({ target:input }) => {
      this.rectSideLength = input.value
      this.redraw()
    } } )

    this.setDescription( `Just draw a line on canvas` )
  }
  setEvents() {
    this.setEventListener( this.wrapper, `mousemove`, ({ layerX, layerY }) => {
      this.mouse.x = layerX
      this.mouse.y = layerY

      const { ctx } = this
      const { downX, downY, x, y, pressed } = this.mouse

      this.redraw()

      if (!pressed) return

      ctx.lineWidth = 5
      ctx.strokeStyle = '#b00'
      ctx.beginPath()
      ctx.moveTo( downX, downY )
      ctx.lineTo( x, y )
      ctx.stroke()
    } )

    this.setEventListener( this.wrapper, `mousedown`, ({ layerX, layerY }) => {
      this.mouse.pressed = true
      this.mouse.downX = layerX
      this.mouse.downY = layerY
      this.mouse.x = layerX
      this.mouse.y = layerY
    } )

    this.setEventListener( this.wrapper, `mouseup`, ({ layerX, layerY }) => {
      this.mouse.x = layerX
      this.mouse.y = layerY

      const { downX, downY, x, y } = this.mouse

      this.lines.push( {
        pointA: new Point( downX, downY, true ),
        pointB: new Point( x, y, true )
      } )

      this.redraw()

      this.mouse.pressed = false
    } )
  }

  bresenham( { x:xA, y:yA }, { x:xB, y:yB } ) {
    const { ctx, rectSideLength } = this

    let x1   = floorToDivisible( xA, rectSideLength )
    let y1   = floorToDivisible( yA, rectSideLength )
    const x2 = floorToDivisible( xB, rectSideLength )
    const y2 = floorToDivisible( yB, rectSideLength )

    const deltaX = Math.abs( x1 - x2 )
    const deltaY = Math.abs( y1 - y2 )

    const stepX = (x1 < x2 ? 1 : -1) * rectSideLength
    const stepY = (y1 < y2 ? 1 : -1) * rectSideLength

    let err = deltaX - deltaY

    do  {
      ctx.fillRect( x1, y1, rectSideLength, rectSideLength )

      const doubledErr = err * 2

      if (doubledErr > -deltaY) {
        err -= deltaY
        x1 += stepX
      }
      if (doubledErr < deltaX) {
        err += deltaX
        y1 += stepY
      }
    } while (x1 != x2 || y1 != y2)

    ctx.fillRect( x1, y1, rectSideLength, rectSideLength )
  }

  draw() {
    const { ctx, lines } = this

    for (const { pointA, pointB, color='#0b0' } of lines) {
      ctx.fillStyle = color

      this.bresenham( pointA, pointB )
    }
  }
  redraw() {
    this.clearContext()
    this.draw()
  }

  floorToDivisible( number, divider ) {
    return Math.floor( number / divider ) * divider
  }
}