$(function (){
    $('#sel1').on('change', function(event){
        if ($('#sel1').val().length == 1){
            var ses = localStorage.getItem('usingSes');
            localStorage.setItem('previous3', this.value);
            $.post('/SDproc/process', { idnext: this.value },
            function(data){
                $('#process_plot_spot').html( $(data).find('#process_plot_spot').html());
                $('#maxes').html( $(data).find('#maxes').html());
                $('#maxVal').html( $(data).find('#maxVal').html());
            })

            $.post('/SDproc/show_comment', { idnext: this.value, format: 1, ses: ses},
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

            $.post('/SDproc/process', { idList: jIds },
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
        $.post("/SDproc/make_name", {id: this},
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
    $.post('/SDproc/close_plots');
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
    $.post('/SDproc/add_entry', {process: 1},
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
                $.post('/SDproc/process', { idList: id , binWidth: binWidth},
                    function(data){
                        $('#process_plot_spot').html( $(data).find('#process_plot_spot').html());
                        $('#maxes').html( $(data).find('#maxes').html());
                        $('#maxVal').html( $(data).find('#maxVal').html());
                    })
                $('#ssModal').modal('hide');
            }
            else{
                $.post('/SDproc/process', { idnext: id , binWidth: binWidth},
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
    if (localStorage.getItem('previous3') === null){
        alert('No file loaded');
    }
    else{
        BootstrapDialog.show({
            title: 'Output Location?',
            message: 'Would you like to save the data locally, or to the server?',
            buttons: [{
                label: 'Save Locally',
                action: function(dialogItself){
                        if ($('#sel1').val().length == 1){
                                $('#output').val(1);
                                $('#idnext').val(localStorage.getItem('previous3'));
                                $('#output-form').attr('action', '/SDproc/process');
                                $('#output-form')[0].submit();
                                $('#idnext').val(None);
                            }
                        else{
                            var ids = []
                            $('#sel1 > option:selected').each(function(){
                                ids.push(this.value);
                            });
                            var jIds = JSON.stringify(ids);
                            $('#output').val(1);
                            $('#idList').val(jIds);
                            $('#output-form').attr('action', '/SDproc/process');
                            $('#output-form')[0].submit();
                            $('#idList').val(None);
                        }
                        dialogItself.close();
                    }
                }, {
                label: 'Save to Server',
                action: function(dialogItself){
                    alert("Not yet implemented")
                    /*$('#session').val(localStorage.getItem('previous'))
                    $('#outSingular').val(0)
                    $.post('/generateOutput', $('#meta-form').serialize(), function(data){
                        alert(data);
                    })
                    */
                    dialogItself.close();
                }
            }]
        });
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