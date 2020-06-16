import ProjectBase from "https://evolveye.github.io/projectBase.js"
import { Point, Rect } from "../utils.js"

import Quadtree from "./classes.js"

class Project extends ProjectBase {
  mount() {
    /** @type {CanvasRenderingContext2D} */
    this.ctx = this.createRenderingContext()

    this.mouse = { downX:0, downY:0, x:0, y:0, pressed:false }
    this.objects = []
    this.resolution = 10
    this.qTreeSize = 500
    this.drawArea = new Rect(
      (this.ctx.canvas.width - this.qTreeSize) / 2,
      (this.ctx.canvas.height - this.qTreeSize) / 2,
      this.qTreeSize,
      this.qTreeSize,
    )

    this.meshShowing = false

    const { ctx, resolution, drawArea, meshShowing } = this

    /** @type {Quadtree} */
    this.qTree = this.createQTree( resolution )
    this.qTree.show( ctx, { meshShowing, drawArea } )

    this.clear()
    this.setUi()
    this.setEvents()
  }


  /* *
   * Project methods */


  setUi() {
    const { ctx, resolution, drawArea } = this

    this.createInput( `button`, `Clear`, { onclick:() => {
      this.qTree.clear()
      this.clear()
    } } )
    this.createInput( `number`, `Resolution`, { value:resolution, min:1, max:20, onchange:({ target:input }) => {
      this.createQTree( input.value )
      this.clear()
    } } )
    this.createInput( `checkbox`, `Show mesh`, { checked:this.meshShowing, onchange: ({ target:input }) => {
      this.meshShowing = input.checked

      this.clear()
      this.qTree.show( ctx, { meshShowing:this.meshShowing, drawArea } )
    } } )
    this.setDescription( `Quadtree for figures/objects. Try draw a line on featured area.` )
  }
  setEvents() {
    const { ctx, qTreeSize, drawArea } = this

    this.setEventListener( this.wrapper, `mousedown`, ({ layerX, layerY }) => {
      this.mouse.pressed = true
      this.mouse.downX = layerX
      this.mouse.downY = layerY
      this.mouse.x = layerX
      this.mouse.y = layerY

      const { downX:x, downY:y } = this.mouse

      const pointDown = new Point( x - drawArea.x, y - drawArea.y )

      this.clear()
      this.qTree.show( ctx, { meshShowing:this.meshShowing, drawArea } )

      ctx.strokeStyle = '#b00'
      ctx.beginPath()
      ctx.arc( x, y, 3, 0, 2 * Math.PI )
      ctx.stroke()
    } )

    this.setEventListener( this.wrapper, `mouseup`, ({ layerX, layerY }) => {
      this.mouse.x = layerX
      this.mouse.y = layerY

      const { downX, downY, x, y, pressed } = this.mouse

      const pointUp = new Point( x - drawArea.x, y - drawArea.y )
      const pointDown = new Point( downX - drawArea.x, downY - drawArea.y )

      if (!pressed || !this.qTree.boundary.contains( pointUp )) return

      if (pointUp.equal( pointDown )) {
        const obj = { type:'point', ...pointUp }

        this.objects.push( obj )
        this.qTree.insert( obj, pointUp )
      } else {
        const obj = {
          type: 'line',
          startPoint: new Point( pointDown.x, pointDown.y ),
          endPoint: new Point( pointUp.x, pointUp.y )
        }

        this.objects.push( obj )
        this.qTree.insertPointSequence( obj, pointDown, pointUp )
      }

      this.clear()
      this.qTree.show( ctx, { meshShowing:this.meshShowing, drawArea } )

      this.mouse.pressed = false
    } )

    this.setEventListener( this.wrapper, `mousemove`, ({ layerX, layerY }) => {
      this.mouse.x = layerX
      this.mouse.y = layerY

      const { ctx, qTree } = this
      const { downX, downY, x, y, pressed } = this.mouse

      if (pressed) {
        this.clear()

        if (!drawArea.contains( { x, y } )) {
          this.mouse.pressed = false
        } else {
          ctx.strokeStyle = `red`

          ctx.beginPath()
          ctx.moveTo( downX, downY )
          ctx.lineTo( x, y )
          ctx.stroke()
        }

        qTree.show( ctx, { meshShowing:this.meshShowing, drawArea } )
      }
    } )
  }

  createQTree( resolution=5 ) {
    this.qTree = new Quadtree( new Rect( 0, 0, this.qTreeSize, this.qTreeSize ), resolution )

    return this.qTree
  }
  clear() {
    const { ctx, drawArea } = this

    this.clearContext()

    ctx.fillStyle = `#fff2`
    ctx.fillRect( drawArea.x, drawArea.y, drawArea.width, drawArea.height )
  }
}

ProjectBase.run( new Project() )