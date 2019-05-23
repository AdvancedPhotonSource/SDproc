$(document).ready(function(){

     $("#tree").jstree({
        'core' : {
            'data' : {
               "url" : "scans_data",
               "dataType" : "json"
            }
        },
        'types' : {
            'Folder' : { "icon" : "/static/images/root.png" },
            'File' : { "icon" : "jstree-icon jstree-file", "valid_children" : [] },
            'Root' : { "icon" : "static/images/root.png" }
        },
        'plugins' : [ "wholerow", "unique", "types" ]
    })
    .on("select_node.jstree", function (e, data) {
        graph(data.node.id, data.node.text);
        show_table(data.node.id, data.node.text);
    });
});

function sortTable(table) {
    tbody = table.find('tbody')
    tbody.find('tr').sort(function(a, b){
        return $('td:first', a).text().localeCompare($('td:first', b).text());
    }).appendTo(tbody);
}

function show_table(file_id, file_name) {
    $('#sel1 > tbody:last-child')
            .append('<tr style="cursor: pointer;" data-value="'+ file_id +'" class="file"><td class="fileNameCell">' + file_name + '</td><td><input checked onclick="updateSumCheck(this)" type="checkbox"></td></tr>');
    $('#pane').show();
    if (localStorage.getItem('use_files') === null) {
        var files = [];
        files.push(file_id);
        localStorage.setItem('use_files', JSON.stringify(files));
    } else {
        var files = JSON.parse(localStorage.getItem('use_files'));
        files.push(file_id);
        localStorage.setItem('use_files', JSON.stringify(files));
    }
    $('#fileModal').modal('toggle');
    sortTable($('#sel1'));
}

function graph(file_id, file_name) {
    var ses = localStorage.getItem('usingSes');
        $('#fileName').text(file_name);
        if (localStorage.getItem('previous2') === null)
        {
            localStorage.setItem('previous2', file_id);
            $.post('/SDproc/data', { idnext: file_id , plot: 1},
            function(data){
                $('#metaForm_id').html( $(data).find('#metaForm_id').html());
                $('#plot_spot').html( $(data).find('#plot_spot').html());
                $('#currentAE').html( $(data).find('#currentAE').html());
                $.post('/SDproc/show_comment', { idnext: localStorage.getItem('previous2'), format: 1, ses: ses},
                function(data){
                    $('#comment').val(data)
                    setPlotAgainst();
                })
            })
        }
        else
        {
            var nextID = file_id
            previous = localStorage.getItem('previous2');
            $('#idnum').val(previous);
            localStorage.setItem('previous2', file_id);
            $('#meta-form').submit();
            $.post( "/SDproc/save_comment", { idprev: previous, comment: $('#comment').val(), format: 1},
            function(){
                $.post('/SDproc/show_comment', { idnext: nextID, format: 1, ses: ses},
                function(data){
                    $('#comment').val(data)
                    setPlotAgainst();
                })
            })
        }
}