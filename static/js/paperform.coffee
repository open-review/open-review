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
    $("#id-scraper-field").html("<i>Retrieving document information</i>");
    if (current_type == 'doi' || current_type == 'arxiv'){
        if (latest_request) latest_request.abort();
        latest_request = $.ajax({
            type: "GET",
            url: "/papers/"+current_type+"/"+$("#id_doc_id").val()
        });
        latest_request.done(function(data){
            if (data.error){
                $("#id-scraper-field").html("<b>Error: </b><i>"+data.error+"</i>");
            } else {
                $("#id-scraper-field").html("<h2>"+data.title+"</h2><br/><b>Author(s): </b><i>"+data.authors.join(", ")+
                "</i><br/><b>Abstract:</b> "+data.abstract+"<br/><b>URL:</b> <a href='"+data.urls+"'>"+data.urls+"</a>");
            }
            MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
        });
    }


}

renew_form();
$("#id_type").change(renew_form);

var latest_request;

$("#id_doc_id").keyup(load_scraper)

`