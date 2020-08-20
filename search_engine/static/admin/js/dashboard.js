$(function(){

    var qtdes_ctx = $("#grafico-pizza-qtdes-indices").get(0).getContext("2d");
    var qtdes_config = {
        type: 'pie',
        data: {
            datasets: [{
                data: indices_amounts['data'],
                backgroundColor: indices_amounts['colors'],
            }],
            labels: indices_amounts['labels']
        },
        options: {
            legend:{
                position: 'left',
            },
            responsive: true
        }
    };
    var grafico_qtdes_indices = new Chart(qtdes_ctx, qtdes_config);


    var num_buscas_ctx = $("#grafico-num-buscas-dia").get(0).getContext("2d");
    var num_buscas_config = {
        type: 'bar',
        data: {
            datasets: [
                {label: 'Total',
                data: total_searches_per_day['data'],
                backgroundColor: '#36a2eb',},

                {label: 'Sem cliques',
                data: no_clicks_per_day['data'],
                backgroundColor: '#ffcd56',},

                {label: 'Sem resultados',
                data: no_results_per_day['data'],
                backgroundColor: '#ff9f40'},

            ],
            labels: total_searches_per_day['labels']
        },
        options: {
            legend: {}
        }
    }
    var grafico_num_buscas_dia = new Chart(num_buscas_ctx, num_buscas_config);


    var response_time_ctx = $("#grafico-tempo-resposta").get(0).getContext("2d");
    var response_time_config = {
        type: 'line',
        data: {
            datasets: [
                {label: 'Tempo de resposta',
                data: response_time_per_day['data'],
                borderColor: '#6ac472',
                backgroundColor: '#b2e1b6',},
            ],
            labels: response_time_per_day['labels']
        },
        options: {
            legend: false,
            elements: {
                point: {
                    radius: 3,
                    backgroundColor: "#000"
                },
                line: {
                    tension: 0
                }
            },
        }
    }
    var chart_response_time = new Chart(response_time_ctx, response_time_config);


    var no_clicks_ctx = $("#grafico-consultas-sem-clique").get(0).getContext("2d");
    var no_clicks_config = {
        type: 'bar',
        data: {
            datasets: [{
                data: porc_no_clicks_per_day['data'],
                backgroundColor: '#ffcd56',

            }],
            labels: porc_no_clicks_per_day['labels']
        },
        options: {
            legend: false,
            scales: {
                yAxes: [{
                    ticks: {
                        min: 0,
                        max: 100
                    }
                }]
            },
        }
    }
    var grafico_sem_cliques_dia = new Chart(no_clicks_ctx, no_clicks_config);


    var no_results_ctx = $("#grafico-consultas-sem-resultado").get(0).getContext("2d");
    var no_results_config = {
        type: 'bar',
        data: {
            datasets: [{
                data: porc_no_results_per_day['data'],
                backgroundColor: '#ff9f40',

            }],
            labels: porc_no_results_per_day['labels']
        },
        options: {
            legend: false,
            scales: {
                yAxes: [{
                    ticks: {
                        min: 0,
                        max: 100
                    }
                }]
            },
        }
    }
    var grafico_sem_resultados_dia = new Chart(no_results_ctx, no_results_config);
});