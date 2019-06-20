$x(document).ready( function() {
    if (jQuery.trim($x('#process_plot').text()) == "No DAT selected"){
        alert('Please select or generate a DAT file');
    }
    else{
        $x.post('/SDproc/show_comment', {format: 3}, function(data){
            $x('#comment').val(data)
        })
    }
    if ($x('#flatRad').is(':checked')){
        $x('#flatVal').prop('disabled', false);
        $x('#leftX').prop('disabled', true);
        $x('#leftY').prop('disabled', true);
        $x('#rightX').prop('disabled', true);
        $x('#rightY').prop('disabled', true);
    }
    if ($x('#linearRad').is(':checked')){
        $x('#flatVal').prop('disabled', true);
        $x('#leftX').prop('disabled', false);
        $x('#leftY').prop('disabled', false);
        $x('#rightX').prop('disabled', false);
        $x('#rightY').prop('disabled', false);
    }
    if ($x('#avRad').is(':checked')){
        $x('#leftX').prop('disabled', true);
        $x('#leftY').prop('disabled', true);
        $x('#rightX').prop('disabled', true);
        $x('#rightY').prop('disabled', true);
        $x('#flatVal').prop('disabled', true);
    }
    $x('#calcLeftYLabel').hide()
    $x('#calcRightYLabel').hide()

    if(localStorage.getItem("usingDAT") == 1){
        $x("#navData").addClass('disabled');
        $x('#navProcess').addClass('disabled');
    }
    else{
        $x('#navData').removeClass('disabled');
        $x('#navProcess').removeClass('disabled');
    }
})

function showLine(){
    if ($x('#flatRad').is(':checked')){
        var flatVal = $x('#flatVal').val()
        $x.post('/SDproc/showLineDAT', {flatVal: flatVal}, function(data){
            $x('#process_plot').html($x(data).find('#process_plot').html())
        })
    }
    else if ($x('#calcRad').is(':checked')){
        var leftIn = $x('#leftIn').val()
        var rightIn = $x('#rightIn').val()
        $x.post('/SDproc/showLineDAT', {right: rightIn, left: leftIn}, function(data){
            var data = JSON.parse(data)
            $x('#process_plot').html(data[0])
            localStorage.setItem('averageLin', data[1])
            $x('#calcLeftY').text('Left Y: ');
            $x('#calcRightY').text('Right Y: ');
        })
    }
    else if ($x('givRad').is(':checked')){
        var lX = $x('#leftX').val()
        var lY = $x('#leftY').val()
        var rX = $x('#rightX').val()
        var rY = $x('#rightY').val()
    }
    else{
        alert('Please select an option to show.');
    }
}

function remBackground(show){
    if ($x('#flatRad').is(':checked')){
        var flatVal = $x('#flatVal').val()
        $x.post('/SDproc/remBackDAT', {show: show, flatVal: flatVal}, function(data){
            if (show == 0){
                $x('#process_plot').html($x(data).find('#process_plot').html())
            }
            else{
                $x('#process_plot').html($x(data))
            }
        })
    }
    else if ($x('#givRad').is(':checked')){
        var lX = $x('#leftX').val()
        var lY = $x('#leftY').val()
        var rX = $x('#rightX').val()
        var rY = $x('#rightY').val()
        $x.post('/SDproc/remBackDAT', {show: show, leftX : lX, leftY : lY, rightX: rX, rightY: rY}, function(data){
            if (show == 0){
                $x('#process_plot').html($x(data).find('#process_plot').html())
            }
            else{
                $x('#process_plot').html($x(data))
            }
        })
    }
    else if ($x('#calcRad').is(':checked')){
        var leftIn = $x('#calcLeftX').val()
        var rightIn = $x('#calcRightX').val()
        $x.post('/SDproc/remBackDAT', {show: show, leftIn: leftIn, rightIn: rightIn}, function(data){
        if (show == 0){
            $x('#process_plot').html($x(data).find('#process_plot').html())
        }
        else{
            var data = JSON.parse(data)
            $x('#process_plot').html($x(data[0]))
            $x('#calcLeftY').text(data[1])
            $x('#calcRightY').text(data[2])
            $x('#calcLeftYLabel').show()
            $x('#calcRightYLabel').show()
        }
        })
    }
}

function resetPlot(){
    $x.post('/SDproc/resetDAT', function(data){
        $x('#process_plot').html($x(data).find('#process_plot').html())
    })
}

$x(function (){
    $x('input[type=radio][name=methodRad]').on('change', function(event){
        if ($x('#flatRad').is(':checked')){
            $x('#flatVal').prop('disabled', false);
            $x('#leftX').prop('disabled', true);
            $x('#leftY').prop('disabled', true);
            $x('#rightX').prop('disabled', true);
            $x('#rightY').prop('disabled', true);
            $x('#calcLeftX').prop('disabled', true);
            $x('#calcRightX').prop('disabled', true);
        }
        if ($x('#calcRad').is(':checked')){
            $x('#flatVal').prop('disabled', true);
            $x('#calcLeftX').prop('disabled', false);
            $x('#calcRightX').prop('disabled', false);
            $x('#leftX').prop('disabled', true);
            $x('#leftY').prop('disabled', true);
            $x('#rightX').prop('disabled', true);
            $x('#rightY').prop('disabled', true);
        }
        if ($x('#givRad').is(':checked')){
            $x('#leftX').prop('disabled', false);
            $x('#leftY').prop('disabled', false);
            $x('#rightX').prop('disabled', false);
            $x('#rightY').prop('disabled', false);
            $x('#flatVal').prop('disabled', true);
            $x('#calcLeftX').prop('disabled', true);
            $x('#calcRightX').prop('disabled', true);
        }
    })
})

function outputFile(){
    BootstrapDialog.show({
        title: 'Save Options',
        message: function(dialog){
            if (jQuery.trim($x('#sesName').text()) == 'None'){
                var $xcontent = $x('<input type="text" id="DATname" placeholder="Name of DAT file">')
            }
            else{
                var temp = jQuery.trim($x('#sesName').text())
                var $xcontent = $x('<input type="text" id="DATname">')
                $xcontent[0].value = temp
            }
            return $xcontent
        },
        buttons: [{
            label: 'Save to Server',
            action: function(dialogItself){
                $x.post('/SDproc/generateOutput', {outType: 7, datFName: $x('#DATname').val()}, function(data){
                    alert('Saved');
                    $x('#sesName').html(data);
                    dialogItself.close();
                })
            }
        }, {
            label: 'Save Locally',
            action: function(dialogItself){
                $x('#output-form').attr('action', '/SDproc/generateOutput')
                $x('#outType').val(6);
                $x('#datFName').val($x('#DATname').val())
                $x('#output-form')[0].submit();
                dialogItself.close();
            }
        }]
    })
}

// check this function again, might not be correct format
function logout(){
    if (localStorage.getItem('usingDAT') === null){
        window.location.href = ("logout");
    }
    else{
        previous = localStorage.getItem('usingDAT');
        $x.post("/SDproc/save_comment", { idprev: previous, comment: $x('#comment').val(), format: 1}, function(){
            window.location.href = ("logout")
        });
    }
}


$x(window).on('unload', function(){
    if (jQuery.trim($x('#process_plot').text()) == "No DAT selected"){
        return;
    }
    else{
        $x.post( "/SDproc/save_comment", {comment: $x('#comment').val(), format: 3})
    }
})