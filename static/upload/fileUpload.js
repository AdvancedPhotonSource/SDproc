$( "#fileForm" ).submit(function(event){
    event.preventDefault();
    sendfileForm();
});

$(document).ready(function(){
    localStorage.clear();
})

$(window).on('unload', function(){
    if (localStorage.getItem('previous') === null)
    {
        return;
    }
    else
    {
        previous = localStorage.getItem('previous');
        $.post( "/save_comment", { idprev: previous, comment: $('#comment').val()});
    }
})

function resetForm()
{
    $('#fileForm')[0].reset();
}

function sendfileForm()
{
    var formData = new FormData($('#fileForm')[0]);
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
            localStorage.removeItem('previous');
            })
        }

        });
        if (found == 0)
        {
            alert('No File Selected')
        }
}