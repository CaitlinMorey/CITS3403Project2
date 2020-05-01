var ctx = document.getElementById("barGraph").getContext("2d");
    

var myBarChart = new Chart(ctx, {
    type: 'bar',
    data: {
    labels: ["CSS","HTML","Javascript"], 
    datasets: [
        {
            label: "average score",
            data: [1,4,28]
        }]},
    options: {
    }});