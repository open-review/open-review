delete_review = (e) ->
  e.preventDefault()
  url = $(this).attr("href")
  csrf = $("body").data("csrf")

  $.ajax({
    type: "POST", url: url,
    headers: {
      'X-HTTP-Method-Override': 'DELETE',
      'X-CSRFToken': csrf
    }
  })

  review = $(this).closest(".review")
  review.find("article").addClass("deleted").empty().text("[deleted]")
  review.find(".author").text("Anonymous")
  review.find(".delete").hide()
  review.find(".edit").hide()


$(".review .options .delete").click delete_review

$.each($(".paper").data("reviews"), ->
  $("[data-review-id=#{this}] .options .delete").show()
)
