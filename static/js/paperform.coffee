`
function renew_form(){
    var form_elems = "#id_title, #id_authors, #id_keywords, #id_abstract, #id_publisher, #id_publish_date, #id_urls";

    $("#id-scraper-field").hide();
    switch($("#id_type :selected").val()){
        case "doi":
        case "arxiv":
            $(form_elems).parents(".form-group").hide();
            $("#id-scraper-field").show();
            $("#id_doc_id").parents(".form-group").show();
            load_scraper();
            break;
        case "":
            $(form_elems).parents(".form-group").hide();
            $("#id-scraper-field").hide();
            $("#id_doc_id").parents(".form-group").hide();
            break;
        default:
            $(form_elems).parents(".form-group").show();
            $("#id_doc_id").parents(".form-group").show();
    }
}

function load_scraper(){
    var current_type = $("#id_type :selected").val();
    $("#scraper-status").text("Retrieving document information");
    $("#scraper-status").show();
    $("#scraper-result").hide();
    if (current_type == 'doi' || current_type == 'arxiv'){
        if (latest_request) latest_request.abort();
        latest_request = $.ajax({
            type: "GET",
            url: "/papers/"+current_type+"/"+$("#id_doc_id").val()
        });
        latest_request.done(function(data){
            if (data.error){
                $("#scraper-status").text(data.error);
                $("#scraper-status").show();
                $("#scraper-result").hide();
            } else {
                $("#scraper-title").text(data.title);
                $("#scraper-authors").text(data.authors.join(", "));
                $("#scraper-abstract").text(data.abstract);
                $("#scraper-url").text(data.urls);
                $("#scraper-publisher").text(data.publisher);
                $("#scraper-publish-date").text(data.publish_date);
                
                for(i=0; i < data.categories.length; i++){
                  $('#span_id > select > option[value=data.category[i]]').attr("selected", "selected")
                }
                
                $("#scraper-result").show();
                $("#scraper-status").hide();
            }
            MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
        });
    }


}

renew_form();
$("#id_type").change(renew_form);

var latest_request;

$("#id_doc_id").on('input', null, null, load_scraper)

`