( function( factory ) {
	if ( typeof define === "function" && define.amd ) {

		// AMD. Register as an anonymous module.
		define( [ "../widgets/datepicker" ], factory );
	} else {

		// Browser globals
		factory( jQuery.datepicker );
	}
}( function( datepicker ) {

datepicker.regional[ "pt-BR" ] = {
	closeText: "Fechar",
	prevText: "&#x3C;Anterior",
	nextText: "Próximo&#x3E;",
	currentText: "Hoje",
	monthNames: [ "Janeiro","Fevereiro","Março","Abril","Maio","Junho",
	"Julho","Agosto","Setembro","Outubro","Novembro","Dezembro" ],
	monthNamesShort: [ "Jan","Fev","Mar","Abr","Mai","Jun",
	"Jul","Ago","Set","Out","Nov","Dez" ],
	dayNames: [
		"Domingo",
		"Segunda-feira",
		"Terça-feira",
		"Quarta-feira",
		"Quinta-feira",
		"Sexta-feira",
		"Sábado"
	],
	dayNamesShort: [ "Dom","Seg","Ter","Qua","Qui","Sex","Sáb" ],
	dayNamesMin: [ "Dom","Seg","Ter","Qua","Qui","Sex","Sáb" ],
	weekHeader: "Sm",
	dateFormat: "dd/mm/yy",
	firstDay: 0,
	isRTL: false,
	showMonthAfterYear: false,
	yearSuffix: "" };
datepicker.setDefaults( datepicker.regional[ "pt-BR" ] );

return datepicker.regional[ "pt-BR" ];

} ) );

$(function(){
    
    $('.datepicker').datepicker();
	$('[data-toggle="tooltip"]').tooltip({boundary:"viewport"});
	
	$('.results-per-page').change(function(){
		var targetForm = $(this).data('target-form');
		var selectedValue = $(this).val();
		$('#'+targetForm).find('input[name=results_per_page]').val(selectedValue);
		$('#'+targetForm).submit();
	});

	$('.clear-form').click(function(){
		var formObj = $(this).parents('form');
		formObj.find('input,select').each(function(i){
			if($(this).attr('data-no-reset') == undefined){
				if($(this).prop("tagName") == "INPUT")
					$(this).val("")
				else if($(this).prop("tagName") == "SELECT")
					$(this)[0].selectedIndex = 0;
			}
		});
	});

	$('#log-search-table tr').click(function(){
		var id_sessao = $(this).data('id-sessao');
		$('.detalhe-consultas').html('')
		var ajax = $.get('/admin/log_search_detail/?id_sessao='+id_sessao)
		ajax.done(function(response){
			response = response['session_detail'];
			$('.detalhe-id-sessao').html(id_sessao);
			$('.detalhe-nome-usuario').html(response['id_usuario']);

			for(var id_consulta in response['consultas']){
				var template_consulta = $($("#detalhe-template-consulta .detalhe-item-consulta").get(0).outerHTML);
				template_consulta.find('.detalhe-id-consulta').html(id_consulta);
				template_consulta.find('.detalhe-texto-consulta').html(response['consultas'][id_consulta]['text_consulta']);
				template_consulta.find('.detalhe-algoritmo').html(response['consultas'][id_consulta]['algoritmo']);

				for(var num_pagina in response['consultas'][id_consulta]['paginas']){
					var template_pagina = $($("#detalhe-template-consulta .detalhe-item-pagina").get(0).outerHTML);
					template_pagina.find('.detalhe-numero-pagina').html(num_pagina);
					template_pagina.find('.detalhe-data-hora').html(response['consultas'][id_consulta]['paginas'][num_pagina]['data_hora']);
					template_pagina.find('.detalhe-tempo-resposta').html(response['consultas'][id_consulta]['paginas'][num_pagina]['tempo_resposta_total']);
					for(var i=0; i<response['consultas'][id_consulta]['paginas'][num_pagina]['documentos'].length; i++){
						var doc_id = response['consultas'][id_consulta]['paginas'][num_pagina]['documentos'][i];
						template_pagina.find('.detalhe-documentos').append(doc_id+'<br>');
					}
					template_consulta.find('.detalhe-paginas').append(template_pagina);
				}

				$('.detalhe-consultas').append(template_consulta);
			}
		});
		
		ajax.fail(function(){
			console.log('falha');
		});

		$('#log-search-detail').modal();
	});
});
	
function get_algo_options(){
	var selected_algo = $('#id_algorithm').val().toLowerCase();
	$( "#id_algorithm" ).children('option').each(function( index ) {
		var algo = $( this ).val().toLowerCase();
		var elements_by_class = $('.' + algo);
		$.each(elements_by_class, function() {
			var cur_id = $( this ).attr('id');
			if (algo == selected_algo) { // Mostrar opções
				$('#' + cur_id).show();
				$( "label[for='" + cur_id + "']").show();
			}
			else { // Esconder opções
				$('#' + cur_id).hide();
				$( "label[for='" + cur_id + "']").hide();
			}
		});
	});
};

$(function(){
	get_algo_options();
  
	$('#id_algorithm').change(function(){
		get_algo_options();
	});
});