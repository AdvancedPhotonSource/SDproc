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
        table = model.find('.table');
        rows = table.find('tbody tr');
        /* Dirtiest filter function ever ;) */
        var filteredRows = rows.filter(function(){
            var value = $(this).find('td').eq(column).text().toLowerCase();
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
        $.post( "/save_comment", { idprev: previous, comment: $('#comment').val(), format: 2});
    }
})

function moveFile()
{
    var found = 0;
    $("tr.item").each(function(){
        var row = $(this);
        if ($(row).hasClass( "highlight" ))
        {
            found = 1;
            $.post( "/make_name" , {id : $('td:first', $(row)).attr('id')},
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
    $.post('/clear_rowa',function(){
        $.post('/clear_cmeta', function(){
            window.location.href = ("data");
        })
    });
}


function proceed()
{
    $.post('/clear_rowa',function(){
        $.post('/clear_cmeta', function(){
            sesID = localStorage.getItem('previous');
            $.post('/set_ses', {id: sesID}, function(data){
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
                            $.post( "/delete", { id: fid, table: "Session"},
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

}