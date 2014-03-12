`
function renew_form(){
    switch($("#id_type :selected").val()){
        case "doi":
        case "arxiv":
            $("#id_title, #id_authors, #id_keywords, #id_abstract, #id_publisher, #id_publish_date, #id_urls").parent().parent().hide();
            $("#id_doc_id").parent().parent().show();
            break;
        case "":
            $("#id_title, #id_authors, #id_keywords, #id_abstract, #id_publisher, #id_publish_date, #id_urls").parent().parent().hide();
            $("#id_doc_id").parent().parent().hide();
            break;
        default:
            $("#id_title, #id_authors, #id_keywords, #id_abstract, #id_publisher, #id_publish_date, #id_urls").parent().parent().show();
            $("#id_doc_id").parent().parent().show();
    }
}

renew_form();
$("#id_type").change(renew_form);

var latest_request;

$("#id_doc_id").keyup(function(){
    var current_type = $("#id_type :selected").val();
    if (current_type == 'doi' || current_type == 'arxiv'){
        if (latest_request) latest_request.abort();
        latest_request = $.ajax({
            type: "GET",
            url: "/papers/"+current_type+"/"+$("#id_doc_id").val()
        });
        latest_request.done(function(data){
            $("#id-scraper-field").html(data);
        });
    }


})

`