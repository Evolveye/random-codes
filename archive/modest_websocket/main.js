export default class WS extends WebSocket {
  #listeners = new Map()
  #defaultListener = () => {}

  emit( event, data ) {
    const msg = data ? { [event]:data } : event
    const send = () => this.send( JSON.stringify( msg ) )

    if (this.readyState !== 1) {
      this.addEventListener( `open`, send )
    } else {
      send()
    }
  }

  on( event, listener ) {
    this.#listeners.set( event, listener )
  }

  // onmessage = data => console.log( data )
  onmessage = ({ data }) => {
    let jsonData

    try {
      jsonData = JSON.parse( data )
    } catch {
      jsonData = data
    }

    if (typeof jsonData === `object` && `event` in jsonData && `data` in jsonData) {
      const { event, data } = jsonData

      if (this.#listeners.has( event )) this.#listeners.get( event )( data )
      else console.warn( `Unhandled event: ${event}` )
    } else if (typeof jsonData === `string` && this.#listeners.has( jsonData )) {
      this.#listeners.get( jsonData )( jsonData )
    } else this.#defaultListener( jsonData )
  }

  setDefaultListener( listener ) {
    if (typeof listener != `function`) throw new Error( `Listener should be the function type` )

    this.#defaultListener = listener
  }
}