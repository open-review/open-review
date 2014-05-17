TIMEOUT_AFTER = 750

PREVIEW_PROCEDURE_API_URL = "/api/v1/procedures/preview"
REVIEW_API_URL = "/api/v1/reviews/"

anonymous = $("body").data("anonymous")
last_keypress = null
timeout = null

###
  Parses form elements, and puts them in an object. For example:

  <div>
   <input name=foo type=hideen value=1 />
  </div>

  becomes:

  { foo: "1" }
###
get_form_data = (form) ->
  form_data = {}
  form.serializeArray().map((x) ->
    form_data[x.name] = x.value
  );

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

  preview.closest(".review-container").find("[type=submit]").show().siblings(".spinner").hide()

review_received = (html) ->
  preview = $("#"+$(this).closest(".compose").data("preview-id"));
  preview.html(html)
  preview.find(".voting").hide()
  preview.find(".options").hide()
  preview.find(".comments").hide()
  MathJax.Hub.Queue(["Typeset", MathJax.Hub, preview.get(0)]);

submit = (container) ->
  form = container.find("> form")
  form_data = get_form_data(form)

  # Validate rating input if we are a top-level review
  if form_data.rating == "-1" and not form_data.parent?
      console.log("Wrong rating: not submitting.")
      return container.find(".form-error.rating").show()

  # Validate text
  if !($.trim(form_data.text))
    console.log("Wrong text: not submitting.")
    return container.find(".form-error.text").show()

  container.find("[type=submit]").hide().siblings(".spinner").show()

  request = {
    type: "POST",
    url: REVIEW_API_URL,
    data: form_data,
    success: (-> window.location.reload()),
    error: error_received.bind(form),
  }

  if form_data.review?
    # A review is defined, which means we're editing an existing
    # contribution. We need to change the url, so we can post to
    # an API object url
    request.url += form_data.review + "/"

    # As some browsers do not support PATCH methods a workaround
    # is needed to perform correctly in all cases. See also:
    # http://stackoverflow.com/q/22813013
    request.headers = {
      'X-HTTP-Method-Override': 'PATCH'
    }

  $.ajax request


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


# Initialise clicking on textareas
$(".compose textarea").focus(->
  compose = $(this).closest(".compose")
  init_writing(compose)
  compose.find(".form-error.text").hide()
)

# Catch submit button
$(".compose [type=submit]").click((e) ->
  e.preventDefault()
  submit($(this).closest(".compose"))
)

# Collapse / show editing area if user clicked edit button
$(".review .options .edit, .review .options .reply").click((e) ->
  e.preventDefault();
  target = $("#" + $(e.currentTarget).data("edit-id"))
  other = target.siblings(".edit-form")

  # Hide other and its preview
  other.hide()
  $("#" + other.data("preview-id")).hide()

  # Toggle ourselves
  target.toggle()
  $("#" + target.data("preview-id")).toggle()

  if target.is(":visible")
    target.find("textarea").focus()
)

# Show edit button for each owned review
$.map($(".paper").data("reviews"), (review_id) ->
  $(".review[data-review-id=#{review_id}] .edit").show();
)

# Show reply button if logged in
if not anonymous
  $(".review .options .reply").show();
