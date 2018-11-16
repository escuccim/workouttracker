var intensities = ['Very Low', 'Low', 'Moderate', 'High']

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
    } else if(chart == "totals"){
        display_summary(start_date, end_date);
    } else if(chart == "weight"){
        weight_chart(ctx, myChart, start_date, end_date);
    }
});

// the date filter buttons
$(".date-filter-button").on("click", function(e){
    e.preventDefault();
    value = $(this).data("val");

    // activate the appropriate button
    old_button = $(":button.btn-success");
    old_button.addClass("btn-secondary");
    old_button.removeClass("btn-success");
    $(".date-filter-button").removeClass("active");
    $(this).addClass("active");
    $(this).addClass("btn-success");
    $(this).removeClass("btn-secondary");

    start_date = new Date($("#end_date").val());

    // convert the date into a properly formatted string
    date_string = start_date.getFullYear() + "-"
    if(value == 7){
        start_date.setDate(start_date.getDate()-value);
        date_string += (start_date.getMonth()+1).toString().padStart(2, '0') + "-" + start_date.getDate().toString().padStart(2, '0');
    } else if(value == 365){
        date_string += '01-01';
    } else if(value == 30){
        date_string += (start_date.getMonth()+1).toString().padStart(2, '0') + "-01";
    }


    $("#start_date").val(date_string);
    $("#controller").trigger("submit");
});

$(document).on("click", ".expand_detail", function(e){
    id = $(this).data("val");
    url = "api/exercise_detail/" + id;

    // get the current content of the controller which indicates if it's open or closed
    current_html = $(this).html();
    // set them all to closed
    $(".expand_detail").html("+");
    // if this was closed set it to open
    if(current_html == "+"){
        $(this).html("-");
        data = get_chart_data(url);
        display_exercise_detail(id, data);
    }
    // else if it's open close it
    else {
         $("#detail_"+id).hide();
    }
});

function display_exercise_detail(id, data){
    $(".exercise_detail").hide();

    // check if the exercises are cardio or strength
    if(data[0].sets == 0 && data[0].reps == 0){
        cardio = true;

        total_duration = 0;
        total_calories = 0;
    } else {
        cardio = false;

        total_weight_moved = 0;
        total_sets = 0;
        total_reps = 0;
    }

    if(cardio){
        html = '<div class="col-md-10 col-md-offset-1"><table class="table table-striped"><thead><tr><th>Exercise</th><th class="text-right">Duration (min)</th><th class="text-right">Intensity</th><th class="text-right">Calories</th></tr></thead>';
    } else {
        html = '<div class="col-md-10 col-md-offset-1"><table class="table table-striped"><thead><tr><th>Exercise</th><th class="text-right">Sets</th><th class="text-right">Reps</th><th class="text-right">Weight</th><th class="text-right">Weight Moved</th></tr></thead>';
    }

    for(var i = 0; i < data.length; i++){
        html += '<tr><td>' + data[i].exercise + '</td>';
        if(data[i].sets != 0 && data[i].reps != 0){
            html += '<td class="text-right">' + data[i].sets + '</td>';
            html += '<td class="text-right">' + data[i].reps + '</td>';
            html += '<td class="text-right">' + data[i].weight + ' kg</td>';
            html += '<td class="text-right">' + (data[i].weight * data[i].reps * data[i].sets) + ' kg</td>';
            total_weight_moved += (data[i].weight * data[i].reps * data[i].sets);
            total_sets += data[i].sets;
            total_reps += data[i].reps;
        } else {
            html += '<td class="text-right">' + data[i].duration + '</td>';
            html += '<td class="text-right">' + intensities[data[i].intensity] + '</td>';
            html += '<td class="text-right">' + data[i].calories + '</td>';
            total_duration += data[i].duration;
            total_calories += data[i].calories;

        }
        html += '</tr>';
    }
    if(cardio){
        html += '<tr><td><b>Totals</b></td><td class="text-right">' + total_duration + '</td><td class="text-right">-</td><td class="text-right">' + total_calories + '</td></tr>';
    } else {
        html += '<tr><td><b>Totals</b></td><td class="text-right">' + total_sets + '</td><td class="text-right">' + total_reps + '</td><td class="text-right">-</td><td class="text-right">' + total_weight_moved + ' kg</td></tr>';
    }


    if(data.length == 0){
        html += '<div class="row"><div class="col-md-3"></div><div class="col-md-9">No details available</div></div>';
    }
    html += '</table></div>';
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
                    'rgba(255, 19, 120, 0.1)',
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                ],
                borderWidth: 2
            },{
                label: 'Minutes',
                data: data.minutes,
                label: 'min',
                yAxisID: 'B',
                backgroundColor: [
                    'rgba(120, 99, 255, 0.1)',
                ],
                borderColor: [
                    'rgba(132,99,255,1)',
                ],
                borderWidth: 2
            }]
        },
        options: {
            scales: {
              yAxes: [{
                id: 'A',
                type: 'linear',
                position: 'left',
                ticks: {
                    beginAtZero: true,
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Calories',
                }
              }, {
                id: 'B',
                type: 'linear',
                position: 'right',
                ticks: {
                    beginAtZero: true,
                },
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
            borderColor: "#000",
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

function weight_chart(ctx, myChart, start_date, end_date){
    url = "api/weight?foo";
    if(start_date != undefined){
        url += "&start=" + start_date;
    }
    if(end_date != undefined) {
        url += "&end=" + end_date;
    }

    try {
        ctx = clearChart();
    } catch(err) {
        console.log(err);
    }
    datasets = [{
                label: 'Weight',
                data: data.weights,
                yAxisID: 'A',
                backgroundColor: [
                    'rgba(255, 19, 120, 0.1)',
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                ],
                borderWidth: 2
            }];

     yAxes = [{
                id: 'A',
                type: 'linear',
                position: 'left',
                scaleLabel:{
                    display: true,
                    labelString: 'kg',
                }
              }];

    bodyfat_values_present = false;

    // create the body fat dataset if there is any data there
    for(var i=0; i<data.bodyfats.length;i++){
        if(data.bodyfats[i] != 0){
            bodyfat_values_present = true;
            break;
        }
    }

    if(bodyfat_values_present){
        bodyfat_dataset = {
                label: 'Body Fat %',
                data: data.bodyfats,
                yAxisID: 'B',
                backgroundColor: [
                    'rgba(120, 99, 255, 0.1)',
                ],
                borderColor: [
                    'rgba(132,99,255,1)',
                ],
                borderWidth: 2
            }
        datasets.push(bodyfat_dataset);
        yScale = {
                id: 'B',
                type: 'linear',
                position: 'right',
                scaleLabel:{
                    display: true,
                    labelString: '%',
                }
              };
        yAxes.push(yScale);
    }

    // create the datasets
    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: datasets
        },
        options: {
            scales: {
              yAxes: yAxes,
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

    html = '<div class="col-md-12"><div class="panel-group" id="accordion">';
    // create our new HTML
    for(var i=0; i<data.dates.length; i++){
        html += '<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title"><a data-toggle="collapse" href="#'+data.dates[i] + '"><div class="row"><div class="col-sm-2">' + data.dates[i] + '</div><div class="col-sm-2">';
        html += data.summaries.minutes[i] + ' mins </div><div class="col-md-2">';
        html += data.summaries.calories[i] + ' kCal </div></div></a></h4></div>';

        html += '<div id="'+data.dates[i] + '" class="panel-collapse collapse"><div class="panel-body"><div class="row"><div class="col-sm-9 col-sm-offset-1">';

        for(var j=0; j < data.workouts[data.dates[i]].length; j++){
            html += '<div class="row row_border">';
            html += '<div class="col-sm-1">' + data.workouts[data.dates[i]][j]['time'] + '</div>';
            html += '<div class="col-sm-2">' + data.workouts[data.dates[i]][j].group + '</div><div class="col-sm-2">'  +data.workouts[data.dates[i]][j].minutes + ' mins</div>';
            html += '<div class="col-sm-2">' +  data.workouts[data.dates[i]][j].calories + ' kCal</div>';
            html += '<div class="col-sm-1"><a data-val="' + data.workouts[data.dates[i]][j].id + '" id="expand_control'+data.workouts[data.dates[i]][j].id+'" class="expand_detail">+</a></div></div>';
            html += '<div class="row exercise_detail" style="display: none;" id="detail_' + data.workouts[data.dates[i]][j].id + '"></div>';
        }

        html += '</div></div></div>';
        html += '</div></div>';
    }

    html += '</div></div>';
    $("#details").html(html);
}

function display_summary(start_date, end_date){
    $("#charts").hide();
    $("#details").show();

    url = "api/breakdown?foo";
    if(start_date != undefined){
        url += "&start=" + start_date;
    }
    if(end_date != undefined) {
        url += "&end=" + end_date;
    }

    try {
        myChart.destroy();
    } catch(err) {
        // do nothing
    }

    data = get_chart_data(url);

    // create our table and headers
    html = '<div class="col-md-12"><table class="table table-striped">';
    html += '<thead><tr><th>Date</th>';
    totals = {}
    for(var i=0; i<data.groups.length;i++){
        html += '<th colspan="1" width="9%">' + data.groups[i] + '</th>';

        // while we are looping through groups also create a struct to hold the weekly totals
        totals[data.groups[i]] = 0;
    }
    totals['total'] = 0;

    html += '<th>Total</th></thead></tr>';

    // populate the table
    for(var i=0; i<data.dates.length; i++){
        html += '<tr><td>' + data.dates[i] + '</td>';
        day_total = 0;
        for(var j=0; j<data.groups.length;j++){
            group = data.groups[j];

            // increment our daily total
            day_total += data.data[group]['minutes'][i];
            totals['total'] += data.data[group]['minutes'][i];
            // increment the total per group
            totals[group] += data.data[group]['minutes'][i];

            if(data.data[group]['minutes'][i] != 0){
                html += '<td>' + data.data[group]['minutes'][i] + ' min</td>';
            } else {
                html += '<td> - </td>';
            }
        }
        html += '<td>' + day_total + ' min</td>';
        html += '</tr>';
    }

    html += '<tr class="total_row"><td><b>Total:</b></td>';
    // display the totals per group
    for(var i=0; i<data.groups.length;i++){
        html += '<td>' + totals[data.groups[i]] + ' min</td>';

        // while we are looping through groups also create a struct to hold the weekly totals
        totals[data.groups[i]] = 0;
    }
    html += '<td>' + totals['total'] + ' min</td>';

    html += '</tr></table></div>';
    $("#details").html(html);
}

var myChart = summary_chart(ctx, myChart);