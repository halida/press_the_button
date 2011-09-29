window.init_index = ()->
  window.ws = new WebSocket "ws://localhost:9999/button"

  ws.onmessage = (e)->
    $('#the-number').html(e.data)

  ws.onclose = ()->
    window.setTimeout(init_index, 1000)


window.press_the_button = (i)-> ws.send(i)


