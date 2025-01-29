
document.querySelectorAll('.display-button').forEach(function(button) {
  button.addEventListener('click', function() {
    var contentToHide = document.querySelector('.statistics');
    var otherContentToHide = document.querySelector('.streak');
    var infoContentToHide = document.querySelector('.more-info');
    var newContent = document.querySelector('.overlay-info');
    
    if (contentToHide.classList.contains('hidden')) {
      contentToHide.classList.remove('hidden');
      otherContentToHide.classList.remove('hidden');
      newContent.style.display = "none";
      infoContentToHide.style.display = "block";
      otherContentToHide.style.display = "block";
    } else {
      contentToHide.classList.add('hidden');
      otherContentToHide.classList.add('hidden');
      newContent.style.display = "block";
      infoContentToHide.style.display = "none";
      otherContentToHide.style.display = "none";
    }
  });
});

var ctx = document.getElementById('avg-score-graph').getContext('2d');

var matchScoresChart = new Chart(ctx, {
type: 'line',
data: {
    labels: ['12/04/2021', '05/08/2019', '23/11/2020', '15/06/2018', '09/02/2023', '30/09/2022', '17/12/2020', '25/07/2017', '02/03/2021', '19/10/2019'],
    datasets: [{
        data: [1, 2, 2, 4, 5, 5, 3, 4, 0, 4],
    }]
},
options: {
    responsive: true,
    scales: {
        x: {
            display: false,
        },
        y: {
            title: {
                display: false,
            },
            ticks: {
                display: true,
            },
            beginAtZero: true
        }
    },
    plugins: {
        legend: {
            display: false,
        },
        tooltip: {
            enabled: true,
        }
    }
}
});