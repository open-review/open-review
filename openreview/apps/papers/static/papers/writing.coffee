TIMEOUT_AFTER = 750

last_keypress = null
timeout = null

stopped_typing = ->
  form = $(this.currentTarget).closest("form")
  url = form.attr("action") + "?commit=false"

  # Get form data as javascript object
  form_data = {}
  form.serializeArray().map((x) ->
    form_data[x.name] = x.value
  );

  $.post(url, form_data, review_received.bind(form))

review_received = (html) ->
  preview = this.closest(".new").find(".preview")
  preview.html(html)
  preview.find(".voting").hide()
  preview.find(".options").hide()

$(".new textarea").keyup((e) ->
  last_keypress = Date.now() if not last_keypress?
  delta = Date.now() - last_keypress

  if delta > TIMEOUT_AFTER
    last_keypress = null
  else
    clearTimeout(timeout);
    timeout = setTimeout(stopped_typing.bind(e), TIMEOUT_AFTER);
)