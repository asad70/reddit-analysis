Chart.defaults.global.pointHitDetectionRadius = 1;
Chart.defaults.global.tooltips.enabled = false;
Chart.defaults.global.tooltips.mode = 'index';
Chart.defaults.global.tooltips.position = 'nearest';
Chart.defaults.global.tooltips.custom = coreui.ChartJS.customTooltips;
Chart.defaults.global.defaultFontColor = '#646470';
Chart.defaults.global.responsiveAnimationDuration = 1;
document.body.addEventListener('classtoggle', function (event) {
  if (event.detail.className === 'c-dark-theme') {
    if (document.body.classList.contains('c-dark-theme')) {
      cardChart1.data.datasets[0].pointBackgroundColor = coreui.Utils.getStyle('--primary-dark-theme');
      cardChart2.data.datasets[0].pointBackgroundColor = coreui.Utils.getStyle('--info-dark-theme');
      Chart.defaults.global.defaultFontColor = '#fff';
    } else {
      cardChart1.data.datasets[0].pointBackgroundColor = coreui.Utils.getStyle('--primary');
      cardChart2.data.datasets[0].pointBackgroundColor = coreui.Utils.getStyle('--info');
      Chart.defaults.global.defaultFontColor = '#646470';
    }

    cardChart1.update();
    cardChart2.update();
    redditChart.update();
  }
}); // eslint-disable-next-line no-unused-vars

var redditChart = new Chart(document.getElementById('reddit-chart'), {
    type: 'line',
    data: {
      labels: ['M', 'T', 'W', 'T', 'F', 'S', 'S', 'M', 'T', 'W', 'T', 'F', 'S', 'S', 'M', 'T', 'W', 'T', 'F', 'S', 'S', 'M', 'T', 'W', 'T', 'F', 'S', 'S'],
      datasets: [{
        label: 'My First dataset',
        backgroundColor: coreui.Utils.hexToRgba(coreui.Utils.getStyle('--info'), 10),
        borderColor: coreui.Utils.getStyle('--info'),
        pointHoverBackgroundColor: '#fff',
        borderWidth: 2,
        data: [100, 180, 70, 69, 77, 57, 125, 165, 172, 91, 173, 138, 155, 89, 50, 161, 65, 163, 160, 103, 114, 185, 125, 196, 183, 64, 137, 95, 112, 175]
      }, {
        label: 'My Second dataset',
        backgroundColor: 'transparent',
        borderColor: coreui.Utils.getStyle('--success'),
        pointHoverBackgroundColor: '#fff',
        borderWidth: 2,
        data: [90, 97, 80, 100, 86, 97, 83, 98, 87, 98, 93, 83, 87, 98, 96, 84, 91, 97, 88, 86, 94, 86, 95, 91, 98, 91, 92, 80, 83, 82]
      }, {
        label: 'My Third dataset',
        backgroundColor: 'transparent',
        borderColor: coreui.Utils.getStyle('--danger'),
        pointHoverBackgroundColor: '#fff',
        borderWidth: 1,
        borderDash: [8, 5],
        data: [65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65]
      }]
    },
    options: {
      maintainAspectRatio: false,
      legend: {
        display: false
      },
      scales: {
        xAxes: [{
          gridLines: {
            drawOnChartArea: false
          }
        }],
        yAxes: [{
          ticks: {
            beginAtZero: true,
            maxTicksLimit: 5,
            stepSize: Math.ceil(250 / 5),
            max: 250
          }
        }]
      },
      elements: {
        point: {
          radius: 0,
          hitRadius: 10,
          hoverRadius: 4,
          hoverBorderWidth: 3
        }
      }
    }
  });