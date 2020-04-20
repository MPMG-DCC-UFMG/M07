function log_search_result_click(link){
    var query = $('#results-container').data('executed-query');
    $.ajax({
        async: false,
        url: SERVICES_URL+'log_search_result_click',
        type: 'post',
        dataType: 'json',
        data:{
            session_id: 123,
            user_id: 0,
            rank_number: $(link).data('rank-number'),
            item_id: $(link).data('item-id'),
            item_type: $(link).data('item-type'),
            query: query,
        }
    });
}

function log_suggestion_click(item){
    $.ajax({
        url: SERVICES_URL+'log_query_suggestion_click',
        type: 'post',
        dataType: 'json',
        data:{
            session_id: 123,
            user_id: 0,
            rank_number: item['rank_number'],
            suggestion_id: item['suggestion_id'],
        }
    });
}

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

        },
        select: function(event, ui) {
            log_suggestion_click(ui['item']);
        }
    });

    $('#results-container .result-link').on('mousedown', function(e1){
        $('#results-container .result-link').one('mouseup', function(e2){
          if (e1.which == 2 && e1.target == e2.target) { // consider only the middle button click
            log_search_result_click(e2.target);
          }
        });
      });

    $('#results-container .result-link').click(function(e){
        // e.preventDefault();
        log_search_result_click(e.target);
    });
});