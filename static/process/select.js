/*
-    Copyright (c) UChicago Argonne, LLC. All rights reserved.
-
-    Copyright UChicago Argonne, LLC. This software was produced
-    under U.S. Government contract DE-AC02-06CH11357 for Argonne National
-    Laboratory (ANL), which is operated by UChicago Argonne, LLC for the
-    U.S. Department of Energy. The U.S. Government has rights to use,
-    reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR
-    UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
-    ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
-    modified to produce derivative works, such modified software should
-    be clearly marked, so as not to confuse it with the version available
-    from ANL.
-
-    Additionally, redistribution and use in source and binary forms, with
-    or without modification, are permitted provided that the following
-    conditions are met:
-
-        * Redistributions of source code must retain the above copyright
-          notice, this list of conditions and the following disclaimer.
-
-        * Redistributions in binary form must reproduce the above copyright
-          notice, this list of conditions and the following disclaimer in
-          the documentation and/or other materials provided with the
-          distribution.
-
-        * Neither the name of UChicago Argonne, LLC, Argonne National
-          Laboratory, ANL, the U.S. Government, nor the names of its
-          contributors may be used to endorse or promote products derived
-          from this software without specific prior written permission.
-
-    THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS
-    AS IS AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
-    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
-    FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago
-    Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
-    INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
-    BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
-    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
-    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
-    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
-    ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
-    POSSIBILITY OF SUCH DAMAGE.
*/
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

function startProc(){
    $('#sel1').trigger('change');
    $('#procButton').hide();
    $('#settingsBtn').show();
    $('#outputBtn').show();
}


$(document).ready( function() {
    asynchOnLoad()
    $('#procButton').show();
    $('#settingsBtn').hide();
    $('#outputBtn').hide();
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
        /*$('#sel1').trigger('change');*/
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
    $('#procButton').hide();
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
        if ($('#binRad').is(':checked')){
        var binWidth = $('#binWidth').val();
            if ($('#sel1').val().length == 1){
                id = localStorage.getItem('previous3');
                $.post('/SDproc/process', {idnext: id , output: 1, binWidth: binWidth}, function(data){
                    $('#idnum').val(id);
                    $('#cordData').val(data);
                    $('#outType').val(2);
                    $('#output-form').attr('action', '/SDproc/generateOutput')
                    $('#output-form')[0].submit();
                });
            }
            else{
                var ids = []
                $('#sel1 > option:selected').each(function(){
                    ids.push(this.value);
                });
                var jIds = JSON.stringify(ids);
                $.post('/SDproc/process', {idList: jIds, output: 1, binWidth: binWidth}, function(data){
                    $('#idnum').val(jIds);
                    $('#cordData').val(data);
                    $('#outType').val(3);
                    $('#output-form').attr('action', '/SDproc/generateOutput')
                    $('#output-form')[0].submit();
                });
            }
        }
        else{
            if ($('#sel1').val().length == 1){
                id = localStorage.getItem('previous3');
                $.post('/SDproc/process', {idnext: id , output: 1}, function(data){
                    $('#idnum').val(id);
                    $('#cordData').val(data);
                    $('#outType').val(2);
                    $('#output-form').attr('action', '/SDproc/generateOutput')
                    $('#output-form')[0].submit();
                });
            }
            else{
                var ids = []
                $('#sel1 > option:selected').each(function(){
                    ids.push(this.value);
                });
                var jIds = JSON.stringify(ids);
                $.post('/SDproc/process', {idList: jIds, output: 1}, function(data){
                    $('#idnum').val(jIds);
                    $('#cordData').val(data);
                    $('#outType').val(3);
                    $('#output-form').attr('action', '/SDproc/generateOutput')
                    $('#output-form')[0].submit();
                });
            }
        }
    }
}