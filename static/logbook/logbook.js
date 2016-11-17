function deleteEntry(id)
{
    $.post( "/SDproc/del_entry", { id: id },
    function(){
        location.reload();
    })
}

function deleteAll(){
    $.post( "/SDproc/del_entry", { id: -1 },
    function(){
        location.reload();
    })
}