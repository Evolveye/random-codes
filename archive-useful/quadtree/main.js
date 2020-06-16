import ProjectBase from "https://evolveye.github.io/projectBase.js"
import { Point, Rect, random } from "../utils.js"

import Quadtree from "./classes.js"

ProjectBase.projectClass = class Project extends ProjectBase {
  constructor() {
    super()

    /** @type {CanvasRenderingContext2D} */
    this.ctx = this.createRenderingContext()

    this.qTreeSize = 500
    this.queryRect = new Rect( 100, 100, 100, 75 )

    this.drawArea = new Rect(
      (this.ctx.canvas.width - this.qTreeSize) / 2,
      (this.ctx.canvas.height - this.qTreeSize) / 2,
      this.qTreeSize,
      this.qTreeSize,
    )

    this.qTree = this.createQTree()
    this.pointsOnlyInLeaves = true

    this.draw()
    this.setUi()
    this.setEvents()
  }

  setUi() {
    this.createInput( `button`, `Clear`, { onclick:() => {
      this.qTree.clear()
      this.clear()
    } } )
    this.createInput( `button`, `Generate 100`, { onclick:() => {
      this.generatePoints( 100 )
      this.draw()
    } } )
    this.createInput( `button`, `Switch "only leaves" mode: ${this.pointsOnlyInLeaves}`, { onclick:({ target:input }) => {
      this.pointsOnlyInLeaves = !this.pointsOnlyInLeaves

      input.value = `Switch "only leaves" mode: ${this.pointsOnlyInLeaves}`

      this.createQTree()
      this.draw()
    } } )
    this.setDescription( `Quadtree for points. Try to click on featured area. "Only leaves" is removing quadtree posibility to store points inside every node` )
  }
  setEvents() {
    const { ctx, qTreeSize, queryRect } = this

    this.setEventListener( this.wrapper, `mouseup`, ({ layerX:x, layerY:y }) => {
      const { qTree } = this

      const testingPoint = new Point(
        x - (ctx.canvas.width - qTreeSize) / 2,
        y - (ctx.canvas.height - qTreeSize) / 2
      )

      if (!qTree.boundary.contains( testingPoint )) return

      qTree.insert( testingPoint )

      this.draw()
    } )

    this.setEventListener( this.wrapper, `mousemove`, ({ layerX:x, layerY:y }) => {
      const testingRect = new Rect(
        x - (ctx.canvas.width - qTreeSize) / 2 - queryRect.width / 2,
        y - (ctx.canvas.height - qTreeSize) / 2 - queryRect.height / 2,
        queryRect.width,
        queryRect.height
      )

      if (!this.qTree.boundary.contains( testingRect )) return

      queryRect.x = testingRect.x
      queryRect.y = testingRect.y

      this.draw()
    } )
  }

  /**
   * @returns {Quadtree}
   */
  createQTree() {
    this.qTree = new Quadtree( new Rect( 0, 0, this.qTreeSize, this.qTreeSize ), this.pointsOnlyInLeaves )

    return this.qTree
  }
  clear() {
    const { drawArea, ctx } = this

    this.clearContext()

    ctx.fillStyle = '#fff2'
    ctx.fillRect( drawArea.x, drawArea.y, drawArea.width, drawArea.height )
  }
  draw() {
    const { drawArea, ctx, queryRect } = this
    const { x, y, width, height } = queryRect

    this.clear()
    this.qTree.show( ctx, drawArea.x, drawArea.y )

    ctx.strokeStyle = '#0f0'
    ctx.strokeRect( drawArea.x + x, drawArea.y + y, width, height )

    ctx.fillStyle = '#0f0'
    this.qTree.query( queryRect ).forEach( ({ x, y }) => {
      ctx.beginPath()
      ctx.arc( drawArea.x + x, drawArea.y + y, 2, 0, Math.PI * 2 )
      ctx.fill()
    } )
  }
  generatePoints( count ) {
    for (let i = 0; i < count; i++) {
      const point = new Point( random( this.qTreeSize ), random( this.qTreeSize ) )

      this.qTree.insert( point )
    }
  }
}