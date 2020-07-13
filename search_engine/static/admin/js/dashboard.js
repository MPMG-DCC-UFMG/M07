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
        type: 'line',
        data: {
            datasets: [{
                data: total_searches_per_day['data'],
                borderColor: '#36a2eb',
                backgroundColor: gradientStrokeFill_1

            }],
            labels: total_searches_per_day['labels']
        },
        options: {
            legend: false
        }
    }
    var grafico_num_buscas_dia = new Chart(num_buscas_ctx, num_buscas_config);
});