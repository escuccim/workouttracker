var intensities = ['Very Low', 'Low', 'Moderate', 'High']

// populate the list of exercises performed
populate_exercise_list_2();

$("#controller").on("submit", function(e){
    e.preventDefault();
    start_date = $("#start_date").val();
    end_date = $("#end_date").val();

    populate_exercise_list_2();
    chart = $("#chart").val();

    $("#charts").show();
    $("#details").hide();
    $(".strength-drill-down").hide();
    $(".exercise_selection").hide();

    if(chart == "summary"){
        summary_chart(ctx, myChart, start_date, end_date);
    } else if(chart == "breakdown"){
        breakdown_chart(ctx, myChart, start_date, end_date);
        display_summary(start_date, end_date);
    } else if(chart == "details"){
        update_details(start_date, end_date);
    } else if(chart == "totals"){
        display_summary(start_date, end_date);
    } else if(chart == "weight"){
        weight_chart(ctx, myChart, start_date, end_date);
    } else if(chart == "strength"){
        $(".strength-drill-down").show();
        $("#strength-group").val("");
        strength_chart(ctx, myChart, start_date, end_date);
    } else if(chart == "by_exercise"){
        $(".exercise_selection").show();
        history_by_exercise_chart(ctx, myChart, start_date, end_date);
    }
});

$(document).on("click", "#exclude_rest_days", function(e){
    url = "api/chart_data?foo=bar";
    if(start_date != undefined){
        url += "&start=" + start_date;
    }
    if(end_date != undefined) {
        url += "&end=" + end_date;
    }
    data = get_chart_data(url);

    summary_text(start_date, end_date, data);
});

$(document).on("click", ".export_data", function(e){
    e.preventDefault();

    // show please wait thing
    $("#WaitModalBody").html("Please wait...");
    $("#waitModal").modal("show");

    url = "api/export_data"
    data = get_chart_data(url);

    if(data.prefix){
        html = '<a href="/media/' + data.prefix + '_weights.csv">Weight History</a><br/>';
        html += '<a href="/media/' + data.prefix + '_workout_summaries.csv">Workout Summaries</a><br/>';
        html += '<a href="/media/' + data.prefix + '_workout_details.csv">Workout Details</a><br/>';
    }

    $("#WaitModalBody").html(html);
});

$(document).on("change", "#select_exercise", function(e){
    by = $("#exercise_history_by").val();
    start_date = $("#start_date").val();
    end_date = $("#end_date").val();

    history_by_exercise_chart(ctx, myChart, start_date, end_date, by);
});

$(document).on("change", "#exercise_history_by", function(e){
    by = $(this).val();
    start_date = $("#start_date").val();
    end_date = $("#end_date").val();

    history_by_exercise_chart(ctx, myChart, start_date, end_date, by=by);
});

$(document).on("click", ".expand_strength", function(e){
    e.preventDefault();
    date = $(this).data("date");
    group = $(this).data("group");
    group_escaped = group.replace(/\s+/g, '-')

    url = "api/strength_detail?date=" + date + "&group=" + group;

    // toggle the thing open or closed
    current_html = $(this).html();
    if(current_html == '<i class="fas fa-plus"></i>'){
        data = get_chart_data(url);

        if(!data.error){
            $(this).html('<i class="fas fa-minus"></i>');

            html = show_strength_detail(data);


            $("#detail_" +  date + "_" + group_escaped).html(html);
            $("#detail_" +  date + "_" + group_escaped).show();
        }

    } else {
        $(this).html('<i class="fas fa-plus"></i>');
        $("#detail_" +  date + "_" + group_escaped).hide();
    }
});

$("#add_weight").on("click", function(e){
    e.preventDefault();

    weight_val = $("#weight").val();
    body_fat_val = $("#bodyfat").val();
    errors = false;
    if(weight_val == "" || isNaN(weight_val)){
        $("#weight_error").show();
        errors = true;
    } else {
        $("#weight_error").hide();
    }
    if(body_fat_val != ""){
        if(isNaN(body_fat_val)){
            $("#bodyfat_error").show();
            errors = true;
        } else {
            $("#bodyfat_error").hide();
        }
    } else {
        $("#bodyfat_error").hide();
    }

    // if there were no errors submit the form
    if(!errors){
        $("#weight_form").trigger("submit");
    }
});

$("#strength-group").on("change", function(e){
    group = $(this).val();
    by = $("#strength-unit-group").val();
    if(group != "" && group != "Upper Body"){
        start_date = $("#start_date").val();
        end_date = $("#end_date").val();
        strength_detail_chart(ctx, myChart, start_date, end_date, $(this).val(), by);
    } else {
        strength_chart(ctx, myChart, start_date, end_date, by);
    }
});

$(document).on("click", ".add_exercise", function(e){
    // get the id
    id = $(this).data("target");
    $("#target").val(id);

    // fill in the type
    $("#exercise_type").val($("#id_summary-type").val());

    // preselect the group in the group dropdown
    current_group = $("#id_summary-group").val();
    $("#main_group").val(current_group);

    // display the modal
    $("#exerciseModal").modal("show");
});

$("#add_exercise_form").on("submit", function(e){
    e.preventDefault();
    $("#loadingModal").modal("show");

    // get the target so we know which field to select the new value from
    target = $("#target").val();

    // serialize and submit the form
    $.ajax({
            url     : $(this).attr('action'),
            type    : $(this).attr('method'),
            dataType: 'json',
            data    : $(this).serialize(),
            success : function( data ) {
                 if(data.success == true){
                    // add the new exercise to the lists at the bottom
                    $(".exercise-list").append('<option value="' + data.exercise.id + '">'+ data.exercise.name + '</option>');

                    // select the new exercise
                    $("#" + target).val(data.exercise.id);

                    // close the modal
                    $("#exerciseModal").modal("hide");
                 }
                 $("#loadingModal").modal("hide");
            },
            error   : function( xhr, err ) {
                 console.log(err);
                 $("#loadingModal").modal("hide");
            }
        });
});

$(".add_workout").on("click", function(e){
    e.preventDefault();
    html = get_add_form();
    $("#ModalLabel").html("Add Workout");
    $("#ModalBody").html(html);
    $("#Modal").modal("show");

    // default the time to now
    $(".time_now").trigger("click");
});

$(".add_weight").on("click", function(e){
    e.preventDefault();
    data = get_chart_data("api/get_weight");
    if(data.weight){
        $("#last_weight").html(data.weight);
        $("#weight_units").html(data.units);
        $("#last_weight_date").html(data.date);
    }
    $("#weight_id").val();
    $("#previous_weight").show();
    $("#weightModal").modal("show");
});

function kgs_to_lbs(number){
    return Math.round(number * 100 * 2.2)  / 100;
}

$(document).on("change", "#strength-unit-group", function(e){
    e.preventDefault();
    by = $(this).val();
    group = $("#strength-group").val();
    if(group != ""){
        start_date = $("#start_date").val();
        end_date = $("#end_date").val();

        strength_detail_chart(ctx, myChart, start_date, end_date, group, by);
    } else {
        strength_chart(ctx, myChart, start_date, end_date, by);
    }
});

$(document).on("click", ".time_now", function(e){
    e.preventDefault();
    var d = new Date();
    now = d.getHours().toString().padStart(2, '0') + ':' + d.getMinutes().toString().padStart(2, '0') + ':' + d.getSeconds().toString().padStart(2, '0');
    $("#id_summary-time").val(now);
});

// change the add/edit form according to the type of workout selected
// also pre-select the group as appropriate
$(document).on("change", "#id_summary-type", function(e){
    val = $(this).val();

    if(val == ""){
        val = 0;
    }

    url = "api/exercise_by_type/" + val;
    data = get_chart_data(url);

    populate_exercise_list(data);

    $(".exercise_detail_form").show();
    if(val == 2){
        $(".strength_field").show();
        $(".walk_field").hide();
    } else if (val == 5){
        $(".strength_field").hide();
        $(".walk_field").show();
    } else if (val == 1){
        $(".strength_field").hide();
        $(".walk_field").hide();
        $("#id_summary-group").val(20);
    } else if ( val == 3) {
        $(".strength_field").hide();
        $(".walk_field").hide();
        $("#id_summary-group").val(21);
    }else {
        $(".strength_field").hide();
        $(".walk_field").hide();
    }
});

$(document).on("click", ".delete-workout", function(e){
    e.preventDefault();
    id = $(this).data("val");
    date = $(this).data("date");
    $("#delete-yes").data("val", id);
    $("#delete-yes").data("date", date);
    $("#delete-yes").data("what", "workout");
    $("#confirmDeleteModalText").html("Are you sure you want to delete this?")
    $("#confirmDeleteModal").modal("show");
});

$(document).on("click", ".delete_weight", function(e){
    e.preventDefault();
    id = $(this).data("val");
    $("#delete-yes").data("val", id);
    $("#delete-yes").data("what", "weight");
    $("#confirmDeleteModalText").html("Are you sure you want to delete this?")
    $("#confirmDeleteModal").modal("show");
});

$(document).on("click", ".edit_weight", function(e){
    e.preventDefault();
    id = $(this).data("val");
    weight = $(this).data("weight");
    bodyfat = $(this).data("bodyfat");
    date = $(this).data("date");
    $("#previous_weight").hide();
    $("#weightModal").modal("show");
    $("#weight").val(weight);
    $("#bodyfat").val(bodyfat);
    $("#date").val(date);
    $("#weight_id").val(id);
});

$(document).on("click", "#confirm-yes", function(e){
    e.preventDefault();
    $(".modal").modal("hide");
});

$(document).on("click", "#delete-yes", function(e){
    e.preventDefault();
    id = $(this).data("val");
    date = $(this).data("date");
    what = $(this).data("what");
    if(what == "workout"){
        url = "api/delete_workout/" + id;
    } else if(what == "weight"){
        url = "api/delete_weight/" + id;
    }

    data = get_chart_data(url);
    if(data.success == true){
        $("#controller").trigger("submit");
        $(".modal").modal("hide");
    } else {
        console.log("Error!");
    }
});

$(document).on("submit", "#profile_form", function(e){
    e.preventDefault();
    $("#loadingModal").modal("show");
    $.ajax({
            url     : $(this).attr('action'),
            type    : $(this).attr('method'),
            dataType: 'json',
            data    : $(this).serialize(),
            success : function( data ) {
                 if(data.success == true){
                    $("#Modal").modal("hide");
                    $("#controller").trigger("submit");
                 }
                 // else display errors
                 else {
                    // form validation should cover the errors, but we may need to address them here in the future?
                 }
                 $("#loadingModal").modal("hide");
            },
            error   : function( xhr, err ) {
                 console.log(err);
                 $("#loadingModal").modal("hide");
            }
        });
});

$(document).on("change", "#id_summary-group", function(e){
    type = $("#id_summary-type").val();
    group = $(this).val();
    url = "api/exercise_by_group/" + type + "/" + group;
    data = get_chart_data(url);

    populate_exercise_list(data);
});

function show_strength_detail(data){
    if(data.units == "imp"){
        label_str = "lbs";
        multiplier = 2.2;
    } else {
        label_str = "kg";
        multiplier = 1;
    }

    html = '<td></td><td colspan=7><table class="table table-striped"><thead><tr><th>Exercise</th><th class="text-right">Sets</th><th class="text-right">Reps</th><th class="text-right">Weight ('+label_str+')</th><th class="text-right">Weight Moved ('+label_str+')</th></tr></thead>';
    for(exercise in data.workouts){
        for(var i=0; i<data.workouts[exercise].length; i++){
            html += '<tr><td><a class="exercise_link" data-val="' + data.workouts[exercise][i].exercise_id + '">' + exercise + '</a></td>';
            html += '<td class="text-right">' + data.workouts[exercise][i].sets + '</td>';
            html += '<td class="text-right">' + data.workouts[exercise][i].reps + '</td>';
            html += '<td class="text-right">' + Math.round(data.workouts[exercise][i].weight * multiplier * 100) / 100 + '</td>';
            html += '<td class="text-right">' + Math.round(data.workouts[exercise][i].total_weight * multiplier * 100) / 100 + '</td>';
            html += '<td><a class="edit-workout" data-val="' + data.workouts[exercise][i].workout_id + '"><i class="fas fa-edit"></i></a></td>';
            html += '</tr>';
        }
    }
    html += '</table></td>';
    return html;
}

function populate_exercise_list(data){
    // get the values of the current selections, if any
    fields = $(".exercise-list")
    selections = []

    fields.each(function(index){
        selections.push($(this).val());
    });

    // remove the existing options
    $(".exercise-list option").remove();
    $(".exercise-list").append('<option value=""> ------ </option>');
    // add the new options back in
    for(var i = 0; i < data.length; i++){
        $(".exercise-list").append('<option value="' + data[i].id + '">'+ data[i].name + '</option>');
    }

    // loop through the fields again and reset the selections
    fields.each(function(index){
        selections.push($(this).val(selections[index]));
    });
}

$(document).on("click", ".edit_profile", function(e){
    html = get_profile_form();
    $("#ModalLabel").html("Edit Profile");
    $("#ModalBody").html(html);
    $("#Modal").modal("show");
});

$(document).on("click", "#delete-no", function(e){
    e.preventDefault();
    $("#confirmDeleteModal").modal("hide");
});

$(document).on("click", "#confirm-no", function(e){
    e.preventDefault();
    $("#confirmModal").modal("hide");
});

$(document).on("click", "#close_profile_form", function(e){
    e.preventDefault();

    $("#Modal").modal("hide");
});

$(document).on("click", "#close_form", function(e){
    e.preventDefault();

    // ask the user to save the form first?
    saved = $("#saved").val();

    if(saved == 0){
        $("#confirmModalText").html("Close without saving?")
        $("#confirmModal").modal("show");
    }
    else {
        // refresh the page
        $("#controller").trigger("submit");

        // expand the proper day?
        date = $(this).data("val");
        $("#"+date).removeClass("collapse");
        $("#Modal").modal("hide");
    }

});

$(document).on("submit", "#weight_form", function(e){
    e.preventDefault();
    $("#loadingModal").modal("show");
    $.ajax({
            url     : $(this).attr('action'),
            type    : $(this).attr('method'),
            dataType: 'json',
            data    : $(this).serialize(),
            success : function( data ) {
                 if(data.success == true){
                    $("#weightModal").modal("hide");
                    $("#controller").trigger("submit");
                 }
                 // else display errors
                 else {
                    // form validation should cover the errors, but we may need to address them here in the future?
                 }
                 $("#loadingModal").modal("hide");
            },
            error   : function( xhr, err ) {
                 console.log(err);
                 $("#loadingModal").modal("hide");
            }
        });
});

$(document).on("click", ".exercise_link", function(e){
    e.preventDefault();
    id = $(this).data("val");

    // switch to history by exercise report
    $("#chart").val("by_exercise");
    $("#charts").show();
    $("#details").hide();
    $(".strength-drill-down").hide();
    $(".exercise_selection").hide();

    by = $("#exercise_history_by").val();
    start_date = $("#start_date").val();
    end_date = $("#end_date").val();

    $(".exercise_selection").show();
    $("#select_exercise").val(id);

    history_by_exercise_chart(ctx, myChart, start_date, end_date);
});

$(document).on("submit", "#add_workout_form", function(e){
    e.preventDefault();
    $("#loadingModal").modal("show");
    $.ajax({
            url     : $(this).attr('action'),
            type    : $(this).attr('method'),
            dataType: 'json',
            data    : $(this).serialize(),
            success : function( data ) {
                 if(data.success == true){
                    id = data.id;
                    html = get_edit_form(id);
                    $("#ModalBody").html(html);
                    // update the field to indicate that the form has been saved
                    $("#saved").val(1);

                    // populate the list of exercises performed
                    populate_exercise_list_2();
                 }
                 // else display errors
                 else {
                    // form validation should cover the errors, but we may need to address them here in the future?
                 }
                 $("#loadingModal").modal("hide");
            },
            error   : function( xhr, err ) {
                 console.log(err);
                 $("#loadingModal").modal("hide");
            }
        });
});

$(document).on("submit", "#edit_workout_form", function(e){
    e.preventDefault();
    $("#loadingModal").modal("show");
    $.ajax({
            url     : $(this).attr('action'),
            type    : $(this).attr('method'),
            dataType: 'json',
            data    : $(this).serialize(),
            success : function( data ) {
                 if(data.success == true){
                    id = data.id;
                    html = get_edit_form(id);
                    $("#ModalBody").html(html);
                    // update the field to indicate that the form has been saved
                    $("#saved").val(1);

                    // populate the list of exercises performed
                    populate_exercise_list_2();
                 }
                 // else display errors
                 else {

                 }
                 $("#loadingModal").modal("hide");
            },
            error   : function( xhr, err ) {
                 console.log(err);
                 $("#loadingModal").modal("hide");
            }
        });
});

$(document).on("click", ".edit-workout", function(e){
    e.preventDefault();
    id = $(this).data("val");
    html = get_edit_form(id);
    $("#ModalLabel").html("Edit Workout");
    $("#ModalBody").html(html);
    $("#Modal").modal("show");
});

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function get_edit_form(id){
    url = "edit_workout/" + id;
    html = get_chart_data(url);
    return html;
}

function get_add_form(){
    url = "add_workout/";
    html = get_chart_data(url);
    return html;
}

function get_profile_form(){
    url = "profile/";
    html = get_chart_data(url);
    return html;
}

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

    end_date = $("#end_date").val();

    // if end date is blank fill it with today's date
    if(end_date == ""){
        end_date = new Date();
        end_date_str = end_date.getFullYear() + '-' + (end_date.getMonth()+1).toString().padStart(2, '0') + '-' + end_date.getDate().toString().padStart(2, '0');
        $("#end_date").val(end_date_str);
    }

    start_date = new Date($("#end_date").val());

    // convert the date into a properly formatted string
    year = start_date.getFullYear()
    month = start_date.getMonth() + 1
    day = start_date.getDate()
    date_string = start_date.getFullYear() + "-"
    if(value == 7){
        day -= 7;
        if(day < 1){
            day += 30;
            month -= 1;
        }
        if(month <= 0){
            month = 0;
            year -= 1;
        }
    } else if(value == 365){
        year -= 1;
    } else if(value == 30){
        month -= 1;
        if(month <= 0){
            month = 12;
            year -= 1;
        }
    }
    date_string = year + "-" + month.toString().padStart(2, '0') + "-" + day.toString().padStart(2, '0');
    $("#start_date").val(date_string);
    $("#controller").trigger("submit");
});

$(document).on("click", ".expand_detail", function(e){
    id = $(this).data("val");
    url = "api/exercise_detail/" + id;

    // get the current content of the controller which indicates if it's open or closed
    current_html = $(this).html();
    // set them all to closed
    $(".expand_detail").html('<i class="fas fa-plus"></i>');
    // if this was closed set it to open
    if(current_html == '<i class="fas fa-plus"></i>'){
        $(this).html('<i class="fas fa-minus"></i>');
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
    if(data.length == 0){
        html = '<div class="row" style="padding-top: 5px;"><div class="col-sm-10 col-sm-offset-1 well">No details available</div></div>';
        $("#detail_"+id).html(html);
        $("#detail_"+id).show();
        return;
    }
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
        html += '<tr><td><a class="exercise_link" data-val="' + data[i].exercise_id + '">' + data[i].exercise + '</a></td>';
        if(data[i].sets != 0 && data[i].reps != 0){
            if(data[i].user_units == "imp") {
                label_str = "lbs";
                multiplier = 2.2;
            } else {
                label_str = "kg";
                multiplier = 1;
            }
            html += '<td class="text-right">' + data[i].sets + '</td>';
            html += '<td class="text-right">' + data[i].reps + '</td>';
            html += '<td class="text-right">' + Math.round(data[i].weight * multiplier * 100) / 100 + ' ' + label_str + '</td>';
            html += '<td class="text-right">' + Math.round(data[i].weight * data[i].reps * data[i].sets * multiplier * 100) / 100 + ' ' + label_str + '</td>';
            total_weight_moved += (data[i].weight * data[i].reps * data[i].sets * multiplier);
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
        html += '<tr><td><b>Totals</b></td><td class="text-right">' + total_sets + '</td><td class="text-right">' + total_reps + '</td><td class="text-right">-</td><td class="text-right">' + Math.round(total_weight_moved * 100) / 100 + ' ' + label_str + '</td></tr>';
    }

    html += '</table></div>';
    $("#detail_"+id).html(html);
    $("#detail_"+id).show();
}

function clearChart() {
    var parent = document.getElementById('summary_chart');
    var child = document.getElementById('myChart');
    parent.removeChild(child);
    parent.innerHTML ='<canvas id="myChart" width="400" height="200"></canvas>';
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
        error: function(err){
            console.log(err);
        }
        });
    return data;
}

var ctx = document.getElementById("myChart").getContext('2d');
var myChart;

function add(a, b) {
    return a + b;
}

function summary_text(start_date, end_date, chart_data){
    exclude_rest_days = $("#exclude_rest_days").prop("checked");
    if(exclude_rest_days == true){
        erd_checked = 'checked="checked"';
    } else {
        erd_checked = '';
    }
    url = "api/chart_summary?foo=bar";
    if(start_date != undefined){
        url += "&start=" + start_date;
    }
    if(end_date != undefined) {
        url += "&end=" + end_date;
    }
    data = get_chart_data(url);
    html = '<div class="row"><div class="col-sm-12"><table class="table table-striped"><thead><tr><th>Item</th><th class="text-right">Total Time (min)</th><th class="text-right">Avg Time / Day (min)<th class="text-right">Total Calories</th><th class="text-right">Avg Calories / Day</th></tr></thead>';

    total_total_min = 0;
    total_total_kcal = 0;
    workouts = data.workouts
    exclude_rest_days = $("#exclude_rest_days").prop("checked");

    // if we are including rest days in the average use the total number of days in the period
    // else use only the days with activity
    if(exclude_rest_days == true){
        count = 0;
        for(var i = 0; i < chart_data.minutes.length; i++){
            if(chart_data.minutes[i] > 0){
                count++;
            }
        }
    } else {
        count = data.days;
    }

    for(group in workouts){
        total_kcal = workouts[group]['calories'].reduce(add, 0);
        total_min = workouts[group]['minutes'].reduce(add, 0);

        total_total_kcal += total_kcal;
        total_total_min += total_min;

        html += '<tr><td>' + group + '</td><td class="text-right">'+ numberWithCommas(total_min) +'</td><td class="text-right">'+ numberWithCommas((total_min / count).toFixed(1)) + '</td><td class="text-right">'+ numberWithCommas(total_kcal) +'</td><td class="text-right">'+ numberWithCommas((total_kcal / count).toFixed(1)) +'</td></tr>';
    }

    html += '<tr class="row_top_border"><td><b>Total:</b></td><td class="text-right">'+numberWithCommas(total_total_min)+'</td><td class="text-right">'+ numberWithCommas((total_total_min / count).toFixed(1)) + '</td><td class="text-right">'+ numberWithCommas(total_total_kcal) +'</td><td class="text-right">'+ numberWithCommas((total_total_kcal / count).toFixed(1)) + '</td></tr>';

    html += '</table></div><div class="col-sm-12 text-right"><input type="checkbox" name="exclude_rest_days" id="exclude_rest_days" '+ erd_checked+'> Exclude rest days</div></div>';

    $("#details").html(html);
    $("#details").show();
}

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
                label: 'Minutes',
                data: data.minutes,
                label: 'min',
                yAxisID: 'A',
                backgroundColor: [
                    'rgba(120, 99, 255, 0.1)',
                ],
                borderColor: [
                    'rgba(132,99,255,1)',
                ],
                borderWidth: 2
            },{
                label: 'Calories',
                data: data.calories,
                label: 'kCal',
                yAxisID: 'B',
                backgroundColor: [
                    'rgba(255, 19, 120, 0.1)',
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              yAxes: [ {
                id: 'A',
                type: 'linear',
                position: 'left',
                ticks: {
                    beginAtZero: true,
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Minutes',
                }
              },{
                id: 'B',
                type: 'linear',
                position: 'right',
                ticks: {
                    beginAtZero: true,
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Calories',
                }
              }]
            }
        }
    });

    summary_text(start_date, end_date, data);

    return myChart;
}

function convertHexToRGB(hex, alpha)
{
    var red = hex.substr(1, 2), green = hex.substr(3, 2), blue = hex.substr(5, 2), alpha = alpha;
    color = "rgba(" + parseInt(red, 16) + "," + parseInt(green, 16) + "," + parseInt(blue, 16) + "," + alpha + ")";
    return color;
}

function strength_chart(ctx, myChart, start_date, end_date, by="weight"){
    group = $("#strength-group").val();

    if(group == ""){
        url = "api/strength_data?foo=bar";
    } else {
        url = "api/strength_data?group="+group;
    }

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

    if(data.units == "imp"){
        label_str = "lbs";
    } else {
        label_str = "kg";
    }

    if(by == "weight"){
        datasets = []
        for(group in data.groups){
            use_group = false;

            // check that the data has some values in it
            for(var i = 0; i < data.workouts[group]['total_weight'].length; i++){
                if(data.workouts[group]['total_weight'][i] > 0){
                    use_group = true;
                    break;
                }
            }

            if(data.units == "imp"){
                data.workouts[group].total_weight = data.workouts[group].total_weight.map(kgs_to_lbs);
            }

            if(use_group){
                datasets.push({
                    label: group,
                    data: data.workouts[group].total_weight,
                    borderWidth: 1,
                    backgroundColor: convertHexToRGB(data.groups[group], 0.3),
                    borderColor: data.groups[group],
                });
            }
        };
        scales = {
              yAxes: [ {
                id: 'A',
                type: 'linear',
                position: 'left',
                ticks: {
                    beginAtZero: true,
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Total Weight Moved ('+label_str +')',
                }
              }]
            };
        callbacks = {
                    label: function(tooltipItems, data) {
                       return data.datasets[tooltipItems.datasetIndex].label +': ' + tooltipItems.yLabel + ' ' + label_str;
                    }
                };
    } else{
        datasets = []
        for(group in data.groups){
            use_group = false;

            // check that the data has some values in it
            for(var i = 0; i < data.workouts[group]['total_reps'].length; i++){
                if(data.workouts[group]['total_reps'][i] > 0){
                    use_group = true;
                    break;
                }
            }
            if(use_group){
                datasets.push({
                    label: group,
                    yAxisID: 'A',
                    data: data.workouts[group].total_reps,
                    borderWidth: 1,
                    backgroundColor: convertHexToRGB(data.groups[group], 0.3),
                    borderColor: data.groups[group],
                });
            }
        };

        scales = {
              yAxes: [ {
                id: 'A',
                type: 'linear',
                position: 'left',
                ticks: {
                    beginAtZero: true,
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Total Reps',
                }
              }]
            }
        callbacks = {
                    label: function(tooltipItems, data) {
                       return data.datasets[tooltipItems.datasetIndex].label +': ' + tooltipItems.yLabel + ' reps';
                    }
                };
    }


    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: datasets,
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            tooltips: {
                enabled: true,
                mode: 'single',
                callbacks: callbacks,
            },
            spanGaps: true,
            scales: scales,
        }
    });

    strength_detail(data);

    return myChart;
}

function history_by_exercise_chart(ctx, myChart, start_date, end_date, by="weight"){
    exercise = $("#select_exercise").val()

    url = "api/history_by_exercise/" + exercise + "?foo";
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

    if(data.units == "imp"){
        label_str = "lbs";
    } else {
        label_str = "kg";
    }

    if(by == "weight"){
        datasets = []
        datasets.push({
                    label: 'Total Weight Moved',
                    data: data.total_weights,
                    yAxisID: 'A',
                    borderWidth: 2,
                    backgroundColor: 'rgba(50, 120, 255, 0.2)',
                    borderColor: 'rgba(50, 120, 255, 0.5)',
                });

        datasets.push({
                    label: 'Average Weight',
                    data: data.avg_weights,
                    yAxisID: 'B',
                    borderWidth: 2,
                    backgroundColor: 'rgba(120, 120, 255, 0.3)',
                    borderColor: 'rgba(120, 120, 255, 0.5)',
                });

        datasets.push({
                    label: 'Max Weight',
                    data: data.max_weights,
                    yAxisID: 'B',
                    borderWidth: 2,
                    backgroundColor: 'rgba(175, 20, 50, 0.1)',
                    borderColor: 'rgba(225, 20, 50, 0.5)',
                });
        datasets.push({
                    label: 'One Rep Max',
                    data: data.one_rep_maxes,
                    yAxisID: 'B',
                    borderWidth: 2,
                    backgroundColor: 'rgba(20, 20, 20, 0.05)',
                    borderColor: 'rgba(20, 20, 20, 0.5)',
                });

        scales = {
              yAxes: [ {
                id: 'A',
                type: 'linear',
                position: 'right',
                ticks: {
                    beginAtZero: true,
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Total Weight Moved ('+label_str +')',
                }
              }, {
                id: 'B',
                type: 'linear',
                position: 'left',
                ticks: {
                    beginAtZero: true,
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Weight ('+label_str +')',
                }
              }]
            };
        callbacks = {
                    label: function(tooltipItems, data) {
                       return data.datasets[tooltipItems.datasetIndex].label +': ' + tooltipItems.yLabel + ' ' + label_str;
                    }
                };
    } else if(by == "time"){
        datasets = []
        datasets.push({
                    label: 'Time',
                    data: data.duration,
                    yAxisID: 'A',
                    borderWidth: 2,
                    backgroundColor: 'rgba(50, 120, 255, 0.2)',
                    borderColor: 'rgba(50, 120, 255, 0.5)',
                });

        scales = {
              yAxes: [ {
                id: 'A',
                type: 'linear',
                position: 'right',
                ticks: {
                    beginAtZero: true,
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Time (min)',
                }
              }]
            };
        callbacks = {
                    label: function(tooltipItems, data) {
                       return data.datasets[tooltipItems.datasetIndex].label +': ' + tooltipItems.yLabel + ' ' + label_str;
                    }
                };
    } else{
        datasets = []
         datasets.push({
                    label: 'Total Sets',
                    data: data.sets,
                    yAxisID: 'A',
                    borderWidth: 2,
                    backgroundColor: 'rgba(50, 120, 255, 0.2)',
                    borderColor: 'rgba(50, 120, 255, 0.5)',
                });

        datasets.push({
                    label: 'Total Reps',
                    data: data.reps,
                    yAxisID: 'B',
                    borderWidth: 2,
                    backgroundColor: 'rgba(175, 20, 50, 0.1)',
                    borderColor: 'rgba(225, 20, 50, 0.5)',
                });

        scales = {
              yAxes: [ {
                id: 'A',
                type: 'linear',
                position: 'left',
                ticks: {
                    beginAtZero: true,
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Total Sets',
                }
              },  {
                id: 'B',
                type: 'linear',
                position: 'right',
                ticks: {
                    beginAtZero: true,
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Total Reps',
                }
              }]
            }
        callbacks = {
                    label: function(tooltipItems, data) {
                       return data.datasets[tooltipItems.datasetIndex].label +': ' + tooltipItems.yLabel;
                    }
                };
    }

    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: datasets,
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            tooltips: {
                enabled: true,
                mode: 'single',
                callbacks: callbacks,
            },
            spanGaps: true,
            scales: scales,
        }
    });

//    strength_detail(data);

    return myChart;
}

function strength_detail_chart(ctx, myChart, start_date, end_date, group, by="weight"){
    url = "api/strength_data?group=" + group;
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

    if(by == "weight"){
        datasets = [{
                label: 'Average Weight',
                data: data.workouts[group]['avg_weight'],
                yAxisID: 'A',
                backgroundColor: convertHexToRGB(data.groups[group], 0.3),
                borderColor: data.groups[group],
                borderWidth: 1,
            },
            {
                label: 'Max Weight',
                data: data.workouts[group]['max_weight'],
                yAxisID: 'A',
                borderWidth: 1,
                backgroundColor: 'rgba(50,120,120, 0.3)',
                borderColor: 'rgba(50,120,120, 1.0)',
            },
            {
                label: 'Total Weight',
                data: data.workouts[group]['total_weight'],
                yAxisID: 'B',
                borderWidth: 1,
                backgroundColor: 'rgba(50,225,150, 0.3)',
                borderColor: 'rgba(50,225,150, 1.0)',
            }];

        scales = {
              yAxes: [ {
                id: 'A',
                type: 'linear',
                position: 'left',
                ticks: {
                    beginAtZero: true,
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Single Rep Weight (kg)',
                }
              },{
                id: 'B',
                type: 'linear',
                position: 'right',
                ticks: {
                    beginAtZero: true,
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Total Weight Moved (kg)',
                }
              }]
            }  ;
    } else {
        datasets = [{
                label: 'Total Sets',
                data: data.workouts[group]['total_sets'],
                yAxisID: 'A',
                backgroundColor: convertHexToRGB(data.groups[group], 0.3),
                borderColor: data.groups[group],
                borderWidth: 1,
            },
            {
                label: 'Total Reps',
                data: data.workouts[group]['total_reps'],
                yAxisID: 'B',
                borderWidth: 1,
                backgroundColor: 'rgba(50,175,120, 0.3)',
                borderColor: 'rgba(50,120,175, 1.0)',
            },
           ];
         scales = {
              yAxes: [ {
                id: 'A',
                type: 'linear',
                position: 'left',
                ticks: {
                    beginAtZero: true,
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Sets',
                }
              },{
                id: 'B',
                type: 'linear',
                position: 'right',
                ticks: {
                    beginAtZero: true,
                },
                scaleLabel: {
                    display: true,
                    labelString: 'Reps',
                }
              }]
            }  ;
    }

    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: datasets,
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            spanGaps: true,
            tooltips: {
                enabled: true,
                mode: 'single',
                callbacks: {
                    label: function(tooltipItems, data) {
                       return data.datasets[tooltipItems.datasetIndex].label +': ' + tooltipItems.yLabel + ' kg';
                    }
                }
            },
            scales: scales,
        }
    });

    strength_detail(data);

    return myChart;
}

function strength_detail(data){
    if(data.units == "imp"){
        label_str = "lbs";
        multiplier = 2.2;
    } else {
        label_str = "kg";
        multiplier = 1;
    }

    html = '<div class="col-sm-12 table-responsive"><table class="table"><thead><tr><th>Date</th><th>Group</th><th class="text-right">Sets</th><th class="text-right">Reps</th><th class="text-right">Total Weight ('+label_str+')</th><th class="text-right">Max Weight ('+label_str+')</th><th class="text-right">Avg Weight ('+label_str+')</th><th></th></tr></thead>';
    dates = data.dates.reverse();
    for(var i=0; i < dates.length; i++){
        if(data.tabular[dates[i]]){
            for(group in data.tabular[dates[i]]){
                group_escaped = group.replace(/\s+/g, '-');
                html += '<tr style="background-color: '+ convertHexToRGB(data.groups[group], 0.35) +';"><td>' + dates[i] + '</td>';
                html += '<td >' + group + '</td>';
                html += '<td class="text-right">' + data.tabular[data.dates[i]][group]['total_sets'] + '</td>';
                html += '<td class="text-right">' + data.tabular[data.dates[i]][group]['total_reps'] + '</td>';
                html += '<td class="text-right">' + numberWithCommas(Math.round(data.tabular[data.dates[i]][group]['total_weight'] * multiplier * 100) / 100) + '</td>';
                html += '<td class="text-right">' + numberWithCommas(Math.round(data.tabular[data.dates[i]][group]['max_weight'] * multiplier * 100) / 100) + '</td>';
                html += '<td class="text-right">' + numberWithCommas(Math.round(data.tabular[data.dates[i]][group]['avg_weight'] * multiplier * 100) / 100) + '</td>';
                html += '<td class="text-right"><a class="expand_strength" id="' +  dates[i] + '_' + group_escaped + '" data-date="' + dates[i] + '" data-group="' + group + '"><i class="fas fa-plus"></i></a></td>';
                html += '</tr>';

                // add the blank row to contain the details
                html += '<tr id="detail_' +  dates[i] + '_' + group_escaped + '" style="display: none;"></tr>';
            }
        }
    }

    html += '</table></div>';

    $("#details").html(html);
    $("#details").show();
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
            responsive: true,
            maintainAspectRatio: false,
            tooltips: {
                enabled: true,
                mode: 'single',
                callbacks: {
                    label: function(tooltipItems, data) {
                       return data.datasets[tooltipItems.datasetIndex].label +': ' + tooltipItems.yLabel + ' min';
                    }
                }
            },
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
    data = get_chart_data(url);

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
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              yAxes: yAxes,
            },
            spanGaps: true,
        }
    });
    weight_history(data);

    return myChart;
}

function weight_history(data){
    html = '<div class="col-sm-6 col-sm-offset-3"><table class="table table-striped"><thead><tr><th>Date</th><th>Weight</th><th>Body Fat</th><th colspan="2"></th></tr></thead>';

    for(var i = 0; i < data.dates.length; i++){
        if(data.weights[i] != null | data.bodyfats[i] != null){
            html += '<tr>';
            html += '<td>' + data.dates[i] + '</td>';
            if(data.weights[i] != null){
                html += '<td>' + data.weights[i] + ' ' + data.units[i] + '</td>';
            } else {
                html += '<td></td>';
            }
            if(data.bodyfats[i] != null){
                html += '<td>' + data.bodyfats[i] + ' %</td>';
            } else {
                html += '<td></td>';piu
            }

            html += '<td><a class="edit_weight" data-date="' + data.dates[i] + '" data-weight="' + data.weights[i] + '" data-bodyfat="' + data.bodyfats[i] + '" data-val="' + data.ids[i] + '"><i class="fas fa-edit"></i></a></td>';
            html += '<td><a class="delete_weight" data-val="' + data.ids[i] + '"><i class="fas fa-trash"></i></a></td>';
            html += '</tr>';
        }
    }
    html += '</div>';

    $("#details").html(html);
    $("#details").show();
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
        html += '<div class="panel panel-default"><div class="panel-heading"><h4 class="panel-title"><a data-toggle="collapse" href="#'+data.dates[i] + '"><div class="row"><div class="col-xs-5 col-md-2">' + data.dates[i] + '</div><div class="col-xs-3 col-md-2">';
        html += data.summaries.minutes[i] + ' mins </div><div class="col-xs-3 col-md-3">';
        html += data.summaries.calories[i] + ' kCal </div></div></a></h4>';
        html += '</div>';

        html += '<div id="'+data.dates[i] + '" class="panel-collapse collapse"><div class="panel-body"><div class="row"><div class="col-sm-9 col-sm-offset-1">';

        for(var j=0; j < data.workouts[data.dates[i]].length; j++){
            html += '<div class="row row_border">';
            html += '<div class="col-sm-1">' + data.workouts[data.dates[i]][j]['time'] + '</div>';
            html += '<div class="col-sm-2">' + data.workouts[data.dates[i]][j].group + '</div><div class="col-sm-2">'  +data.workouts[data.dates[i]][j].minutes + ' mins</div>';
            html += '<div class="col-sm-2">' +  data.workouts[data.dates[i]][j].calories + ' kCal</div>';
            html += '<div class="col-sm-1"><a class="edit-workout" data-val="' + data.workouts[data.dates[i]][j].id + '"><i class="fas fa-edit"></i></a></div>';
            html += '<div class="col-sm-1"><a data-val="' + data.workouts[data.dates[i]][j].id + '" data-date="' + data.dates[i] + '" class="delete-workout"><i class="fas fa-trash-alt"></i></a></div>';
            html += '<div class="col-sm-1"><a data-val="' + data.workouts[data.dates[i]][j].id + '" id="expand_control'+data.workouts[data.dates[i]][j].id+'" class="expand_detail"><i class="fas fa-plus"></i></a></div></div>';
            html += '<div class="row exercise_detail" style="display: none;" id="detail_' + data.workouts[data.dates[i]][j].id + '"></div>';
        }

        html += '</div></div></div>';
        html += '</div></div>';
    }

    html += '</div></div>';
    $("#details").html(html);
}

function display_summary(start_date, end_date){
//    $("#charts").hide();
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
    html = '<div class="col-md-12 table-responsive"><table class="table table-striped w-auto">';
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
                html += '<td>' + data.data[group]['minutes'][i] + '</td>';
            } else {
                html += '<td> - </td>';
            }
        }
        html += '<td>' + day_total + '</td>';
        html += '</tr>';
    }

    html += '<tr class="total_row"><td><b>Total:</b></td>';
    // display the totals per group
    for(var i=0; i<data.groups.length;i++){
        html += '<td>' + totals[data.groups[i]] + '</td>';

        // while we are looping through groups also create a struct to hold the weekly totals
        totals[data.groups[i]] = 0;
    }
    html += '<td>' + numberWithCommas(totals['total']) + '</td>';

    html += '</tr></table></div>';
    $("#details").html(html);
}

function convert_weights(){
    fields = $(".weight_field")

    fields.each(function(index){
        kgs = $(this).val();
        $(this).val(Math.round(kgs * 2.2 * 100)/ 100);
    });
}

function populate_exercise_list_2(){
    start_date = $("#start_date").val();
    end_date = $("#end_date").val();

    url = "api/exercises_performed?start=" + start_date + "&end=" + end_date;
    data = get_chart_data(url);

    // get the current selection
    val = $("#select_exercise").val();

    // empty the list
    $("#select_exercise").empty();

    // repopulate the list
    for(var i=0; i<data.exercises.length; i++){
        $("#select_exercise").append('<option value="' + data.exercises[i][1] + '">'+ data.exercises[i][0] + '</option>');
    }

    if(val != null)
        $("#select_exercise").val(val);
}

var myChart = summary_chart(ctx, myChart);