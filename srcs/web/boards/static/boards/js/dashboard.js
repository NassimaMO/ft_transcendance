document.querySelectorAll('.display-button').forEach(function(button) {
  button.addEventListener('click', function() {
    var contentToHide = document.querySelector('.statistics');
    var otherContentToHide = document.querySelector('.streak');
    var infoContentToHide = document.querySelector('.more-info');
    var newContent = document.querySelector('.overlay-info');
    
    if (contentToHide.classList.contains('hidden')) {
      contentToHide.classList.remove('hidden');
      otherContentToHide.classList.remove('hidden');
      newContent.classList.remove('show');
      infoContentToHide.style.display = "block";
      otherContentToHide.style.display = "block";
    } else {
        contentToHide.classList.add('hidden');
        otherContentToHide.classList.add('hidden');
        newContent.classList.add('show');
      infoContentToHide.style.display = "none";
      otherContentToHide.style.display = "none";
    }
  });
});

var ctx = document.getElementById('avg-score-graph').getContext('2d');

var matchScoresChart = new Chart(ctx, {
type: 'line',
data: {
    labels: matchDates,
    datasets: [{
        data: matchScores,
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
            beginAtZero: true,
            min: 0,
            max: 5
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