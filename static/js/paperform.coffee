$("#id_title, #id_authors, #id_keywords, #id_abstract, #id_publisher, #id_publish_date, #id_urls").parent().parent().hide();
$("#id_doc_id").parent().parent().hide();

$("#id_type").change(`function(){
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
}`)