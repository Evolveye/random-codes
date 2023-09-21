"use strict"

/** Class of web code editors */
class RNav {
 /** Constructor
   * @param {String} name Name of textarea - Text
   * @param {{}} [config={}] Object with settings
   */
  constructor(name ,config={}) {
        
    this.scopes = {}
    let RNav = document.createElement('nav')
        RNav.className = 'RNav'

     // inside
        for(let scope of config.scopes) {
          let name = scope.getAttribute('name') || config.scopes.indexOf(scope)
          let title = scope.getAttribute('title') || name

          if(this.scopes[name]) continue

          scope.removeAttribute('name')
          scope.removeAttribute('title')
          scope.dataset.rNavName = `${name}`
          name = name.replace(/\r?\n|\r|\s+/,'_')

          let li = document.createElement('li')
              li.className = `title ${name}`
              li.textContent = title

          scope.insertAdjacentElement('afterbegin',li)
          this.scopes[name] = scope
          RNav.appendChild(scope)
        }
        
    this.ele = RNav

    if(config.initializer) {
      config.initializer.insertAdjacentElement('beforebegin',RNav)
      config.initializer.remove()
      delete config.initializer
    }
  }

 /** New item
   * @param {String} navName RNav name
   * @param {String} scopeName Scope name
   * @param {String} innerHTML HTML to inserted
   */
  static item_insert(navName ,scopeName ,innerHTML) {
    console.log('abc')
    let nav = R.tags.nav[navName]
    if(!nav) return

    let scope = nav.scopes[scopeName]
    if(!scope) return

    let li = document.createElement('li')
        li.className = 'item'
        li.innerHTML = innerHTML

    scope.appendChild(li)
  }
}