import ProjectBase from "https://evolveye.github.io/projectBase.js"
import helper from "./helper.js"

class Project extends ProjectBase {
  constructor() {
    super()

    console.log( this, helper )
  }
}

new Project()