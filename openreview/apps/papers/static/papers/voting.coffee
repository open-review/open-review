anonymous = $("body").data("anonymous")

###
Given a vote-button, change its value with `delta`.
###
change_btn_value = (btn, delta) ->
  btn = btn.find ".counter"
  btn.text(parseInt(btn.text()) + delta)

change_counter = (counter, value, reversed) ->
  value = if reversed then value * -1 else value
  counter.text(parseInt(counter.text()) + value)

###
Function called when a vote button is clicked
###
vote = (btn, value) ->
  review = btn.closest(".review")
  counter = btn.siblings(".counter")
  reversed = btn.hasClass("voted")

  if review.find("article").hasClass("deleted")
    return review.find(".deleted-message").show()

  if anonymous
    return review.find(".login-message").show()

  # Send vote; don't do anything if server reports error.
  $.ajax {
    method: "POST",
    url : review.find(".voting").data("url")
    data: {
      vote: if reversed then 0 else value,
      csrfmiddlewaretoken: $("body").data("csrf")
    }
  }

  # Remove state of *other* button
  btn.siblings().removeClass("voted")
  console.log(counter, value, reversed)
  change_counter(counter, value, reversed)

  if reversed
    btn.removeClass("voted")
  else
    btn.addClass("voted")

###
Initialise vote buttons (make sure they've got the correct classes)
###
init_votes = ->
  votes = $(".paper").data("votes")

  $.each(votes, (review_id, vote) ->
    if vote == 0
      return

    element = $(".review[data-review-id='#{review_id}']")
    element = element.find(if vote > 0 then ".up" else ".down")
    element.addClass("voted")
  );

###
All owned reviews should display a
###
init_reviews = ->
  reviews = $(".paper").data("reviews");

  for review_id in reviews
    review = $(".review[data-review-id='#{review_id}']")
    review.addClass("own")

###
###
init = ->
  if not anonymous
    init_votes()
    init_reviews()

  $(".review .voting .up").click((e) -> vote($(e.currentTarget), 1))
  $(".review .voting .down").click((e) -> vote($(e.currentTarget), -1))

init()

