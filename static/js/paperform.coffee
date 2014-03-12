`
function renew_form(){
    $("#id-scraper-field").html("");
    switch($("#id_type :selected").val()){
        case "doi":
        case "arxiv":
            $("#id_title, #id_authors, #id_keywords, #id_abstract, #id_publisher, #id_publish_date, #id_urls").parent().parent().hide();
            $("#id-scraper-field").show();
            $("#id_doc_id").parent().parent().show();
            load_scraper();
            break;
        case "":
            $("#id_title, #id_authors, #id_keywords, #id_abstract, #id_publisher, #id_publish_date, #id_urls").parent().parent().hide();
            $("#id-scraper-field").hide();
            $("#id_doc_id").parent().parent().hide();
            break;
        default:
            $("#id_title, #id_authors, #id_keywords, #id_abstract, #id_publisher, #id_publish_date, #id_urls").parent().parent().show();
            $("#id_doc_id").parent().parent().show();
    }
}

function load_scraper(){
    var current_type = $("#id_type :selected").val();
    if (current_type == 'doi' || current_type == 'arxiv'){
        if (latest_request) latest_request.abort();
        latest_request = $.ajax({
            type: "GET",
            url: "/papers/"+current_type+"/"+$("#id_doc_id").val()
        });
        latest_request.done(function(data){
            $("#id-scraper-field").html("<h2>"+data.title+"</h2><br/><b>Authors: </b><i>"+data.authors.join(", ")+"</i><br/><b>Abstract:</b> "+data.abstract);
        });
    }


}

renew_form();
$("#id_type").change(renew_form);

var latest_request;

$("#id_doc_id").keyup(load_scraper)

`