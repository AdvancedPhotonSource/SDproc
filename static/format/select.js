$(function (){
        $('#sel1').on('change', function(event){
        var ses = localStorage.getItem('usingSes');
        if (localStorage.getItem('previous2') === null)
        {
            localStorage.setItem('previous2', this.value);
            $.post('/data', { idnext: this.value , plot: 1},
            function(data){
                $.getScript( "https://gitcdn.github.io/bootstrap-toggle/2.2.2/js/bootstrap-toggle.min.js" );
                $('#metaForm_id').html( $(data).find('#metaForm_id').html());
                $('#plot_spot').html( $(data).find('#plot_spot').html());
                var hidden = $(data).find('#agaE').val();
                if (hidden === 'true' || hidden === 'True')
                {
                    $('#againstE').prop('checked', true);
                    $('#againstE').bootstrapToggle('on');
                    $('#agaE').val(true);
                }
                else
                {
                    $('#againstE').prop('checked', false);
                    $('#againstE').bootstrapToggle('off');
                    $('#agaE').val(false);
                }
            })

            $.post('/show_comment', { idnext: this.value, format: 1, ses: ses},
            function(data){
            $('#comment').val(data)
            })
        }
        else
        {
            var nextID = this.value
            previous = localStorage.getItem('previous2');
            $('#idnum').val(previous);
            localStorage.setItem('previous2', this.value);
            $('#meta-form').submit();
            $.post( "/save_comment", { idprev: previous, comment: $('#comment').val(), format: 1},
            function(){
                $.post('/show_comment', { idnext: nextID, format: 1, ses: ses},
                function(data){
                    $('#comment').val(data)
                })
            })
        }
    });

    /*$('#sel1').on('dblclick', function(){
        if (this.previousElementSibling !== null)
        {
            var prevID = this.previousSibling.value
            $.post
        }
    })
    */
})


$(document).ready( function() {
    asynchOnLoad()
    if (!localStorage.getItem('previous2') === null)
        localStorage.removeItem("previous2")
    $('#fitType').text('Fit around max');
    $('#fitType').append("<span class='caret'></span>");
    $('#peakLocation').attr('placeholder', 'Peak found automatically');
    $('#peakLocation').prop('disabled', true);
    $('#pWInput').prop('disabled', false);
    $('#logbtn').prop('disabled', false);
})

function asynchOnLoad(){
    var deferred = new $.Deferred(), completed = deferred.then(function(){
        $('#sel1 option:first').prop('selected', true);
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
    if (localStorage.getItem('previous2') === null)
    {
        return;
    }
    else
    {
        previous = localStorage.getItem('previous2');
        $('#idnum').val(previous);
        $.post( "/save_comment", { idprev: previous, comment: $('#comment').val(), format: 1})
        $.post('/save_graph', $('#meta-form').serialize())
        localStorage.removeItem('previous2');
    }
})

$(function()
{
    var rows = $('tr.item');
    rows.on('click', function(e)
    {
        var row = $(this);
        rows.removeClass('highlight');
        rows.removeClass('lightlight');
        row.addClass('highlight');
        $('#sel1')
            .append($('<option></option>')
            .text($('td:first', $(row)).text())
            .attr('value', $('td:first', $(row)).attr('id')))
        row.removeClass('highlight');
        if (localStorage.getItem('use_files') === null)
        {
            var files = [];
            files.push($('td:first', $(row)).attr('id'));
            localStorage.setItem('use_files', JSON.stringify(files));
        }
        else
        {
            var files = JSON.parse(localStorage.getItem('use_files'));
            files.push($('td:first', $(row)).attr('id'));
            localStorage.setItem('use_files', JSON.stringify(files));
        }
        $('#fileModal').modal('toggle');
        $('#sel1 option').prop('selected', false);
        $('#sel1 option:last').prop('selected', true);
        $('#sel1').trigger('change');
    })

    rows.on('mouseenter', function(e)
    {
        var row = $(this);
        if ($(row).hasClass( "highlight" ))
        {
            rows.removeClass('lightlight');
        }
        else
        {
            rows.removeClass('lightlight');
            row.addClass('lightlight');
        }
    })

    $(document).on('selectstart dragstart', function(e)
    {
        e.preventDefault();
        return false;
    })
})

function saveSes(){
    if (localStorage.getItem('previous2') === null)
    {
        return;
    }
    else
    {
        previous = localStorage.getItem('previous2');
        $('#idnum').val(previous);
        var temp = $('#againstE').prop('checked');
        $('#agaE').val(temp);
        $.post( "/save_comment", { idprev: previous, comment: $('#comment').val(), format: 1});
        $.post('/save_graph', $('#meta-form').serialize());
    }
    $.post('/save_ses',{name: $('#ssName').val(), comment: $('#ssComment').val(), checked: 0}, function(data){
        var data = JSON.parse(data)
        if (data.status == null){
            BootstrapDialog.show({
                title: 'Overwrite Session?',
                message: 'A session with this name already exists, would you like to overwrite it?',
                buttons: [{
                    label: 'Yes',
                    action: function(dialogItself){
                        $.post('/delete',{ id: data, table: "Session"});
                        $.post('/save_ses',{name: $('#ssName').val(), comment: $('#ssComment').val(), checked: 1}, function(data){
                            $('#sesName').html(data);
                            dialogItself.close();
                        });
                        }
                    }, {
                    label: 'No',
                    action: function(dialogItself){
                        dialogItself.close();
                        $('#ssModal').modal('show');
                    }
                }]
            });
        }
        $('#sesName').html(data.name);
    });
}

function log(){
    previous = localStorage.getItem('previous2');
    $.post('/add_entry', {id : previous},
    function(){
        $('#log_add').text('Added');
        $('#log_add').fadeOut(1000);
        $('#logbtn').prop('disabled', true);
    })
}

function hitAgaE(){
    var temp = $('#againstE').prop('checked');
    if (temp == false)
    {
        $('#againstE').bootstrapToggle('on');
    }
    else
    {
        $('#againstE').bootstrapToggle('off');
    }
    $('#againstE').promise().done(function(){
        $('#meta-form').trigger('change');
    });
}


$(function(){
    $('#AeListener').click(function(){
        hitAgaE();
    });
})

function deleteCmeta(){
    if (localStorage.getItem('previous2') === null){
        alert("No file selected")
    }
    else{
        selected = localStorage.getItem('previous2')
        $.post('/clearPart_cmeta', {id: selected}, function(){
            $('#sel1 > option:selected').each(function(){
                localStorage.removeItem('previous2');
                var sel = parseInt(selected);
                if (this.previousElementSibling !== null){
                    $(this.previousSibling).prop('selected', 'True');
                    $(this).remove();
                    var saved_files = JSON.parse(localStorage.getItem('use_files'));
                    var result = $.grep(saved_files, function(n,i){
                        return (n !== String(sel));
                    })
                    localStorage.setItem('use_files', JSON.stringify(result));
                    $("#sel1").trigger('change');
                }
                else if (this.nextElementSibling !== null){
                    $(this.nextSibling).prop('selected', 'True');
                    $(this).remove();
                    var saved_files = JSON.parse(localStorage.getItem('use_files'));
                    var result = $.grep(saved_files, function(n,i){
                        return (n !== String(sel));
                    })
                    localStorage.setItem('use_files', JSON.stringify(result));
                    $("#sel1").trigger("change");
                }
                else{
                    $('#comment').val('');
                    $(this).remove();
                    var saved_files = JSON.parse(localStorage.getItem('use_files'));
                    var result = $.grep(saved_files, function(n,i){
                        return (n !== String(sel));
                    })
                    localStorage.setItem('use_files', JSON.stringify(result));
                }
            })
        })
    }
}




$(function(){
    $('#meta-form').on('submit', function(event){
        event.preventDefault();
        $.post('/save_graph', $(this).serialize(),
        function(){
            nextID = localStorage.getItem('previous2');
            $.post('/data', { idnext: nextID , plot: 1},
            function(data){
                $.getScript( "https://gitcdn.github.io/bootstrap-toggle/2.2.2/js/bootstrap-toggle.min.js" );
                $('#metaForm_id').html( $(data).find('#metaForm_id').html());
                $('#plot_spot').html( $(data).find('#plot_spot').html());
                var hidden = $(data).find('#agaE').val();
                if (hidden === 'true' || hidden === 'True')
                {
                    $('#againstE').prop('checked', true);
                    $('#againstE').bootstrapToggle('on');
                    $('#agaE').val(true);
                }
                else
                {
                    $('#againstE').prop('checked', false);
                    $('#againstE').bootstrapToggle('off');
                    $('#agaE').val(false);
                }
            })
        });
        $('#logbtn').prop('disabled', false);
    });
})

$(function(){
    $('#meta-form').on('change', function(event){
        if(event.target.id == 'snbool')
            $('#sbool').removeProp('checked');
        else if(event.target.id == 'sbool')
            $('#snbool').removeProp('checked');
        else if(event.target.id == 'ebool')
        {
            $('#ecbool').removeProp('checked');
            $('#etcbool').removeProp('checked');
        }
        else if(event.target.id == 'ecbool')
        {
            $('#ebool').removeProp('checked');
            $('#etcbool').removeProp('checked');
        }
        else if(event.target.id == 'etcbool')
        {
            $('#ebool').removeProp('checked');
            $('#ecbool').removeProp('checked');
        }
        previous = localStorage.getItem('previous2');
        $('#idnum').val(previous);
        var temp = $('#againstE').prop('checked');
        $('#agaE').val(temp);
        $.post('/save_graph', $('#meta-form').serialize(),
        function(){
            $.post('/data', { idnext: previous , plot: 1},
            function(data){
                $.getScript( "https://gitcdn.github.io/bootstrap-toggle/2.2.2/js/bootstrap-toggle.min.js" );
                $('#metaForm_id').html( $(data).find('#metaForm_id').html());
                $('#plot_spot').html( $(data).find('#plot_spot').html());
                var hidden = $('#agaE').val();
                if (hidden === 'true' || hidden === 'True')
                {
                    $('#againstE').prop('checked', true);
                    $('#againstE').bootstrapToggle('on');
                }
                else
                {
                    $('#againstE').prop('checked', false);
                    $('#againstE').bootstrapToggle('off');
                }
            })
        })
        $('#logbtn').prop('disabled', false);
    })
})

$(function(){
    $('#comment').on('change', function(){
        previous = localStorage.getItem('previous2');
        $('#idnum').val(previous);
        $.post('/save_comment', {idprev: previous, comment: $('#comment').val(), format: 1});
    })
})

function aroundMax(){
    $('#fitType').text('Fit around max');
    $('#fitType').append("<span class='caret'></span>");
    $('#peakLocation').attr('placeholder', 'Peak found automatically');
    $('#peakLocation').prop('disabled', true);
    $('#peakGroup').removeClass('splitInput');
    $('#localRange').hide();
}

function atPoint(){
    $('#fitType').text('Peak at Point');
    $('#fitType').append("<span class='caret'></span>");
    $('#peakLocation').attr('placeholder', 'Energy Value');
    $('#peakLocation').prop('disabled', false);
    $('#peakGroup').removeClass('splitInput');
    $('#localRange').hide();
}

function nearestPeak(){
    $('#fitType').text('Fit around point');
    $('#fitType').append("<span class='caret'></span>");
    $('#peakLocation').attr('placeholder', 'Energy Value');
    $('#localRange').prop('placeholder', 'Range');
    $('#peakLocation').prop('disabled', false);
    $('#peakGroup').addClass('splitInput');
    $('#localRange').show();
}

function fitPeak(){
    previous = localStorage.getItem('previous2');
    $('#a1bool').removeProp('checked');
    $('#a2bool').removeProp('checked');
    $('#t1bool').removeProp('checked');
    $('#t2bool').removeProp('checked');
    $('#tcbool').removeProp('checked');
    $('#nbool').removeProp('checked');
    $('#nfbool').removeProp('checked');
    $('#xbool').removeProp('checked');
    if (!$('#ebool').prop('checked') && !$('#ecbool').prop('checked') && !$('#etcbool').prop('checked')){
        $('#ebool').prop('checked', true);
    }
    if (!$('#sbool').prop('checked') && !$('#sncbool').prop('checked')){
        $('#sbool').prop('checked', true);
    }
    if ($('#againstE').prop('checked') == false){
        $('#againstE').bootstrapToggle('on');
    }
    if ($('#fitType').text() == 'Fit around max'){
        var range = $('#pWInput').val()
        if ($.isNumeric(range)){
            $.post('/peakFit', {idnum: previous, fitType: 0, inputRange: range}, function(data){
                $('#plot_spot').html( $(data).find('#plot_spot').html());
            });
        }
        else{
            $('#meta-form').trigger('change');
            alert('Please enter a valid range')
        }
    }
    else if ($('#fitType').text() == 'Peak at Point'){
        var cord = $('#peakLocation').val()
        var range = $('#pWInput').val()
        if ($.isNumeric(cord)){
            if ($.isNumeric(range)){
                $.post('/peakFit', {idnum: previous, fitType: 1, inputCord: cord, inputRange: range}, function(data){
                $('#plot_spot').html( $(data).find('#plot_spot').html());
                })
            }
            else{
                $('#meta-form').trigger('change');
                alert('Please enter a valid range');
            }
        }
        else{
            $('#meta-form').trigger('change');
            alert('Please enter a valid point');
        }
    }
    else{
        var cord = $('#peakLocation').val()
        var range = $('#pWInput').val()
        var localRange = $('#localRange').val()
        if ($.isNumeric(cord)){
            if ($.isNumeric(range)){
                if ($.isNumeric(localRange)){
                    $.post('/peakFit', {idnum: previous, fitType: 2, inputCord: cord, inputRange: range, localRange: localRange}, function(data){
                        $('#plot_spot').html( $(data).find('#plot_spot').html());
                    })
                }
                else{
                    $('#meta-form').trigger('change');
                    alert('Please enter a valid peak range');
                }
            }
            else{
                $('#meta-form').trigger('change');
                alert('Please enter a valid range');
            }
        }
        else{
            $('#meta-form').trigger('change');
            alert('Please enter a valid energy value');
        }
    }
}

$(function (){
    $('#HRMdd li a').on('click', function(event){
        var hrm = event.target.text;
        previous = localStorage.getItem('previous2');
        if (hrm == 'Fe-inline-1meV'){
            hrm = '++'
            //    hrm_e0 = 14412500.0
            //    hrm_bragg1 = 18.4704
            //    hrm_bragg2 = 77.5328
            //    hrm_alpha1 = 2.6e-6
            //    hrm_alpha2 = 2.6e-6
            $('#HRM').text('Fe-inline-1meV')
            $('#HRM').append("<span class='caret'></span>");
        }
        else if (hrm == 'Sn-nested-1meV'){
            hrm = '+-'
            $('#HRM').text('Sn-nested-1meV')
            $('#HRM').append("<span class='caret'></span>");
        }
        else if (hrm == 'Eu-nested-1meV'){
            hrm = '+-'
            $('#HRM').text('Eu-nested-1meV')
            $('#HRM').append("<span class='caret'></span>");
        }
        else if (hrm == 'Dy-nested-1meV'){
            hrm = '+-'
            $('#HRM').text('Dy-nested-1meV')
            $('#HRM').append("<span class='caret'></span>");
        }
        else if (hrm = 'IXS-cryo-1meV'){
            hrm = '++'
            $('#HRM').text('IXS-cryo-1meV')
            $('#HRM').append("<span class='caret'></span>");
        }
        $.post('/updateHRM', {idnum: previous, hrm: hrm}, function(){
            $('#meta-form').trigger('change');
        })
    })
})

function advance(){
    window.location.href = ("process");
}

function outputFile(){
    if (localStorage.getItem('previous2') === null){
        alert('No file loaded');
    }
    else{
        BootstrapDialog.show({
            title: 'Output Type?',
            message: 'Would you like to save the data for the current file, or for the entire session?',
            buttons: [{
                label: 'Current File',
                action: function(dialogItself){
                        $('#idnum').val(localStorage.getItem('previous2'))
                        $('#outSingular').val(1)
                        $.post('/generateOutput', $('#meta-form').serialize(), function(data){
                            alert(data);
                        })
                        dialogItself.close();
                    }
                }, {
                label: 'Entire Session',
                action: function(dialogItself){
                    $('#session').val(localStorage.getItem('previous'))
                    $('#outSingular').val(0)
                    $.post('/generateOutput', $('#meta-form').serialize(), function(data){
                        alert(data);
                    })
                    dialogItself.close();
                }
            }]
        });
    }
}