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
});