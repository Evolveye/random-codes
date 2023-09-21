"use strict"


Paf.modules.anchors = {constructor : class RAnchor {
  /** Constructor of editor DOM
   * @param {HTMLElement} initializer Initializer of R tag
   */
    constructor(initializer) {
      if(!initializer.dataset.scope) {
        initializer.innerHTML = '<strong>Attribute data-scope must defined!</strong>'
        return
      }

      //* General CSS
        if(!document.querySelector('style.RAnchors_generalCSS')) {
          let generalCSS = document.createElement('style')
              generalCSS.className = 'RAnchors_generalCSS'
              generalCSS.textContent = `
                .RAnchors {
                  width: max-content;
                  border: 1px solid #D0D0D0;
                  padding: 10px;
                  padding-right: 100px;
                }
                    .RAnchors ul {
                      margin-left: 10px;
                    }
                    .RAnchors a {
                      color: #67F;
                    }
                        .RAnchors a:hover {
                          border-bottom: 2px dashed;
                        }
                
              `
          document.head.appendChild(generalCSS)
        }
      //*

      this.ele           = document.createElement('nav')
      this.ele.id        = initializer.id
      this.ele.className = `RTag RAnchors ${initializer.className}`
      this.initialHTML   = initializer.innerHTML
      this.scope         = initializer.dataset.scope ? document.body.querySelector(initializer.dataset.scope) : document.body
      this.topMargin     = initializer.dataset.topMargin
      this.anchors       = []
      this.build()

      initializer.parentElement.replaceChild(this.ele,initializer)
      window.addEventListener('load', e => { window.scrollBy(0,-this.topMargin) })
    }

  /** Build table of content
   */
    build() {
      let ele
      let tableOfContent = this.initialHTML ? `<ul><li class="before">${this.initialHTML}</li>` : '<ul>'
      let lastHTree = []
      let nodeIterator = document.createNodeIterator(this.scope ,NodeFilter.SHOW_ELEMENT 
        ,ele => /h[1-6]/i.test(ele.nodeName) ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT
      )

      while (ele = nodeIterator.nextNode()) {
        let lastItem = lastHTree[lastHTree.length - 1]
        let HNum     = ele.nodeName.slice(-1)
        let anchor   = `anchor-${this.anchors.length}-${ele.textContent.replace(/[ #]/g, '_')}`
        let link     = `<a onclick="R.tags.anchors.$constructor.toAnchor('#${anchor}',${this.topMargin})">${ele.textContent}</a>`

        ele.id = anchor
        this.anchors.push(ele)

        if(!lastItem) {
          tableOfContent += `<li>${link}`
          lastHTree.push(HNum)

        } else if(lastItem < HNum) {
          for(let n=lastItem; n<HNum; n++)
            tableOfContent += '<ul><li>'
          tableOfContent += `${link}`
          lastHTree.push(HNum)

        } else if(lastItem == HNum) {
          tableOfContent += `</li><li>${link}`

        } else {
          for(let n=lastItem; n>HNum; n--)
            tableOfContent += '</li></ul></li>'
          tableOfContent += `<li>${link}`
          lastHTree.pop()

        }
      }
      tableOfContent += '</li></ul>'

      this.ele.innerHTML = tableOfContent
    }

  /** Reload
   */
    static reload() {
      let anchors = R.tags.anchors
      let count   = Object.keys(anchors).length

      for(let i=1; i<count; i++)
        anchors[i].build()
    }

  /** When scroll to anchor
   * @param {String} anchorId Id of anchor
   */
    static toAnchor(anchorId, topMargin) {
      let anchor = document.querySelector(anchorId)

      if(!anchor) return

      window.location.hash = anchorId
      let top = anchor.offsetTop

      while(anchor.offsetParent != document.documentElement && anchor.offsetParent != document.body) {
        anchor = anchor.offsetParent
        top += anchor.offsetTop
      }

      window.scrollTo(0,top - topMargin)
    }
}}