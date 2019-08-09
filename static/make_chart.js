data = [randomScalingFactor(),
				randomScalingFactor(),
				randomScalingFactor(),
				randomScalingFactor(),
				randomScalingFactor(),
				randomScalingFactor(),
				randomScalingFactor()]

var myLineChart = new Chart(ctx, {
    type: 'line',
    data: data,
    options: options
});