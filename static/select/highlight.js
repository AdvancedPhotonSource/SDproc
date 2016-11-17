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
        $('#finito').prop('disabled', false);
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
        if (localStorage.getItem('previous') === null)
        {
            localStorage.setItem('previous', id)
            $.post('/SDproc/show_comment', { idnext: id, format: 2},
            function(data){
            $('#comment').val(data)
            })
        }
        else
        {
            var nextID = id
            previous = localStorage.getItem('previous');
            $.post( "/SDproc/save_comment", { idprev: previous, comment: $('#comment').val(), format: 2},
            function(){
                $.post('/SDproc/show_comment', { idnext: nextID, format: 2},
                function(data){
                    $('#comment').val(data)
                })
            })
            localStorage.setItem('previous', id);
        }
}