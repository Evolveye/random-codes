let interval = 0

function main() {
  interval = setInterval( () => console.log( 1 ), 1000 )
}

function clear() {
  clearInterval( interval )
}