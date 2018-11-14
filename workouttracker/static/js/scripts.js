$("#controller").on("submit", function(e){
    e.preventDefault();
    start_date = $("#start_date").val();
    end_date = $("#end_date").val();

    chart = $("#chart").val();

    $("#charts").show();
    $("#details").hide();

    if(chart == "summary"){
        summary_chart(ctx, myChart, start_date, end_date);
    } else if(chart == "breakdown"){
        breakdown_chart(ctx, myChart, start_date, end_date);
    } else if(chart == "details"){
        update_details(start_date, end_date);
    }
});

$(document).on("click", ".expand_detail", function(e){
    id = $(this).data("val");
    url = "api/exercise_detail/" + id;
    data = get_chart_data(url);
    display_exercise_detail(id, data);
});

function display_exercise_detail(id, data){
    $(".exercise_detail").hide();
    html = "<div class='col-md-12'>";
    for(var i = 0; i < data.length; i++){
        html += '<div class="row"><div class="col-md-3"></div><div class="col-md-2">' + data[i].exercise + '</div>';
        html += '<div class="col-md-2">' + data[i].sets + ' sets</div>';
        html += '<div class="col-md-2">' + data[i].reps + ' reps</div>';
        html += '<div class="col-md-2">' + data[i].weight + ' kg</div>';
        html += '</div>';
    }
    if(data.length == 0){
        html += '<div class="row"><div class="col-md-3"></div><div class="col-md-9">No details available</div></div>';
    }
    html += '</div>';
    $("#detail_"+id).html(html);
    $("#detail_"+id).show();
}

function clearChart() {
    var parent = document.getElementById('summary_chart');
    var child = document.getElementById('myChart');
    parent.removeChild(child);
    parent.innerHTML ='<canvas id="myChart" width="400" height="150"></canvas>';
    ctx = document.getElementById("myChart").getContext('2d');
    return ctx;
}

function get_chart_data(url){
    var data;
    $.ajax({
        async: false,
        url: url,
        type: 'get',
        success: function(result){
            data = result;
        },
        error: function(){
            console.log("Error!");
        }
        });
    return data;
}

var ctx = document.getElementById("myChart").getContext('2d');
var myChart;

function summary_chart(ctx, myChart, start_date, end_date){
    url = "api/chart_data?foo=bar";
    if(start_date != undefined){
        url += "&start=" + start_date;
    }
    if(end_date != undefined) {
        url += "&end=" + end_date;
    }
    data = get_chart_data(url);

    try {
        ctx = clearChart();
    } catch(err) {
        console.log(err);
    }

    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [{
                label: 'Calories',
                data: data.calories,
                label: 'kCal',
                yAxisID: 'A',
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                ],
                borderColor: [
                    'rgba(255,99,132,1)',
                ],
                borderWidth: 1
            },{
                label: 'Minutes',
                data: data.minutes,
                label: 'min',
                yAxisID: 'B',
                backgroundColor: [
                    'rgba(132, 99, 255, 0.2)',
                ],
                borderColor: [
                    'rgba(132,99,255,1)',
                ],
                borderWidth: 1
            }]
        },
        options: {
            scales: {
              yAxes: [{
                id: 'A',
                type: 'linear',
                position: 'left',
                scaleLabel: {
                    display: true,
                    labelString: 'Calories',
                }
              }, {
                id: 'B',
                type: 'linear',
                position: 'right',
               scaleLabel: {
                    display: true,
                    labelString: 'Minutes',
                }
              }]
            }
        }
    });

    return myChart;
}

function breakdown_chart(ctx, myChart, start_date, end_date){
    url = "api/breakdown?foo";
    if(start_date != undefined){
        url += "&start=" + start_date;
    }
    if(end_date != undefined) {
        url += "&end=" + end_date;
    }
    data = get_chart_data(url);

    try {
        ctx = clearChart();
    } catch(err) {
        console.log(err);
    }

    data = get_chart_data(url);

    try {
        myChart.destroy();
    } catch(err) {
        // do nothing
    }

    // create the datasets
    datasets = []
    for(var i=0; i < data.groups.length; i++){
       group = {
            label: data.groups[i],
            data: data.data[data.groups[i]].minutes,
            yAxisID: 'A',
            borderWidth: 1,
            backgroundColor: data.data[data.groups[i]].color,
       }
       datasets.push(group);
    }

    myChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.dates,
            datasets: datasets,
        },
        options: {
            scales: {
              yAxes: [{
                id: 'A',
                type: 'linear',
                position: 'left',
                stacked: true,
                scaleLabel:{
                    display: true,
                    labelString: 'Minutes',
                }
              }],
              xAxes: [{
                stacked: true,
              }]
            }
        }
    });

    return myChart;
}

function update_details(start_date, end_date){
    $("#charts").hide();
    $("#details").show();

    url = "api/details?foo";
    if(start_date != undefined){
        url += "&start=" + start_date;
    }
    if(end_date != undefined) {
        url += "&end=" + end_date;
    }
    data = get_chart_data(url);

    try {
        myChart.destroy();
    } catch(err) {
        // do nothing
    }

    data = get_chart_data(url);

    html = '<div class="col-md-12"><div class="panel-group" id="accordion">';
    // create our new HTML
    for(var i=0; i<data.dates.length; i++){
        html += '<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title"><a data-toggle="collapse" href="#'+data.dates[i] + '"><div class="row"><div class="col-md-2">' + data.dates[i] + '</div><div class="col-md-2">';
        html += data.summaries.minutes[i] + ' mins </div><div class="col-md-2">';
        html += data.summaries.calories[i] + ' kCal </div></div></a></h4></div>';

        html += '<div id="'+data.dates[i] + '" class="panel-collapse collapse"><div class="panel-body">';

        for(var j=0; j < data.workouts[data.dates[i]].length; j++){
            html += '<div class="row"><div class="col-md-2">' + data.workouts[data.dates[i]][j].start + '</div>';
            html += '<div class="col-md-1">' + data.workouts[data.dates[i]][j]['time'] + '</div>';
            html += '<div class="col-md-2">' + data.workouts[data.dates[i]][j].group + '</div><div class="col-md-2">'  +data.workouts[data.dates[i]][j].minutes + ' mins</div>';
            html += '<div class="col-md-2">' +  data.workouts[data.dates[i]][j].calories + ' kCal</div>';
            html += '<div class="col-md-1"><a data-val="' + data.workouts[data.dates[i]][j].id + '" class="expand_detail">+</a></div></div>';
            html += '<div class="row exercise_detail well" style="display: none;" id="detail_' + data.workouts[data.dates[i]][j].id + '"></div>';
        }

        html += '</div>';
        html += '</div></div>';
    }

    html += '</div></div>';
    $("#details").html(html);
}

var myChart = summary_chart(ctx, myChart);