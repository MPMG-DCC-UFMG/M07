$(function(){
    $("#query").autocomplete({
        source: function(request, response){
            var ajax = $.ajax({
                url: SERVICES_URL+'query_suggestion',
                type: 'get',
                dataType: 'json',
                data:{
                    query: request.term
                }
            });

            ajax.done(function(data){
                suggestions = data['suggestions'];
                response(suggestions);
            });

        }
    });
});