TIMEOUT_AFTER = 750

PREVIEW_PROCEDURE_API_URL = "/api/v1/procedures/preview"
REVIEW_API_URL = "/api/v1/reviews/"

anonymous = $("body").data("anonymous")
last_keypress = null
timeout = null

get_form_data = (form) ->
  form_data = {}
  form.serializeArray().map((x) ->
    form_data[x.name] = x.value
  );

  console.log(form)

  return form_data

stopped_typing = (form) ->
  form = $(this.currentTarget).closest("form") if not form?

  $.ajax({
    type: "POST",
    url: PREVIEW_PROCEDURE_API_URL,
    data: get_form_data(form),
    success: review_received.bind(form),
    error: error_received.bind(form)
  })

  last_keypress = null

error_received = (jqXHR, textStatus) ->
  preview = this.closest(".compose")
  error_class = if jqXHR.status == 403 then "permission-denied" else "uknown"
  error = preview.find(".preview-error.#{error_class}")
  error.find(".status-code").text(jqXHR.status)
  error.find(".status-text").text(jqXHR.statusText)
  error.show()
  preview.find("[type=submit]").attr("disabled", "disabled")

review_received = (html) ->
  preview = $("#"+$(this).closest(".compose").data("preview-id"));
  preview.html(html)
  preview.find(".voting").hide()
  preview.find(".options").hide()
  preview.find(".comments").hide()
  preview.find("[type=submit]").attr("disabled", null)
  MathJax.Hub.Queue(["Typeset", MathJax.Hub, preview.get(0)]);

submit = (container) ->
  form = container.find("> form")

  # Validate rating input
  if form.find("input[name=rating]").val() == "-1"
    if container.hasClass("compose-review")
      return container.find(".form-error.rating").show()

  # Validate text
  if !($.trim(form.find("textarea").val()))
    return container.find(".form-error.text").show()

  container.find("[type=submit]").hide().siblings(".spinner").show()

  $.ajax({
    type: "POST",
    url: REVIEW_API_URL,
    data: get_form_data(form),
    success: (-> window.location.reload()),
    error: error_received.bind(form)
  })


keyup = (e) ->
  last_keypress = Date.now() if not last_keypress?
  delta = Date.now() - last_keypress

  if delta > TIMEOUT_AFTER
    last_keypress = null
  else
    clearTimeout(timeout);
    timeout = setTimeout(stopped_typing.bind(e), TIMEOUT_AFTER);

init_writing = (container) ->
  if $(container).prop("initialised") == true
    return

  form = $(container).find("form")
  $(container).find("textarea").keyup(keyup)
  $(container).prop("initialised", true);

  stopped_typing form
  form.find("select,input").change(-> stopped_typing form)


$(".compose textarea").focus(->
  compose = $(this).closest(".compose")
  init_writing(compose)
  compose.find(".form-error.text").hide()
)

$(".compose [type=submit]").click((e) ->
  e.preventDefault()
  submit($(this).closest(".compose"))
)

