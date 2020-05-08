$(document).ready(function(){
    var _data;
    var _labels;
   $.ajax({
    url: "/data",
    type: "get",
    data: {vals: ''},
    success: function(response) {
      full_data = JSON.parse(response.payload);
      _data = full_data['values'];
      _labels = full_data['labels'];
    },
 
});

var ctx = document.getElementById("barGraph").getContext("2d");
    

var myBarChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: _labels,  
        datasets: [
            {
                label: "average score",
                backgroundColor: ["blue","red","yellow"],
                data: _data
            }]
        },
    options: {
        responsive: true,
        title: {
            display: true,
            text: 'Number of Attempts for each Quiz'
        },
        scales: {
            yAxes: [{
                ticks: {   
                    max: 20,
                    beginAtZero: true
                } 
            }],
        }   
    },
});
});