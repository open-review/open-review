# Star rating input fields
fix_stars = (field, val) ->
    html = "";
    for i in [1..7]
        do (i) ->
            star = if val >= i then "★" else "☆"
            html += "<span data-star=\"#{i}\">#{star}</span>";
    
    field.html(html);
    
    field.find("span").each ->
        $(this).mouseenter ->
            val = $(this).data("star");
            fix_stars($(this).closest(".rating-input"), val);
        
        $(this).click ->
            field_id = field.data("id");
            val = $(this).data("star");
            $("##{field_id}").val(val);
    
    field.mouseleave ->
        field_id = field.data("id");
        val = parseInt($("##{field_id}").val(), 10);
        fix_stars(field, val);

$(".rating-input").each ->
    field_id = $(this).data("id");
    val = parseInt($("##{field_id}").val(), 10);
    fix_stars($(this), val);


