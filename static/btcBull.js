
document.addEventListener('DOMContentLoaded', function() {

	// On content load, set end date to yesterday
    var endDateInput = document.getElementById("endDateInput");
	var date = new Date();
	date.setDate(date.getDate() - 1);
	endDateInput.value = date.toISOString().substr(0, 10);

	goBtnClick(true);

	document.getElementById("dateAlert").style.display = "none";

	var today = new Date();
	var dd = today.getDate();
	var mm = today.getMonth()+1; //January is 0!
	var yyyy = today.getFullYear();
	 if(dd<10){
	        dd='0'+dd
	    } 
	    if(mm<10){
	        mm='0'+mm
	    } 

	today = yyyy+'-'+mm+'-'+dd;

	document.getElementById("startDateInput").setAttribute("max", today);
	document.getElementById("endDateInput").setAttribute("max", today);

}, false);

document.getElementById("goBtn").onclick = function() {goBtnClick(false)};

function goBtnClick(first) {

	var startDate = document.getElementById("startDateInput").value;
	var endDate = document.getElementById("endDateInput").value;
	var btcVal = parseFloat(document.getElementById("btcWeight").value);
	var spVal = parseFloat(document.getElementById("sp500Weight").value);

	var strtDt = new Date(startDate);
	var endDt = new Date(endDate);	

	if (strtDt > endDt){
		document.getElementById("dateAlert").style.display = "block";
		console.log("Oh Shit");
		return 
	}

	document.getElementById("dateAlert").style.display = "none";


	var btcWeight = btcVal/(btcVal + spVal);
	var spWeight = spVal/(btcVal + spVal);

	
	document.getElementById("sp500Weight").value = spWeight;
	document.getElementById("btcWeight").value = btcWeight;

	var url = "https://bitcoinbull.herokuapp.com/getChartVals?start=" + startDate + "&end=" + endDate + "&btc_weight=" + btcWeight + "&sp_weight=" + spWeight;
	
	async function callChartDataAPI() 
	{
	  let response = await fetch(url);
	  let data = await response.json();
	  return data;
	}

	function drawGraphFirst(data) {


		returns = JSON.parse(data["Returns"]);
		dates = JSON.parse(data["Dates"]);

		$("#returnCard").html((parseFloat(returns[returns.length-1])*100).toFixed(3)+"%");
		$("#alphaCard").html(data["Alpha"].toFixed(3));
		$("#betaCard").html(data["Beta"].toFixed(3));
		$("#sharpeCard").html(data["Sharpe"].toFixed(3));

		maxVal = 0 ;
		minVal = 10000000000;
		var vals = [];
	    for (var i = 0; i < dates.length; i++) {
	    	if (returns[i] > maxVal) {
	    		maxVal = returns[i];
	    	}

	    	if (returns[i] < minVal) {
	    		minVal = returns[i];
	    	}
	      	var innerArr = [dates[i], returns[i]];
	      	vals.push(innerArr);
	    }

	    var options = {
	      chart: {
	        type: 'area',
	        stacked: false,
	        zoom: {
	          type: 'x',
	          enabled: true
	        },
	        toolbar: {
	          autoSelected: 'zoom'
	        },
	        height: 550
	      },
	      dataLabels: {
	        enabled: false
	      },
	      series: [{
	        name: 'BTC/S&P 500 Return',
	        data: vals
	      }],
	      markers: {
	        size: 0,
	      },
	      title: {
	        text: 'BTC/S&P 500 Portfolio',
	        align: 'center'
	      },
	      fill: {
	        type: 'gradient',
	        gradient: {
	          shadeIntensity: 1,
	          inverseColors: false,
	          opacityFrom: 0.9,
	          opacityTo: 0.1,
	          stops: [0, 90, 100]
	        },
	      },
	      yaxis: {
	        min: minVal-0.5,
	        max: maxVal+0.5,
	        labels: {
	          formatter: function (val) {
	            return (val).toFixed(3);
	          },
	        },
	        title: {
	          text: 'Return'
	        },
	      },
	      xaxis: {
	        type: 'datetime',
	        title: {
	          text: 'Time'
	        },
	      },

	      tooltip: {
	        shared: false,
	        y: {
	          formatter: function (val) {
	            return (val).toFixed(3);
	          }
	        }
	      }
	    }




	    if (!document.querySelector("#line-chart").hasChildNodes()) {

		    var chart = new ApexCharts(
		      document.querySelector("#line-chart"),
		      options
		    );

		    chart.render();
		}

		else {

			var graph = document.querySelector("#line-chart");

			while (graph.lastChild) {
				graph.removeChild(graph.lastChild);
			} 

			var chart = new ApexCharts(
		      document.querySelector("#line-chart"),
		      options
		    );

		    chart.render();
		}
	  
				
	}


	callChartDataAPI().then(data => drawGraphFirst(data));

		

}






