$(document).ready( function() {
    if (jQuery.trim($('#process_plot').text()) == "No DAT selected"){
        alert('Please select or generate a DAT file');
    }
    if ($('#flatRad').is(':checked')){
        $('#flatVal').prop('disabled', false);
        $('#leftX').prop('disabled', true);
        $('#leftY').prop('disabled', true);
        $('#rightX').prop('disabled', true);
        $('#rightY').prop('disabled', true);
    }
    if ($('#linearRad').is(':checked')){
        $('#flatVal').prop('disabled', true);
        $('#leftX').prop('disabled', false);
        $('#leftY').prop('disabled', false);
        $('#rightX').prop('disabled', false);
        $('#rightY').prop('disabled', false);
    }
    if ($('#avRad').is(':checked')){
        $('#leftX').prop('disabled', true);
        $('#leftY').prop('disabled', true);
        $('#rightX').prop('disabled', true);
        $('#rightY').prop('disabled', true);
        $('#flatVal').prop('disabled', true);
    }
})

function averageRange(){
    var leftIn = $('#leftIn').val()
    var rightIn = $('#rightIn').val()
    $.post('/averageDAT', {right: rightIn, left: leftIn}, function(data){
        $('#process_plot').html(data)
    })
}

function remBackground(){
    if ($('#flatRad').is(':checked')){
        var flatVal = $('#flatVal').val()
        $.post('/remBackDAT', {flatVal: flatVal}, function(data){
            $('#process_plot').html($(data).find('#process_plot').html())
        })
    }
    else if ($('#linearRad').is(':checked')){
        var lX = $('#leftX').val()
        var lY = $('#leftY').val()
        var rX = $('#rightX').val()
        var rY = $('#rightY').val()
        $.post('/remBackDAT', {leftX : lX, leftY : lY, rightX: rX, rightY: rY}, function(data){
            $('#process_plot').html($(data).find('#process_plot').html())
        })
    }
    else if ($('#avRad').is(':checked')){
        alert('Should I have users chose a line or connect the lines and use that?')
    }
}

function resetPlot(){
    $.post('/resetDAT', function(data){
        $('#process_plot').html($(data).find('#process_plot').html())
    })
}

$(function (){
    $('input[type=radio][name=methodRad]').on('change', function(event){
        if ($('#flatRad').is(':checked')){
            $('#flatVal').prop('disabled', false);
            $('#leftX').prop('disabled', true);
            $('#leftY').prop('disabled', true);
            $('#rightX').prop('disabled', true);
            $('#rightY').prop('disabled', true);
        }
        if ($('#linearRad').is(':checked')){
            $('#flatVal').prop('disabled', true);
            $('#leftX').prop('disabled', false);
            $('#leftY').prop('disabled', false);
            $('#rightX').prop('disabled', false);
            $('#rightY').prop('disabled', false);
        }
        if ($('#avRad').is(':checked')){
            $('#leftX').prop('disabled', true);
            $('#leftY').prop('disabled', true);
            $('#rightX').prop('disabled', true);
            $('#rightY').prop('disabled', true);
            $('#flatVal').prop('disabled', true);
        }
    })
})

function outputFile(){
    BootstrapDialog.show({
        title: 'Save Options',
        message: function(dialog){
            if (jQuery.trim($('#sesName').text()) == 'None'){
                var $content = $('<input type="text" id="DATname" placeholder="Name of DAT file">')
            }
            else{
                var temp = jQuery.trim($('#sesName').text())
                var $content = $('<input type="text" id="DATname">')
                $content[0].value = temp
            }
            return $content
        },
        buttons: [{
            label: 'Save to Server',
            action: function(dialogItself){
                $.post('/generateOutput', {outType: 7, datFName: $('#DATname').val()}, function(){
                    alert('Saved')
                })
            }
        }, {
            label: 'Save Locally',
            action: function(dialogItself){
                $('#output-form').attr('action', '/SDproc/generateOutput')
                $('#outType').val(6);
                $('#datFName').val($('#DATname').val())
                $('#output-form')[0].submit();
            }
        }]
    })
}