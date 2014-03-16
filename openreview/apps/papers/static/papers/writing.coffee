TIMEOUT_AFTER = 750

last_keypress = null
timeout = null

stopped_typing = (form) ->
  form = $(this.currentTarget).closest("form") if not form?

  # Get form data as javascript object
  form_data = {}
  form.serializeArray().map((x) ->
    form_data[x.name] = x.value
  );

  $.post(form.attr("action"), form_data, review_received.bind(form))

review_received = (html) ->
  preview = this.closest(".new").find(".preview")
  preview.html(html)
  preview.find(".voting").hide()
  preview.find(".options").hide()
  MathJax.Hub.Queue(["Typeset", MathJax.Hub, preview.get(0)]);

keyup = (e) ->
  last_keypress = Date.now() if not last_keypress?
  delta = Date.now() - last_keypress

  if delta > TIMEOUT_AFTER
    last_keypress = null
  else
    clearTimeout(timeout);
    timeout = setTimeout(stopped_typing.bind(e), TIMEOUT_AFTER);

init_writing = (container) ->
  container.find("textarea").keyup(keyup)
  stopped_typing container.find("form")
  container.prop("initialised", true);

icon_clicked = (hide, toggle) ->
  return ->
    container = $(this).closest(".review-container");
    container.find("> .#{hide}").hide()
    container.find("> .#{toggle}").toggle()

    container = container.find("> .#{toggle}")
    if not container.prop("initialised")
      init_writing(container)

$(".review .options .edit").click(icon_clicked("new", "edit"))
$(".review .options .reply").click(icon_clicked("edit", "new"))

