
$x(function (){
    $x('#sel1').on('click', 'tr.file', function(e) {
        var rows = $x('tr.file');
        rows.removeClass('highlight');
        $x(this).addClass('highlight');
        var ses = localStorage.getItem('usingSes');
        $x('#fileName').text($x('td:first', $x(this)).text());
        if (localStorage.getItem('previous2') === null) {
            localStorage.setItem('previous2', $x(this).data('value'));
            $x.post('/SDproc/data', { idnext: $x(this).data('value') , plot: 1}, function(data) {
                $x('#metaForm_id').html( $x(data).find('#metaForm_id').html());
                $x('#plot_spot').html( $x(data).find('#plot_spot').html());
                $x('#currentAE').html( $x(data).find('#currentAE').html());
                $x.post('/SDproc/get_fsession_comment', { id: localStorage.getItem('previous2') }, function(data) {
                    $x('#comment').val(data);
                    setPlotAgainst();
                });
            });
            $x.post('/SDproc/get_hrm', { fileID: $x(this).data('value') }, function(hrmName) {
                $x('#HRM').text(hrmName);
            });
        } else {
            var nextID = $x(this).data('value');
            previous = localStorage.getItem('previous2');
            $x('#idnum').val(previous);
            localStorage.setItem('previous2', nextID);
            $x('#meta-form').submit();
            $x.post('/SDproc/get_fsession_comment', { id: nextID }, function(data) {
                $x('#comment').val(data);
                setPlotAgainst();
            });
            $x.post('/SDproc/get_hrm', { fileID: $x(this).data('value') }, function(hrmName) {
                $x('#HRM').text(hrmName);
            });
        }
    });
});



$x(document).ready( function() {
    $x('#unit').val('meV');
    setPlotAgainst();
    asynchOnLoad()
    $x('#pane').hide();
    if (!localStorage.getItem('previous2') === null)
        localStorage.removeItem("previous2");
    $x('#fitType').text('Fit around max');
    $x('#fitType').append("<span class='caret'></span>");
    $x('#peakLocation').attr('placeholder', 'Peak found automatically');
    $x('#peakLocation').prop('disabled', true);
    $x('#pWInput').prop('disabled', false);
    $x('#logbtn').text('Add to Logbook');
    $x('#logbtn').prop('disabled', false);
    $x('#commentGroup').removeClass('logCommentGroup');
    $x('#commentGroup').addClass('commentGroup');
    sortTable($x('#filePicker'));
    localStorage.setItem('justPeakFit', 0);
});

/*
    This function is listening on the whole document for a key press, it checks if the <enter> key has been pressed.
    If the <enter> key is pressed, then prevent it from doing its normal function. Then, check if there is an active
    element on the page, and if there is, then lose its focus. (i.e. it is not highlighted)
*/
//$x(document).keypress( function(event) {
//     if (event.which == '13') {
//        event.preventDefault();
//        if ("activeElement" in document) {
//            document.activeElement.blur();
//        }
//      }
//});

function asynchOnLoad(){
    var deferred = new $x.Deferred(), completed = deferred.then(function(){
        sortTable($x('#sel1'));
        $x('#sel1 tr.file:first').trigger('click');
        return 1;
    });
    if (localStorage.getItem('use_files')){
        $x.post("/SDproc/get_file_name", {ids: localStorage.getItem('use_files')},
        function(data){
            data = JSON.parse(data)
            for(i = 0; i < data.length; i++){
                if (data[i][1] == true){
                    $x('#sel1 > tbody:last-child')
                    .append('<tr style="cursor: pointer;" data-value="'+data[i][2]+'" class="file"><td class="fileNameCell">' + data[i][0] + '<td><input onclick="updateSumCheck(this)" checked type="checkbox"></td></tr>')
                }
                else{
                    $x('#sel1 > tbody:last-child')
                    .append('<tr style="cursor: pointer;" data-value="'+data[i][2]+'" class="file"><td class="fileNameCell">' + data[i][0] + '<td><input onclick="updateSumCheck(this)" type="checkbox"></td></tr>')
                }
            }
            $x('#pane').show();
            deferred.resolve();
        })
    }
    return deferred.promise()
}

function removeID(id, idArray){
    var result = $x.grep(idArray, function(n, i){
        return (n !== id);
    })
    return result;
}


$x(window).on('unload', function(){
//    $x.post('/SDproc/close_plots');
    if (localStorage.getItem('previous2') === null)
    {
        return;
    }
    else
    {
        previous = localStorage.getItem('previous2');
        $x('#idnum').val(previous);
//        $x.post( "/SDproc/save_comment", { idprev: previous, comment: $x('#comment').val(), format: 1})
//        $x.post('/SDproc/save_graph', $x('#meta-form').serialize())
        localStorage.removeItem('previous2');
    }
})

$x(function() {
    var rows = $x('tr.item');
    rows.on('click', function(e)
    {
        var row = $x(this);
        rows.removeClass('highlight');
        rows.removeClass('lightlight');
        row.addClass('highlight');
        $x('#sel1 > tbody:last-child')
            .append('<tr style="cursor: pointer;" data-value="'+$x('td:first', $x(row)).attr('id')+'" class="file"><td class="fileNameCell">' + $x('td:first', $x(row)).text() + '</td><td><input checked onclick="updateSumCheck(this)" type="checkbox"></td></tr>')
        $x('#pane').show()
        row.removeClass('highlight');
        if (localStorage.getItem('use_files') === null)
        {
            var files = [];
            files.push($x('td:first', $x(row)).attr('id'));
            localStorage.setItem('use_files', JSON.stringify(files));
        }
        else
        {
            var files = JSON.parse(localStorage.getItem('use_files'));
            files.push($x('td:first', $x(row)).attr('id'));
            localStorage.setItem('use_files', JSON.stringify(files));
        }
        $x('#fileModal').modal('toggle');
        $x('#sel1 tr:last').addClass('highlight');
        $x('#sel1 tr:last').trigger('click');
        sortTable($x('#sel1'));
    })

    rows.on('mouseenter', function(e)
    {
        var row = $x(this);
        if ($x(row).hasClass( "highlight" ))
        {
            rows.removeClass('lightlight');
        }
        else
        {
            rows.removeClass('lightlight');
            row.addClass('lightlight');
        }
    })

    $x(document).on('selectstart dragstart', function(e)
    {
        e.preventDefault();
        return false;
    })
})


/* session functions to save/overwrite session*/
//function populate_session(){
//    if ($x('#sesName').text() != 'None'){
//        $x('#ssName').val("HEllo");
//    }
//}

function save_session() {
    if (localStorage.getItem('previous2') === null) {
        return;
    } else {
        previous = localStorage.getItem('previous2');
        $x('#idnum').val(previous);
        $x.post('/SDproc/save_graph', $x('#meta-form').serialize());
    }

    $x.post('/SDproc/save_ses',{name: $x('#ssName').val(), comment: $x('#ssComment').val(), checked: 0}, function(data) {
        $x('#sesName').html(data.name);
    }).done(function (d) {
        location.reload();
    });
}

/* if the user did not change the session name, then the function only return the ID of the session */
function overwrite_session() {
    $x.post('/SDproc/save_ses', {name: $x('#ssName').val(), comment: $x('#ssComment').val(), checked: 0}, function(data) {
        var data = JSON.parse(data); // this is the session ID
        /* status is null because user did not change the session name */
        if (data.status == null) {
            $x('#confirmModal').modal('show')
        } else {
            $x('#sesName').html(data.name);
        }
    });
}

function confirm_overwrite() {
    $x.post('/SDproc/save_ses', {name: $x('#ssName').val(), comment: $x('#ssComment').val(), checked: 0}, function(data) {
        var data = JSON.parse(data); // this is the session ID
        /* status is null because user did not change the session name */
        if (data.status == null) {
            // deletes the current session with the ID we received from first save
            $x.post('/SDproc/delete_session',{ id: data, type: "session"});
            // calls the save function again to save the new updated session with the same name
            $x.post('/SDproc/save_ses',{name: $x('#ssName').val(), comment: $x('#ssComment').val(), checked: 1}, function(data) {
                // sets the session name on screen
                $x('#sesName').html(data);
            });
        }
    });
}

//function save_comments() {
//    previous = localStorage.getItem('previous2');
//    $x('#idnum').val(previous);
//    $x.post('/SDproc/save_fsession_comment', {id: previous, comment: $x('#comment').val() });
//}

function log(){
    previous = localStorage.getItem('previous2');
    $x.post('/SDproc/add_entry', {id : previous},
    function(){
        $x('#logbtn').text('Added');
        $x('#logbtn').prop('disabled', true);
        $x('#commentGroup').removeClass('commentGroup');
        $x('#commentGroup').addClass('logCommentGroup');
    })
}

function updateSumCheck(checkbox){
    if ($x(checkbox).is(':checked')){
        idnum = $x(checkbox).parent().parent().data('value');
        $x.post('/SDproc/updateSumCheck', {id: idnum, check: "True"});
    }
    else{
        idnum = $x(checkbox).parent().parent().data('value');
        $x.post('/SDproc/updateSumCheck', {id: idnum, check: "False"});
    }
}

function deleteCmeta() {
    if (localStorage.getItem('previous2') === null) {
        alert("No file selected")
    } else {
        selected = localStorage.getItem('previous2');
        $x.post('/SDproc/clearPart_cmeta', {id: selected}, function() {
            $x('#sel1 > tbody > tr').each(function() {
                var sel = parseInt(selected);
                if ($x(this)[0].getAttribute("data-value") == sel) {
                    localStorage.removeItem('previous2');
                    if (this.previousElementSibling !== null) {
                        var newSelected = this.previousSibling;
                        $x(newSelected).addClass('highlight');
                        $x(this).remove();
                        var saved_files = JSON.parse(localStorage.getItem('use_files'));
                        console.log(saved_files);
                        var result = $x.grep(saved_files, function(n,i) {
                            return (n != String(sel));
                        });
                        console.log(result);
                        localStorage.setItem('use_files', JSON.stringify(result));
                        $x(newSelected).trigger('click');
                    } else if (this.nextElementSibling !== null) {
                        var newSelected = this.nextSibling;
                        $x(newSelected).addClass('highlight');
                        $x(this).remove();
                        var saved_files = JSON.parse(localStorage.getItem('use_files'));
                        console.log(saved_files);
                        var result = $x.grep(saved_files, function(n,i){
                            return (n != String(sel));
                        });
                        console.log(result);
                        localStorage.setItem('use_files', JSON.stringify(result));
                        $x(newSelected).trigger("click");
                    } else {
                        $x('#comment').val('');
                        $x(this).remove();
                        var saved_files = JSON.parse(localStorage.getItem('use_files'));
                        console.log(saved_files);
                        var result = $x.grep(saved_files, function(n,i){
                            return (n != String(sel));
                        });
                        console.log(result);
                        localStorage.setItem('use_files', JSON.stringify(result));
                    }
                }
            });
        });
    }
}


$x(function(){
    $x('#meta-form').on('submit', function(event){
        event.preventDefault();
        $x.post('/SDproc/save_graph', $x(this).serialize(),
        function(){
            nextID = localStorage.getItem('previous2');
            $x.post('/SDproc/data', { idnext: nextID , plot: 1},
            function(data){
                $x('#metaForm_id').html( $x(data).find('#metaForm_id').html());
                $x('#plot_spot').html( $x(data).find('#plot_spot').html());
                $x('#currentAE').html( $x(data).find('#currentAE').html());
                setPlotAgainst();
                localStorage.setItem('justPeakFit', 0);
            })
        });
        $x('#logbtn').text('Add to Logbook');
        $x('#logbtn').prop('disabled', false);
        $x('#commentGroup').removeClass('logCommentGroup');
        $x('#commentGroup').addClass('commentGroup');
    });
})

$x(function(){
    $x('#meta-form').on('change', function(event){
        previous = localStorage.getItem('previous2');
        $x('#idnum').val(previous);
        $x.post('/SDproc/save_graph', $x('#meta-form').serialize(),
        function(){
            var unit = $x('#unit').val();
            $x.post('/SDproc/data', { idnext: previous , plot: 1, unit: unit},
            function(data){
                $x('#metaForm_id').html( $x(data).find('#metaForm_id').html());
                $x('#plot_spot').html( $x(data).find('#plot_spot').html());
                localStorage.setItem('justPeakFit', 0);
            })
        })
        $x('#logbtn').text('Add to Logbook');
        $x('#logbtn').prop('disabled', false);
        $x('#commentGroup').removeClass('logCommentGroup');
        $x('#commentGroup').addClass('commentGroup');
    })
})


function aroundMax(){
    $x('#fitType').text('Fit around max');
    $x('#fitType').append("<span class='caret'></span>");
    $x('#peakLocation').val('');
    $x('#peakLocation').attr('placeholder', 'Peak found automatically');
    $x('#peakLocation').prop('disabled', true);
    $x('#peakGroup').removeClass('splitInput');
    $x('#localRange').hide();
    $x('#hide').hide();
}

function atPoint(){
    $x('#fitType').text('Peak at Point');
    $x('#fitType').append("<span class='caret'></span>");
    $x('#peakLocation').attr('placeholder', 'Energy Value (meV)');
    $x('#peakLocation').prop('disabled', false);
    $x('#peakGroup').removeClass('splitInput');
    $x('#localRange').hide();
    $x('#hide').hide();
}

function nearestPeak(){
    $x('#fitType').text('Fit around point');
    $x('#fitType').append("<span class='caret'></span>");
    $x('#peakLocation').attr('placeholder', 'Energy Value (meV)');
    $x('#localRange').prop('placeholder', 'Range (meV)');
    $x('#peakLocation').prop('disabled', false);
    $x('#peakGroup').addClass('splitInput');
    $x('#localRange').show();
    $x('#hide').show();
}

var waitPeak = $x.Deferred();
function fitPeak(sendOut){
    temp = $x('#peakSignalType').text();
    previous = localStorage.getItem('previous2');
    $x('#metaForm_id input').each(function(){
        $x(this).removeProp('checked');
    })
    var unit = $x('#unit').val();
    if ($x('#fitType').text() == 'Fit around max'){
        var range = $x('#pWInput').val()
        if ($x.isNumeric(range)){
            $x.post('/SDproc/peakFit', {idnum: previous, fitType: 'AtMax', inputRange: range, sendOut: sendOut, unit: unit,
            signal: $x('#peakSignalType').text(), energy: $x('#peakEnergyType').text()}, function(data){
                if (sendOut == 1){
                    localStorage.setItem('peakData', data);
                    waitPeak.resolve();
                }
                $x('#plot_spot').html( $x(data).find('#plot_spot').html());
                $x('#shiftVal').html( $x(data).find('#shiftVal').html());
                localStorage.setItem('justPeakFit', 1);
            });
        }
        else{
            $x('#meta-form').trigger('change');
            alert('Please enter a valid range')
        }
    }
    else if ($x('#fitType').text() == 'Peak at Point'){
        var cord = $x('#peakLocation').val()
        var range = $x('#pWInput').val()
        if ($x.isNumeric(cord)){
            if ($x.isNumeric(range)){
                $x.post('/SDproc/peakFit', {idnum: previous, fitType: 'AtPoint', inputCord: cord, inputRange: range,
                sendOut: sendOut, unit: unit, signalType: $x('#peakSignalType').text(),
                energyType: $x('#peakEnergyType').text()}, function(data){
                if (sendOut == 1){
                    localStorage.setItem('peakData', data);
                    waitPeak.resolve();
                }
                $x('#plot_spot').html( $x(data).find('#plot_spot').html());
                $x('#shiftVal').html( $x(data).find('#shiftVal').html());
                localStorage.setItem('justPeakFit', 1);
                })
            }
            else{
                $x('#meta-form').trigger('change');
                alert('Please enter a valid range');
            }
        }
        else{
            $x('#meta-form').trigger('change');
            alert('Please enter a valid point');
        }
    }
    else{
        var cord = $x('#peakLocation').val()
        var range = $x('#pWInput').val()
        var localRange = $x('#localRange').val()
        if ($x.isNumeric(cord)){
            if ($x.isNumeric(range)){
                if ($x.isNumeric(localRange)){
                    $x.post('/SDproc/peakFit', {idnum: previous, fitType: 'AroundPoint', inputCord: cord, inputRange: range,
                    localRange: localRange, sendOut: sendOut, unit: unit, signalType: $x('#peakSignalType').text(),
                    energyType: $x('#peakEnergyType').text()}, function(data){
                        if (sendOut == 1){
                            localStorage.setItem('peakData', data);
                            waitPeak.resolve();
                        }
                        $x('#plot_spot').html( $x(data).find('#plot_spot').html());
                        $x('#shiftVal').html( $x(data).find('#shiftVal').html());
                        localStorage.setItem('justPeakFit', 1);
                    })
                }
                else{
                    $x('#meta-form').trigger('change');
                    alert('Please enter a valid peak range');
                }
            }
            else{
                $x('#meta-form').trigger('change');
                alert('Please enter a valid range');
            }
        }
        else{
            $x('#meta-form').trigger('change');
            alert('Please enter a valid energy value');
        }
    }
}

$x(function (){
    $x('#HRMdd a').on('click', function(event){
        var hrm = event.target.text;
        previous = localStorage.getItem('previous2');
        $x.post('/SDproc/updateHRM', {idnum: previous, hrm: hrm}, function(data){
            $x('#HRM').text(data);
            $x('#HRM').append("<span class='caret'></span>");
            $x('#meta-form').trigger('change');
        });
    });
});

function outputFile(){
    waitPeak = $x.Deferred();
    if (localStorage.getItem('previous2') === null){
        alert('No file loaded');
    }
    else if (localStorage.getItem('justPeakFit') == 1){
        fitPeak(1)
        $x.when(waitPeak).done(function(){
            $x('#idnum').val(localStorage.getItem('previous2'));
            var cords = localStorage.getItem('peakData');
            $x('#outType').val(2);
            $x('#cordData').val(cords);
            $x('#meta-form').attr('action', '/SDproc/generateOutput')
            $x('#meta-form')[0].submit()
            $x('#meta-form').attr('action', '');
        });
        return waitPeak.promise()
    }
    else{
        $x('#idnum').val(localStorage.getItem('previous2'));
        $x('#outType').val(1);
        $x('#meta-form').attr('action', '/SDproc/generateOutput')
        $x('#meta-form')[0].submit()
        $x('#meta-form').attr('action', '');
    }
}

function setAE(event){
    if (event.target.text == 'Energy'){
        $x('#againstE').text('Energy');
        $x('#againstE').append("<span class='caret'></span>");
        $x('#agaE').val('Energy');
    }
    else if (event.target.text == 'Energy xtal'){
        $x('#againstE').text('Energy xtal');
        $x('#againstE').append("<span class='caret'></span>");
        $x('#agaE').val('Energy xtal');
    }
    else if (event.target.text == 'Energy xtal w/T'){
        $x('#againstE').text('Energy xtal w/T');
        $x('#againstE').append("<span class='caret'></span>");
        $x('#agaE').val('Energy xtal w/T');
    }
    else if (event.target.text == 'Energy Fitted'){
        $x('#againstE').text('Energy Fitted');
        $x('#againstE').append("<span class='caret'></span>");
        $x('#agaE').val('Energy Fitted');
    }
    else {
        $x('#againstE').text('Point #');
        $x('#againstE').append("<span class='caret'></span>");
        $x('#agaE').val('Point #');
    }
    $x('#meta-form').trigger('change');
}

function setPeakSignal(event){
    if (event.target.text == 'Signal Normalized'){
        $x('#peakSignalType').text('Signal Normalized');
        $x('#peakSignalType').append("<span class='caret'></span>");
    }
    else{
        $x('#peakSignalType').text('Signal');
        $x('#peakSignalType').append("<span class='caret'></span>");
    }
}

function setPeakEnergy(event){
    if (event.target.text == 'Energy Fitted'){
        $x('#peakEnergyType').text('Energy Fitted');
        $x('#peakEnergyType').append("<span class='caret'></span>");
    }
    else if (event.target.text == 'Energy xtal'){
        $x('#peakEnergyType').text('Energy xtal');
        $x('#peakEnergyType').append("<span class='caret'></span>");
    }
    else if (event.target.text == 'Energy xtal w/T'){
        $x('#peakEnergyType').text('Energy xtal w/T');
        $x('#peakEnergyType').append("<span class='caret'></span>");
    }
    else{
        $x('#peakEnergyType').text('Energy');
        $x('#peakEnergyType').append("<span class='caret'></span>");
    }
}

function setUnit(event){
    if (event.target.text == 'meV'){
        $x('#unitBtn').text('meV');
        $x('#unitBtn').append("<span class='caret'></span>");
        $x('#unit').val('meV');
    }
    else{
        $x('#unitBtn').text('keV');
        $x('#unitBtn').append("<span class='caret'></span>");
        $x('#unit').val('keV');
    }
    $x('#meta-form').trigger('change');
}

function setPlotAgainst(){
    var currentAE = $x('#currentAE').text();
    $x('#againstE').text(currentAE);
    $x('#againstE').append("<span class='caret'></span>");
    $x('#agaE').val(currentAE);
}

function headerFile(){
    previous = localStorage.getItem('previous2');
    $x.post("/SDproc/header_file", {id: previous}, function(data){
        var header = $x('<div>').text(JSON.parse(data)).text();
        $x('#headerText').html(header.replace(/\n/g, '<br />'));
        $x('#headerModal').modal('show');
    });
}


function sortTable(table){
    tbody = table.find('tbody')
    tbody.find('tr').sort(function(a, b){
        return $x('td:first', a).text().localeCompare($x('td:first', b).text());
    }).appendTo(tbody);
}
