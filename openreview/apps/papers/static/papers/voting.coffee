anonymous = JSON.parse($("#anonymous").html())

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
  review = btn.closest(".review")
  if review.find("article").hasClass("deleted")
    return review.find(".deleted-message").show()

  if anonymous
    return review.find(".login-message").show()


  review_id = review.attr("review_id")
  value = 0 if btn.hasClass("voted")

  # Send vote; don't do anything if server reports error.
  url = review.find(".permalink").attr("href")
  url += "/vote?vote=#{value}"
  $.ajax url

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

###
Initialise vote buttons (make sure they've got the correct classes)
###
init_votes = ->
  votes = JSON.parse($("#my_votes").html())

  $.each(votes, (review_id, vote) ->
    element = $(".review[review_id='#{review_id}']")
    element = element.find(if vote > 0 then ".upvote" else ".downvote")
    element.removeClass("btn-default").addClass("voted")
    element.addClass(if vote > 0 then "btn-success" else "btn-danger")
  );

###
All owned reviews should display a
###
init_reviews = ->
  reviews = JSON.parse($("#my_reviews").html())

  for review_id in reviews
    review = $(".review[review_id='#{review_id}']")
    review.find(".btn:hidden").show()
    review.find(".flag").hide()
    review.addClass("bs-callout-success")

###
###
init = ->
  if not anonymous
    init_votes()
    init_reviews()

  $(".review .upvote").click((e) -> vote($(e.currentTarget), 1))
  $(".review .downvote").click((e) -> vote($(e.currentTarget), -1))

init()

