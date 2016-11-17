$(document).ready(function(){
    $('#finito').prop('disabled', true);
    localStorage.removeItem('previous')
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

$(window).on('unload', function(){
    if (localStorage.getItem('previous') === null)
    {
        return;
    }
    else
    {
        previous = localStorage.getItem('previous');
        $.post( "/SDproc/save_comment", { idprev: previous, comment: $('#comment').val(), format: 2});
    }
})

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

function moveFile()
{
    var found = 0;
    $("tr.item").each(function(){
        var row = $(this);
        if ($(row).hasClass( "highlight" ))
        {
            found = 1;
            $.post( "/SDproc/make_name" , {id : $('td:first', $(row)).attr('id')},
            function(data){
                var temp = data;
                $('#sel1')
                    .append($('<option></option>')
                    .text(data)
                    .attr('value', $('td:first', $(row)).attr('id')))
            })
        }
    })
    if (found == 0)
    {
        alert('No File Selected');
    }
}



function newSession()
{
    localStorage.clear();
    $.post('/SDproc/clear_rowa',function(){
        $.post('/SDproc/clear_cmeta', function(){
            window.location.href = ("data");
        })
    });
}


function proceed()
{
    $.post('/SDproc/clear_rowa',function(){
        $.post('/SDproc/clear_cmeta', function(){
            sesID = localStorage.getItem('previous');
            $.post('/SDproc/set_ses', {id: sesID}, function(data){
            var parsed = $.parseJSON(data);
            var files = [];
                $(parsed).each(function(){
                    files.push(this);
                })
                localStorage.setItem('use_files', JSON.stringify(files));
                localStorage.setItem('usingSes', 1);
                window.location.href = ("data");
            })
        })
    });
}

function delFile()
{
        BootstrapDialog.show({
            title: 'Delete Session?',
            message: 'Are you sure you want to delete this session?',
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
                            $.post( "/SDproc/delete", { id: fid, table: "Session"},
                            function(){
                            $('#navTable').load(location.href+" #navTable>*","");
                            $.getScript( "/static/select/highlight.js" );
                            $('#comment').val('')
                            localStorage.removeItem('previous');
                            $('#finito').prop('disabled', true);
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

function shareSes(){
        BootstrapDialog.show({
            title: 'Share Session?',
            message: 'Are you sure you want to share this session?',
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
                            $.post( "/SDproc/shareSes", { id: fid, toUser: toUser});
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