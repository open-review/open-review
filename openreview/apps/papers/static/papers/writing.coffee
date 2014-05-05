TIMEOUT_AFTER = 750
PREVIEW_PROCEDURE_API_URL = "/api/v1/procedures/preview"

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

  form_data.paper = $(".paper").data("paper-id")

  if (form_data.rating == "")
    form_data.rating = 1


  $.ajax({
    type: "POST",
    url: PREVIEW_PROCEDURE_API_URL,
    data: form_data,
    success: review_received.bind(form),
    error: error_received.bind(form)
  })

  last_keypress = null

error_received = (jqXHR, textStatus) ->
  preview = this.closest(".compose-review")
  error_class = if jqXHR.status == 403 then "permission-denied" else "uknown"
  error = preview.find(".preview-error.#{error_class}")
  error.find(".status-code").text(jqXHR.status)
  error.find(".status-text").text(jqXHR.statusText)
  error.show()
  preview.find("[type=submit]").attr("disabled", "disabled")

review_received = (html) ->
  preview = $("#"+$(this).closest(".compose-review").data("preview-id"));
  preview.html(html)
  preview.find(".voting").hide()
  preview.find(".options").hide()
  preview.find(".comments").hide()
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
  form = $(container).find("form")
  $(container).find("textarea").keyup(keyup)
  $(container).prop("initialised", true);

  stopped_typing form
  form.find("select,input").change(-> stopped_typing form)


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

$("main > .compose-review.box textarea").focus(->
  init_writing($(this).closest(".compose-review"))
)

# Show the edit form of reviews that were being edited but contain errors
$(".edit .errorlist").parents(".edit").show()
