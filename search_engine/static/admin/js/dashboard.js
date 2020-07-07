$(function(){
    var config = {
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

    var ctx = $("#grafico-pizza-qtdes-indices").get(0).getContext("2d");
    var grafico_qtdes_indices = new Chart(ctx, config);
});