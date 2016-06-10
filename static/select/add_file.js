$(document).ready(function(){
    $('#finito').prop('disabled', true);
    localStorage.removeItem('previous')
    var rows = $('tr.item');
    rows.removeClass("highlight")
    rows.removeClass("lightlight")
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