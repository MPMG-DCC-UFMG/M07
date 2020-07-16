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


    var num_buscas_ctx = $("#grafico-linha-num_buscas-dia").get(0).getContext("2d");
    var gradientStrokeFill_1 = num_buscas_ctx.createLinearGradient(0, 0, 0, 450);
        gradientStrokeFill_1.addColorStop(1, 'rgba(255,255,255, 0.0)');
        gradientStrokeFill_1.addColorStop(0, 'rgba(102,78,235, 0.2)');
    var num_buscas_config = {
        type: 'bar',
        data: {
            datasets: [{
                data: total_searches_per_day['data'],
                // borderColor: '#36a2eb',
                backgroundColor: '#36a2eb',

            }],
            labels: total_searches_per_day['labels']
        },
        options: {
            legend: false
        }
    }
    var grafico_num_buscas_dia = new Chart(num_buscas_ctx, num_buscas_config);


    var no_clicks_ctx = $("#grafico-consultas-sem-clique").get(0).getContext("2d");
    var no_clicks_config = {
        type: 'bar',
        data: {
            datasets: [{
                data: no_clicks_per_day['data'],
                backgroundColor: '#ffcd56',

            }],
            labels: no_clicks_per_day['labels']
        },
        options: {
            legend: false
        }
    }
    var grafico_sem_cliques_dia = new Chart(no_clicks_ctx, no_clicks_config);
});