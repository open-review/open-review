$(document).ready ->
    $(".starfield").each ->
        field = $(this).data("field");
        f = $(this).parents("form").find("input[name=#{field}]");
        if $(this).data("score")
            score = $(this).data("score");
        else
            score = f.val();
        
        readOnly = false;
        if $(this).data("readonly")
            readOnly = $(this).data("readonly");
        
        $(this).raty({
            click       : (score) -> f.val(score),
            hints       : ['1 star', '2 stars', '3 stars', '4 stars', '5 stars', '6 stars', '7 stars'],
            number      : 7,
            path        : "#{window.staticUrl}raty/lib/images/",
            readOnly    : readOnly,
            score       : score
            # It should be possible to use scoreName: field instead of score and click, but for some unknown reason that does not seem to work
        });
