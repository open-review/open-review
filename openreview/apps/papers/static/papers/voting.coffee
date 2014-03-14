###
Given a vote-button, change its value with `delta`.
###
change_btn_value = (btn, delta) ->
  btn = btn.find ".count"
  btn.text(parseInt(btn.text()) + delta)

###
Remove voted-classes and reset counter
###
clear_btn = (btn) ->
  if not btn.hasClass "voted"
    return

  btn.removeClass "voted btn-success btn-danger"
  btn.addClass "btn-default"
  change_btn_value(btn, -1)

###
Function called when a vote button is clicked
###
vote = (btn, value) ->
  review = btn.closest ".review"
  if not review.hasClass("enabled")
    return review.find(".login").show()

  review_id = review.attr("review_id")
  value = 0 if btn.hasClass("voted")

  # Send vote; don't do anything if server reports error.
  $.ajax("review/#{review_id}/vote?vote=#{value}")

  # Remove state of *other* button
  clear_btn btn.siblings(".btn")

  if btn.hasClass("voted")
    change_btn_value(btn, -1)
    btn.removeClass("voted btn-danger btn-success")
    btn.addClass "btn-default"
  else
    change_btn_value(btn, 1)
    btn.removeClass "btn-default"
    btn.addClass("voted " + (if btn.hasClass "upvote" then "btn-success" else "btn-danger"))

$(".review .upvote").click((e) -> vote($(e.currentTarget), 1))
$(".review .downvote").click((e) -> vote($(e.currentTarget), -1))
$(".review .login").hide()
