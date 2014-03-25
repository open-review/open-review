delete_review = ->
  review = $(this).closest(".review")
  url = review.find(".permalink").attr("href")
  csrf = $("body").attr("csrf")

  $.ajax({
    type: "DELETE", url: url, csrf: csrf,
    beforeSend: (xhr) ->
      # JQuery is confused when using data, this is a workaround
      xhr.setRequestHeader("X-CSRFToken", csrf);
  })

  review.find("article").addClass("deleted").empty()
  review.find(".author").text("?")
  review.find(".delete").hide()
  review.find(".edit").hide()


$(".review .delete.btn").click delete_review