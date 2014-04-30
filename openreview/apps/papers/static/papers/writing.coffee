TIMEOUT_AFTER = 750

anonymous = $("body").data("anonymous")
last_keypress = null
timeout = null

stopped_typing = (form) ->
  form = $(this.currentTarget).closest("form") if not form?

  # Get form data as javascript object
  form_data = {}
  form.serializeArray().map((x) ->
    form_data[x.name] = x.value
  );

  if form.data("preview")
    url = form.data("preview")
  else
    url = form.attr("action")

  $.ajax({
    type: "POST",
    url: url,
    data: form_data,
    success: review_received.bind(form),
    error: error_received.bind(form)
  })

  last_keypress = null

error_received = (jqXHR, textStatus) ->
  preview = this.closest(".new")
  error_class = if jqXHR.status == 403 then "permission-denied" else "uknown"
  error = preview.find(".preview-error.#{error_class}")
  error.find(".status-code").text(jqXHR.status)
  error.find(".status-text").text(jqXHR.statusText)
  error.show()

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
  $(container).find("textarea").keyup(keyup)
  stopped_typing $(container).find("form")
  $(container).prop("initialised", true);

icon_clicked = (hide, toggle) ->
  if anonymous
    return ->
      $(this).closest(".review").find(".login-message").show()

  return ->
    container = $(this).closest(".review-container");
    container.find("> .#{hide}").hide()
    container.find("> .#{toggle}").toggle()

    container = container.find("> .#{toggle}")
    if not container.prop("initialised")
      init_writing(container)

$(".review .options .edit").click(icon_clicked("new", "edit"))
$(".review .options .reply").click(icon_clicked("edit", "new"))
$(".new-review:visible textarea").focus(->
  init_writing($(this).closest(".review-container"))
)

# Show the edit form of reviews that were being edited but contain errors
$(".edit .errorlist").parents(".edit").show()
