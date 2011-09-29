window.init_index = ()->
  window.ws = new WebSocket "ws://localhost:9999/button"

  ws.onmessage = (e)->
    $('#the-number').html(e.data)

  ws.onclose = ()->
    alert('connection closed, refresh please..')


window.press_the_button = ()->
  ws.send("*")

