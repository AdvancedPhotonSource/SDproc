$(document).ready( function() {
    Users();

    var rows = $('tr.item');
    rows.removeClass("highlight")
    rows.removeClass("lightlight")


    $('#fileFilt').keyup(function(e){

        /* Ignore tab key */
        var code = e.keyCode || e.which;
        if (code == '9') return;
        /* Useful DOM data and selectors */
        var input = $(this);
        inputContent = input.val().toLowerCase();
        model = input.parents();
        table = model.find('#fileTable');
        rows = table.find('tbody tr');
        rows.removeClass('highlight');
        rows.removeClass('lightlight');
        var filteredRows = rows.filter(function(){
            var value = $(this).find('td').text().toLowerCase();
            return value.indexOf(inputContent) === -1;
        });
        /* Clean previous no-result if exist */
        table.find('tbody .no-result').remove();
        /* Show all rows, hide filtered ones */
        rows.show();
        filteredRows.hide();
        /* Prepend no-result row if all rows are filtered */
        if (filteredRows.length === rows.length) {
            table.find('tbody').prepend($('<tr class="no-result text-center"><td colspan="'+ ('#fileFilt').length +'">No result found</td></tr>'));
        }
    });

    $('#userFilt').keyup(function(e){

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
        var filteredRows = rows.filter(function(){
            var value = $(this).find('td').text().toLowerCase();
            return value.indexOf(inputContent) === -1;
        });
        /* Clean previous no-result if exist */
        table.find('tbody .no-result').remove();
        /* Show all rows, hide filtered ones */
        rows.show();
        filteredRows.hide();
        /* Prepend no-result row if all rows are filtered */
        if (filteredRows.length === rows.length) {
            table.find('tbody').prepend($('<tr class="no-result text-center"><td colspan="'+ ('#userFilt').length +'">No result found</td></tr>'));
        }
    });

    $('#sessionFilt').keyup(function(e){

        /* Ignore tab key */
        var code = e.keyCode || e.which;
        if (code == '9') return;
        /* Useful DOM data and selectors */
        var input = $(this);
        inputContent = input.val().toLowerCase();
        model = input.parents();
        table = model.find('#sessionTable');
        rows = table.find('tbody tr');
        rows.removeClass('highlight');
        rows.removeClass('lightlight');
        var filteredRows = rows.filter(function(){
            var value = $(this).find('td').text().toLowerCase();
            return value.indexOf(inputContent) === -1;
        });
        /* Clean previous no-result if exist */
        table.find('tbody .no-result').remove();
        /* Show all rows, hide filtered ones */
        rows.show();
        filteredRows.hide();
        /* Prepend no-result row if all rows are filtered */
        if (filteredRows.length === rows.length) {
            table.find('tbody').prepend($('<tr class="no-result text-center"><td colspan="'+ ('#sessionFilt').length +'">No result found</td></tr>'));
        }
    });
})

$(function()
{
    var rows = $('tr.item')
    rows.on('click', function(e)
    {
        var row = $(this);
        var id = $('td:first', $(row)).attr('id');
        rows.removeClass('highlight');
        rows.removeClass('lightlight');
        row.addClass('highlight');
        if (row.parents('#fileTable').length){
            $('#fileModal').load('/getInfo'+" #fileModal>*",{ id: id, table: "File"}, function(){
                $('#fileModal').modal('show');
            });
        }
        if (row.parents('#nameTable').length){
            $.post( "/getInfo", { id: id, table: "User"}, function(data){
                $('#UserModal').html(data);
            })
            $('#userModal').modal('show');
        }
        if (row.parents('#sessionTable').length){
            $.post( "/getInfo", { id: id, table: "Session"}, function(data){
                $('#sessionModal').html(data);
            })
            $('#sessionModal').modal('show');
        }
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



function Users(){
    $('#fileNav').hide();
    $('#sessionNav').hide();
    $('#userNav').show();
    clearHighlight();
}

function Files(){
    $('#userNav').hide();
    $('#sessionNav').hide();
    $('#fileNav').show();
    clearHighlight();
}

function Sessions(){
    $('#userNav').hide();
    $('#fileNav').hide();
    $('#sessionNav').show();
    clearHighlight();
}

function clearHighlight(){
    var rows = $('tr.item');
    rows.removeClass("highlight")
    rows.removeClass("lightlight")
}