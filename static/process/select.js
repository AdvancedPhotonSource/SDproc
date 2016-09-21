$(function (){
    $('#sel1').on('change', function(event){
        if ($('#sel1').val().length == 1){
            var ses = localStorage.getItem('usingSes');
            localStorage.setItem('previous3', this.value);
            $.post('/process', { idnext: this.value },
            function(data){
                $('#process_plot_spot').html( $(data).find('#process_plot_spot').html());
                $('#maxes').html( $(data).find('#maxes').html());
                $('#maxVal').html( $(data).find('#maxVal').html());
            })

            $.post('/show_comment', { idnext: this.value, format: 1, ses: ses},
            function(data){
                $('#comment').text(data);
            })
        }
        else{
            var ses = localStorage.getItem('usingSes');
            var ids = []
            $('#sel1 > option:selected').each(function(){
                ids.push(this.value);
            })
            var jIds = JSON.stringify(ids);
            localStorage.setItem('previous3', jIds);

            $.post('/process', { idList: jIds },
            function(data){
                $('#process_plot_spot').html( $(data).find('#process_plot_spot').html());
                $('#maxes').html( $(data).find('#maxes').html());
                $('#maxVal').html( $(data).find('#maxVal').html());
                $('#comment').text('');
            });
        }
    });
})


$(document).ready( function() {
    asynchOnLoad()
    $('#linearRad').prop("checked", true)
    $('#binWidth').attr('placeholder', 'Input width of bins');
    $('#binWidth').prop('disabled', true);
    $('#logbtn').prop('disabled', false);
    if (!localStorage.getItem('previous3') === null)
        localStorage.removeItem("previous3");
    if (localStorage.getItem('pltStat') === null)
        localStorage.setItem('pltStat', 1);
})

function asynchOnLoad(){
    var deferred = new $.Deferred(), completed = deferred.then(function(){
        $('#sel1 option').prop('selected', true);
        $('#sel1').trigger('change');
        return 1;
    });
    var saved_files = JSON.parse(localStorage.getItem('use_files'));
    $(saved_files).each(function(){
        var temp = this
        $.post("/make_name", {id: this},
        function(data){
        $('#sel1')
            .append($('<option></option')
            .text(data)
            .attr('value', temp))

        saved_files = removeID(temp.valueOf(), saved_files);
        if (saved_files.length == 0){
            deferred.resolve();
        }
        })
    })
    return deferred.promise()
}

function removeID(id, idArray){
    var result = $.grep(idArray, function(n, i){
        return (n !== id);
    })
    return result;
}


$(window).on('unload', function(){
    $.post('/close_plots');
    if (localStorage.getItem('previous3') === null)
    {
        return;
    }
    else
    {
        localStorage.removeItem('previous3');
    }
})

function log(){
    $.post('/add_entry', {process: 1},
    function(){
        $('#log_add').text('Added');
        $('#log_add').fadeOut(1000);
        $('#logbtn').prop('disabled', true);
    })
}

function saveSettings(){
    if ($('#binRad').is(':checked')){
        var id = JSON.parse(localStorage.getItem('previous3'));
        var binWidth = $('#binWidth').val();
        if ($.isNumeric(binWidth)){
            if (id.length > 1){
                var id = JSON.stringify(id);
                $.post('/process', { idList: id , binWidth: binWidth},
                    function(data){
                        $('#process_plot_spot').html( $(data).find('#process_plot_spot').html());
                        $('#maxes').html( $(data).find('#maxes').html());
                        $('#maxVal').html( $(data).find('#maxVal').html());
                    })
                $('#ssModal').modal('hide');
            }
            else{
                $.post('/process', { idnext: id , binWidth: binWidth},
                    function(data){
                        $('#process_plot_spot').html( $(data).find('#process_plot_spot').html());
                        $('#maxes').html( $(data).find('#maxes').html());
                        $('#maxVal').html( $(data).find('#maxVal').html());
                    })
                $('#ssModal').modal('hide');
            }
            $('#logbtn').prop('disabled', false);
        }
        else
        {
            alert('Please enter a bin width')
        }
    }
    else
    {
        $('#sel1').trigger('change');
    }
}


$(function (){
    $('input[type=radio][name=methodRad]').on('change', function(event){
        if ($('#binRad').is(':checked')){
            $('#binWidth').prop('disabled', false);
        }
        if ($('#linearRad').is(':checked')){
            $('#binWidth').prop('disabled', true);
        }
    })
})

function outputFile(){
    if (localStorage.getItem('previous2') === null){
        alert('No file loaded');
    }
    else{
        alert("Not yet implemented")
        /*if ($('#sel1').val().length == 1){
            $.post('/process', { idnext: this.value, output: 1}, function(data){
                alert(data);
            });
        }
        else{
            var ids = []
            $('#sel1 > option:selected').each(function(){
                ids.push(this.value);
            });
            var jIds = JSON.stringify(ids);
            $.post('/process', { idList: jIds, output: 1}, function(data){
                alert(data);
            });
        }
        */
    }
}