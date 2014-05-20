mouse_enter = (event) ->
  set_value(this, $(event.currentTarget).data("star"))

mouse_leave = ->
  set_value(this, get_value(this))

star_clicked = (event) ->
  set_hidden_value(this, $(event.currentTarget).data("star"))
  get_hidden_input(this).closest("form").find(".form-error.rating").hide()


# Set stars of `field` to `value` (populate an amount of 'coloured' stars).
set_value = (field, value) ->
  $("span", field).text("☆")

  if value == -1
    return

  $.map([1..value], (v) ->
    $(":nth-child(#{v})", field).text("★")
  )

# Sets hidden value of `field` to `value`.
set_hidden_value = (field, value) ->
  get_hidden_input(field).val(value).trigger("change")

get_hidden_input = (field) ->
  return $("#" + field.parent().data("id"))

# Get current value of hidden input field. Returns -1 if an illegal value
# is currently specified.
get_value = (field) ->
  input = $("#" + field.parent().data("id"))
  value = parseInt(input.val(), 10)

  if isNaN(value)
    return -1
  return value

# Initialises star_input (sets triggers, creates empty star containers)
init_star_input = (field) ->
  field.append($("<div>"))
  field = field.children().first()
  field.html ($("<span>").data("star", i) for i in [1..7])
  field.mouseleave(mouse_leave.bind(field))

  $("span", field)
    .mouseenter(mouse_enter.bind(field))
    .click(star_clicked.bind(field))

  set_value(field, get_value(field))
  set_hidden_value(field, get_value(field))

# Initialise all rating inputs
$.map($(".rating-input"), (e) -> init_star_input $(e))
