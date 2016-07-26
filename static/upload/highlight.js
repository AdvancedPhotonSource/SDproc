$(function()
{
    var rows = $('tr.item');
    rows.on('click', function(e)
    {
        var row = $(this);
        rows.removeClass('highlight');
        rows.removeClass('lightlight');
        row.addClass('highlight');
        comment($('td:first', $(row)).attr('id'));
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

function comment(id)
{
        if (localStorage.getItem('previous_upload') === null)
        {
            localStorage.setItem('previous_upload', id)
            $.post('/show_comment', { idnext: id },
            function(data){
            $('#comment').val(data)
            })
        }
        else
        {
            var nextID = id
            previous = localStorage.getItem('previous_upload');
            $.post( "/save_comment", { idprev: previous, comment: $('#comment').val()},
            function(){
                $.post('/show_comment', { idnext: nextID },
                function(data){
                    $('#comment').val(data)
                })
            $.getScript( "/static/add_file.js" );
            })
            localStorage.setItem('previous_upload', id);
        }
}