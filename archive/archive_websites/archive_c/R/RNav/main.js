"use strict"

Paf.modules.nav = {constructor : class PafNav {
  /** Paf nav constructor
   * @param  {HTMLElement}  [initializer]  Element being the initializer
   */
  constructor(initializer) {
    let me = this.ele  =  document.createElement('nav')
        me.innerHTML   =  initializer.innerHTML
        me.className   =  `M-PafNav ${initializer.className}`

    this.scopeHeaders  =  me.querySelectorAll('.M-PafNav > span')
    this.scopeStates   =  []
    //: Scopes
      let scopeHeaders = this.scopeHeaders
      for(let scHead of scopeHeaders) {
        if(/[ou]l/i.test(scHead.nextElementSibling.nodeName)) {
          //: Scope header classes
            let scopeClass = `M-PafNav_scope ${scHead.dataset.scopeclass}`
            scHead.removeAttribute('data-scopeClass')
            scHead.classList.add('M-PafNav_scopeHeader')

          //: Scope state input
            let state = document.createElement('input')
                state.type = 'checkbox'
                state.hidden = true

            let scopeStates = this.scopeStates
            scopeStates.push(state)

            let newScHead = scHead.cloneNode(true)
                newScHead.onclick = e => {
                  for(let scHead of scopeStates)
                    if(scHead != state)
                      state.checked = false

                  if(state.checked) {
                    state.checked = false
                    document.body.style.overflow = 'unset'
                  } else {
                    state.checked = true
                    document.body.style.overflow = 'hidden'
                  }
                }

          //: Scope wrapper
            let scope = document.createElement('div')
                scope.className = scopeClass
                scope.appendChild(state)
                scope.appendChild(newScHead)
                scope.appendChild(scHead.nextElementSibling.cloneNode(true))

          //:

          scHead.nextElementSibling.remove()
          me.replaceChild(scope,scHead)
        } else {
          scHead.remove()
        }
      }
    //:

    this.activeLists = me.querySelectorAll('.M-PafNav > ol, .M-PafNav_scope > ol')
    this.staticLists = me.querySelectorAll('.M-PafNav > ul, .M-PafNav_scope > ul')
    this.timerFunc   =  null
    //: Menus layers
      let lists = [...this.staticLists, ...this.activeLists]
      let listsIterator = (list,layer=1) => {
        let subLists = list.querySelectorAll(`.is-layer_${layer} > li > ul, .is-layer_${layer} > li > ol`)
        layer++

        for(let subList of subLists) {
          subList.classList.add(`is-layer_${layer}`,'is-sublist')
          subList.parentElement.classList.add('is-listParent')

          listsIterator(subList, layer)
        }
      }

      for(let list of lists) {
        if(list.nodeName == 'OL')
             list.classList.add(`M-PafNav_dynList`)
        else list.classList.add(`M-PafNav_stList`)

        list.classList.add(`is-layer_1`)

        listsIterator(list)
      }

    //: Active menus interactions
      lists = this.activeLists
      for(let list of lists) {
        let items      =  list.children

        for(let item of items) {
          let onclick    =  'click' in item.dataset
          let onhover    =  'hover' in item.dataset
          let hovertime  =  item.dataset.hover || 150

          if(onhover) {
            if(!this.timerFunc)
              list.addEventListener('mouseout', e => {
                clearTimeout(this.timerFunc)
              })
    
            if(item.classList.contains('is-listParent'))
              item.addEventListener('mousemove', e => {
                clearTimeout(this.timerFunc)
                this.timerFunc = setTimeout(() => {
                  for(let item of items)
                    item.classList.remove('is-active')
      
                  item.classList.add('is-active')
                }, hovertime)
              })
          }

          if(onclick) {
            if(item.classList.contains('is-listParent'))
              item.addEventListener('click', e => {
                for(let item of items)
                  item.classList.remove('is-active')
  
                item.classList.add('is-active')
              })
          }
        }

        if(!list.querySelector('li.is-active'))
          items[0].classList.add('is-active')
      }

    //: Nav items
      let navItems = me.querySelectorAll('.M-PafNav > a, .M-PafNav_stList > a')
      for(let navItem of navItems)
        navItem.classList.add('M-PafNav_item')

      let navDynListTitles = me.querySelectorAll('.M-PafNav_dynList > li > span, .M-PafNav_dynList > li > a')
      for(let navItem of navDynListTitles)
        navItem.classList.add('M-PafNav_dynTitle')

      let navDynListItems = me.querySelectorAll('.M-PafNav_dynList .is-layer_2 a')
      for(let navItem of navDynListItems)
        navItem.classList.add('M-PafNav_dynItem')
    
    //:

    //: FA icons
      let fa = me.querySelectorAll('[data-fa]')
      for(let item of fa) {
        if(item.textContent) {
          item.classList.add(`icon`)
          item.innerHTML = `
            <span class="icon_ico fa fa-${item.dataset.fa}"></span>
            <span class="icon_label">${item.textContent}</span>
          `
        } else {
          item.classList.add(`fa`)
          item.classList.add(`fa-${item.dataset.fa}`)
        }
        delete item.dataset.fa
      }
    //:

    initializer.parentElement.replaceChild(this.ele,initializer)

    //:
    //: Default styles
      if(!document.head.querySelector('.M-PafNav_defaultStyles')) {
        let styles = document.createElement('style')
            styles.className = 'M-PafNav_defaultStyles'
            styles.textContent = `
              /* */
              /*: Module base :*/

                  .M-PafNav {
                    position: relative;
                    display: flex;
                    height: 50px;
                    font-size: 14px;
                    --separatorColor: #D0D0D0;
                  }
                    .M-PafNav ul,
                    .M-PafNav ol {
                      display: flex;
                      margin: 0;
                      padding: 0;
                      overflow: hidden;
                    }
                    .M-PafNav li {
                      list-style: none;
                    }
                    .M-PafNav * {
                      box-sizing: border-box;
                      text-decoration: none;
                      color: inherit;
                    }

              /* */
              /*: Module scopes :*/

                  .M-PafNav_dynTitle,
                  .M-PafNav_dynItem,
                  .M-PafNav_item {
                    display: block;
                    min-width: 60px;
                    padding: 0 7px;
                    margin: 0 3px;
                    text-align: center;
                    cursor: pointer;
                  }
                  .M-PafNav_dynItem {
                    padding-top: 10px;
                  }
                  .M-PafNav_item {
                    height: 100%;
                    padding-top: 17px;
                  }

                  .M-PafNav_scopeHeader {
                    display: none;
                    height: 100%;
                    position: relative;
                    text-align: center;
                    padding-top: 16px;
                    cursor: pointer;
                  }
                    .M-PafNav_scopeHeader.icon {
                      padding-top: 14px;
                    }
                    .M-PafNav_scopeHeader .icon_ico {
                      display: block;
                    }
                    .M-PafNav_scopeHeader .icon_label {
                      font-size: 50%;
                      display: block;
                    }

                  .M-PafNav_dynList {
                    min-height: 100%;
                    position: relative;
                  }

                  .M-PafNav_scope {
                    overflow: hidden;
                  }

              /* */
              /*: Module states :*/

                  .M-PafNav_item.is-image {
                    padding: 7px;
                    min-width: unset;
                  }
                    .M-PafNav_item.is-image img {
                      height: 100%;
                    }

                  .M-PafNav_dynList li.is-active .is-layer_2 {
                    display: flex;
                  }

                  .M-PafNav li.is-active .M-PafNav_dynTitle  {
                    font-weight: bold;
                  }

                  .M-PafNav_dynList .is-layer_2 {
                    display: none;
                    position: absolute;
                    left: 0;
                    right: 0;
                    top: 34%;
                    width: max-content;
                    height: 66%;
                    overflow: hidden;
                    z-index: 1;
                  }

                    @media screen and (max-width: 425px) {
                      /* */
                      /*: Module base :*/

                          .M-PafNav * {
                            user-select: none;
                          }
                          .M-PafNav > * {
                            flex: 1;
                          }
                          .M-PafNav > *::before {
                            display: none;
                          }

                      /* */
                      /*: Module scopes :*/

                          .M-PafNav_scopeHeader {
                            display: block;
                          }
                          .M-PafNav_scope {
                            position: static;
                          }
                          .M-PafNav_item {
                            padding-top: 16px;
                          }
                      
                      /* */
                      /*: Module states :*/

                          .M-PafNav .is-layer_1 {
                            display: none;
                            position: absolute;
                            left: 0;
                            right: 0;
                            top: 100%;
                            max-height: var(--M-PafNav_mobileSubHeight);
                            background-color: #EEE;
                          }
                          .M-PafNav .is-layer_1 > li,
                          .M-PafNav .is-layer_2 {
                            height: unset;
                          }
                          .M-PafNav_dynList li,
                          .M-PafNav_stList li {
                            margin: 3px;
                          }
                          .M-PafNav_dynList li.is-active .is-layer_2,
                          .M-PafNav_stList li.is-active .is-layer_2 {
                            display: block;
                            position: static;
                            width: unset;
                          }

                          .M-PafNav_scope input:checked ~ .M-PafNav_dynList {
                            display: block;
                            overflow: auto;
                          }
                    }
            `

        Paf.library.headDataSection.nextElementSibling.insertAdjacentElement('beforebegin',styles)
      }

    //: RWD mobile sublist height
      document.documentElement.style.setProperty(
        '--M-PafNav_mobileSubHeight',
        `calc(100vh - 100% - ${me.offsetTop}px - 5px)`
      )

    //:
  }


  /** Set active
   * @param {Number} leyer Layer of item to set active
   * @param {String|Number} data Number of item or its text content
   */
    static set_active(leyer, data) {return
      let scopes = Paf.modules.nav.ele.querySelectorAll(`.layer-${layer}`)

      if(typeof data == 'string')
        for(let scope of scopes) {
          let items = scope.children

          for(let item of items)
            if(item.textContent == data)
              console.log(item)
        }

      else if(typeof data == 'number')
        for(let scope of scopes)
          if(scope.children.length >= data)
            console.log(scope.children[data])

    }
}}
