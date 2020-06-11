import ProjectBase from "https://evolveye.github.io/projectBase.js"
import { Point, Rect } from "../utils.js"

import Quadtree from "./classes.js"

class Project extends ProjectBase {
  mount() {
    this.createRenderingContext()

    this.qTreeSize = 500
    this.objects = []

    /** @type {Quadtree} */
    this.qTree = null

    const { ctx, qTreeSize, qTree } = this
    let resolution = 4
    let mouseDown = false
    let meshShowing = true
    let rectSideLength = resolution
    let drawAreaX = (ctx.canvas.width - qTreeSize) / 2
    let drawAreaY = (ctx.canvas.height - qTreeSize) / 2

    this.createQTree( resolution )
    this.clear()

    qTree.show( ctx, { meshShowing, drawAreaX, drawAreaY } )

    this.createInput( `button`, `Clear`, { onclick() {
      qTree.clear()
      this.clear()
    } } )
    this.createInput( `number`, `Resolution`, { value:resolution, min:1, max:20, onchange( input ) {
      this.createQTree( input.value )
      this.clear()
    } } )
    this.createInput( `checkbox`, `Show mesh`, { checked:meshShowing, onchange( input ) {
      const drawAreaX = (ctx.canvas.width - qTreeSize) / 2
      const drawAreaY = (ctx.canvas.height - qTreeSize) / 2

      meshShowing = input.checked

      this.clear()

      qTree.show( ctx, { meshShowing, drawAreaX, drawAreaY } )
    } } )
    //addDescription( `Quadtree for figures/objects. Draw line on canvas` )

    this.setEventListener( this.wrapper, `mouseup`, (up, down) => {
      const drawAreaX = (ctx.canvas.width - qTreeSize) / 2
      const drawAreaY = (ctx.canvas.height - qTreeSize) / 2
      const pointUp = new Point( up.x - drawAreaX, up.y - drawAreaY )
      const pointDown = new Point( down.x - drawAreaX, down.y - drawAreaY )

      if (!qTree.boundary.contains( pointUp )) return

      if (pointUp.equal( pointDown )) {
        const obj = { type:'point', ...pointUp }

        this.objects.push( obj )

        qTree.insert( obj, pointUp )
      }
      else {
        const obj = {
          type: 'line',
          startPoint: new Point( pointDown.x, pointDown.y ),
          endPoint: new Point( pointUp.x, pointUp.y )
        }

        this.objects.push( obj )

        qTree.insertPointSequence( obj, pointDown, pointUp )
      }

      this.clear()

      qTree.show( ctx, { meshShowing, drawAreaX, drawAreaY } )
    } )
    this.setEventListener( this.wrapper, `mousedown`, (pressed, x, y, down) => {
      const drawAreaX = (ctx.canvas.width - qTreeSize) / 2
      const drawAreaY = (ctx.canvas.height - qTreeSize) / 2
      const pointDown = new Point( down.x - drawAreaX, down.y - drawAreaY )
      const pointCurrent = new Point( x - drawAreaX, y - drawAreaY )

      this.clear()

      qTree.show( ctx, { meshShowing, drawAreaX, drawAreaY } )

      if (!pressed || !qTree.boundary.contains( pointCurrent )) return

      ctx.strokeStyle = '#b00'
      ctx.beginPath()
      ctx.moveTo( pointDown.x + drawAreaX, pointDown.y + drawAreaY )
      ctx.lineTo( x, y )
      ctx.stroke()
    } )
  }


  /* *
   * Project methods */


  createQTree( resolution=5 ) {
    this.qTree = new Quadtree( new Rect( 0, 0, this.qTreeSize, this.qTreeSize ), resolution )
  }
  clear() {
    const { ctx, qTreeSize } = this
    const drawAreaX = (ctx.canvas.width - qTreeSize) / 2
    const drawAreaY = (ctx.canvas.height - qTreeSize) / 2

    clearSubcanvas()

    ctx.fillStyle = '#222'
    ctx.fillRect( drawAreaX, drawAreaY, qTreeSize, qTreeSize )
  }
}

ProjectBase.run( new Project() )