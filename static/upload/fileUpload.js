$(document).ready(function(){
    var rows = $('tr.item');
    rows.removeClass("highlight")
    rows.removeClass("lightlight")


    $('#ssName').keyup(function(e){

        /* Ignore tab key */
        var code = e.keyCode || e.which;
        if (code == '9') return;
        /* Useful DOM data and selectors */
        var input = $(this);
        inputContent = input.val().toLowerCase();
        model = input.parents();
        table = model.find('#nameTable');
        rows = table.find('tbody tr');
        rows.removeClass('highlight');
        rows.removeClass('lightlight');
        /* Dirtiest filter function ever ;) */
        var filteredRows = rows.filter(function(){
            var value = $(this).find('td').text().toLowerCase();
            return value.indexOf(inputContent) === -1;
        });
        /* Clean previous no-result if exist */
        table.find('tbody .no-result').remove();
        /* Show all rows, hide filtered ones (never do that outside of a demo ! xD) */
        rows.show();
        filteredRows.hide();
        /* Prepend no-result row if all rows are filtered */
        if (filteredRows.length === rows.length) {
            table.find('tbody').prepend($('<tr class="no-result text-center"><td colspan="'+ ('#ssName').length +'">No result found</td></tr>'));
        }
        if (filteredRows.length === rows.length-1){
            $(table.find('tbody tr:visible').addClass('highlight'))
        }
    });

    $('#navName').keyup(function(e){

        /* Ignore tab key */
        var code = e.keyCode || e.which;
        if (code == '9') return;
        /* Useful DOM data and selectors */
        var input = $(this);
        inputContent = input.val().toLowerCase();
        model = input.parents();
        table = model.find('#navTable');
        rows = table.find('tbody tr');
        rows.removeClass('highlight');
        rows.removeClass('lightlight');
        /* Dirtiest filter function ever ;) */
        var filteredRows = rows.filter(function(){
            var value = $(this).find('td').text().toLowerCase();
            return value.indexOf(inputContent) === -1;
        });
        /* Clean previous no-result if exist */
        table.find('tbody .no-result').remove();
        /* Show all rows, hide filtered ones (never do that outside of a demo ! xD) */
        rows.show();
        filteredRows.hide();
        /* Prepend no-result row if all rows are filtered */
        if (filteredRows.length === rows.length) {
            table.find('tbody').prepend($('<tr class="no-result text-center"><td colspan="'+ ('#navName').length +'">No result found</td></tr>'));
        }
        if (filteredRows.length === rows.length-1){
            $(table.find('tbody tr:visible').addClass('highlight'));
            $(table.find('tbody tr:visible').trigger("click"));
        }
    });
});


$( "#fileForm" ).submit(function(event){
    event.preventDefault();
    sendfileForm();
});


$(window).on('unload', function(){
    if (localStorage.getItem('previous_upload') === null)
    {
        return;
    }
    else
    {
        previous = localStorage.getItem('previous_upload');
        $.post( "/save_comment", { idprev: previous, comment: $('#comment').val()});
    }
})

function resetForm()
{
    $('#fileForm')[0].reset();
}

function sendfileForm()
{
    var formData = new FormData();
    var fileData = $('input[type="file"]')[0].files;
    for (var i = 0; i < fileData.length; i++){
        formData.append("file_"+i, fileData[i]);
    }
    formData.append('formatType', $.trim($('#formatType').text()))
    formData.append('formatDelim', $('#formatDelim').val())
    $.ajax({
        url: '/addf',
        type: 'POST',
        data: formData,
        contentType: false,
        cache: false,
        processData: false,
        async: false,
        success: function (){
            $('#navTable').load(location.href+" #navTable>*","");
            $.getScript( "/static/upload/highlight.js" );
            resetForm();
            return;
        },
        error: function(error){
            console.log(error);
            return;
        }
    });
}

function delFile()
{
        BootstrapDialog.show({
            title: 'Delete File?',
            message: 'Are you sure you want to delete this file?\n\nAfter deletion, sessions that contain this file will likely have problems.',
            buttons: [{
                label: 'Yes',
                action: function(dialogItself){
                        dialogItself.close();
                        var found = 0;
                        $("tr.item").each(function(){
                        var row = $(this);
                        if ($(row).hasClass( "highlight" ))
                        {
                            found = 1;
                            var fid = $('td:first', $(row)).attr('id')
                            $.post( "/delete", { id: fid, table: "File"},
                            function(){
                            $('#navTable').load(location.href+" #navTable>*","");
                            $.getScript( "/static/upload/highlight.js" );
                            $('#comment').val('')
                            localStorage.removeItem('previous_upload');
                            })
                        }
                        });
                        if (found == 0)
                        {
                            alert('No File Selected')
                        }
                    }
                }, {
                label: 'No',
                action: function(dialogItself){
                    dialogItself.close();
                }
            }]
        });
}

function shareFile(){
        BootstrapDialog.show({
            title: 'Share File?',
            message: 'Are you sure you want to share this file?',
            buttons: [{
                label: 'Yes',
                action: function(dialogItself){
                        dialogItself.close();
                        var found = 0;
                        $("#navTable tr.item").each(function(){
                        var row = $(this);
                        if ($(row).hasClass( "highlight" ))
                        {
                            found = 1;
                            var fid = $('td:first', $(row)).attr('id');
                            var nameTable = $('#nameTable');
                            var toUser = $.trim($(table.find('tbody tr.highlight')).text())
                            $.post( "/shareFile", { id: fid, toUser: toUser});
                        }
                        });
                        if (found == 0)
                        {
                            alert('No File Selected')
                        }
                    }
                }, {
                label: 'No',
                action: function(dialogItself){
                    dialogItself.close();
                }
            }]
        });
}

$(function()
{
    table = $('#nameTable');
    rows = table.find('tbody tr');
    rows.on('click', function(e)
    {
        var row = $(this);
        rows.removeClass('highlight');
        rows.removeClass('lightlight');
        row.addClass('highlight');
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