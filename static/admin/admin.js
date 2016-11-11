$(document).ready( function() {
    Users();

    var rows = $('tr.item');
    rows.removeClass("highlight")
    rows.removeClass("lightlight")

    setupRows();
    setupClick();
})

function setupRows(){
    var rows = $('tr.item')
    rows.on('click', function(e){
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

    $('#nestedFileFilt').keyup(function(e){

        /* Ignore tab key */
        var code = e.keyCode || e.which;
        if (code == '9') return;
        /* Useful DOM data and selectors */
        var input = $(this);
        inputContent = input.val().toLowerCase();
        model = input.parents();
        table = model.find('#nestedFileTable');
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
            table.find('tbody').prepend($('<tr class="no-result text-center"><td colspan="'+ ('#nestedFileFilt').length +'">No result found</td></tr>'));
        }
    });

    $('#nestedSessionFilt').keyup(function(e){

        /* Ignore tab key */
        var code = e.keyCode || e.which;
        if (code == '9') return;
        /* Useful DOM data and selectors */
        var input = $(this);
        inputContent = input.val().toLowerCase();
        model = input.parents();
        table = model.find('#nestedSessionTable');
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
            table.find('tbody').prepend($('<tr class="no-result text-center"><td colspan="'+ ('#nestedSessionFilt').length +'">No result found</td></tr>'));
        }
    });

    $('#nestedSUserFilt').keyup(function(e){

        /* Ignore tab key */
        var code = e.keyCode || e.which;
        if (code == '9') return;
        /* Useful DOM data and selectors */
        var input = $(this);
        inputContent = input.val().toLowerCase();
        model = input.parents();
        table = model.find('#nestedSUserTable');
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
            table.find('tbody').prepend($('<tr class="no-result text-center"><td colspan="'+ ('#nestedSUserFilt').length +'">No result found</td></tr>'));
        }
    });

    $('#nestedFUserFilt').keyup(function(e){

        /* Ignore tab key */
        var code = e.keyCode || e.which;
        if (code == '9') return;
        /* Useful DOM data and selectors */
        var input = $(this);
        inputContent = input.val().toLowerCase();
        model = input.parents();
        table = model.find('#nestedFUserTable');
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
            table.find('tbody').prepend($('<tr class="no-result text-center"><td colspan="'+ ('#nestedFUserFilt').length +'">No result found</td></tr>'));
        }
    });

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

    $('#fileUserFilt').keyup(function(e){

        /* Ignore tab key */
        var code = e.keyCode || e.which;
        if (code == '9') return;
        /* Useful DOM data and selectors */
        var input = $(this);
        inputContent = input.val().toLowerCase();
        model = input.parents();
        table = model.find('#fileNameTable');
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
            table.find('tbody').prepend($('<tr class="no-result text-center"><td colspan="'+ ('#fileUserFilt').length +'">No result found</td></tr>'));
        }
    });

   $('#userFileFilt').keyup(function(e){

        /* Ignore tab key */
        var code = e.keyCode || e.which;
        if (code == '9') return;
        /* Useful DOM data and selectors */
        var input = $(this);
        inputContent = input.val().toLowerCase();
        model = input.parents();
        table = model.find('#userFileTable');
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
            table.find('tbody').prepend($('<tr class="no-result text-center"><td colspan="'+ ('#userFileFilt').length +'">No result found</td></tr>'));
        }
    });

   $('#userSessionFilt').keyup(function(e){

        /* Ignore tab key */
        var code = e.keyCode || e.which;
        if (code == '9') return;
        /* Useful DOM data and selectors */
        var input = $(this);
        inputContent = input.val().toLowerCase();
        model = input.parents();
        table = model.find('#userSessionTable');
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
            table.find('tbody').prepend($('<tr class="no-result text-center"><td colspan="'+ ('#userSessionFilt').length +'">No result found</td></tr>'));
        }
    });

   $('#sessionUserFilt').keyup(function(e){

        /* Ignore tab key */
        var code = e.keyCode || e.which;
        if (code == '9') return;
        /* Useful DOM data and selectors */
        var input = $(this);
        inputContent = input.val().toLowerCase();
        model = input.parents();
        table = model.find('#sessionUserTable');
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
            table.find('tbody').prepend($('<tr class="no-result text-center"><td colspan="'+ ('#sessionUserFilt').length +'">No result found</td></tr>'));
        }
    });
}
var waitHighlight = $.Deferred();
function setupClick()
{
    var rows = $('tr.item')
    rows.on('click', function(e)
    {
        var row = $(this);
        var id = $('td:first', $(row)).attr('id');
        rows.removeClass('highlight');
        rows.removeClass('lightlight');
        row.addClass('highlight');
        waitHighlight.resolve();
        if (row.parents('#fileTable').length){
            $('#fileModal').load('/getInfo'+" #fileModal>*",{ id: id, table: "File"}, function(data){
                $('#fileModal').modal('show');
                Files()
                $('#fileTitle').text((row[0].innerText).slice(0, (row[0].innerText).indexOf(" ")) + ' Information');
                localStorage.setItem('location', id);
                setupRows()
            });
        }
        if (row.parents('#nameTable').length){
            var toUser = $.trim($(row).text())
            $('#userModal').load('/getInfo'+" #userModal>*",{ user: toUser, table: "User"}, function(){
                $('#userModal').modal('show');
                Users()
                $('#userTitle').text(row[0].innerText + ' Information');
                localStorage.setItem('location', row[0].innerText);
                setupRows()
            });
        }
        if (row.parents('#sessionTable').length){
            $('#sessionModal').load('/getInfo'+" #sessionModal>*",{ id: id, table: "Session"}, function(){
                $('#sessionModal').modal('show');
                Sessions()
                $('#sessionTitle').text((row[0].innerText).slice(0, (row[0].innerText).indexOf(" ")) + ' Information');
                localStorage.setItem('location', id);
                setupRows()
            });
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

    $('#nestedFUserModal').on('hidden.bs.modal', function (e) {
        $('#fileModal').modal('show');
    })
    $('#nestedSUserModal').on('hidden.bs.modal', function (e) {
        $('#sessionModal').modal('show');
    })
    $('#nestedFileModal').on('hidden.bs.modal', function (e) {
        $('#userModal').modal('show');
    })
    $('#nestedSessionModal').on('hidden.bs.modal', function (e) {
        $('#userModal').modal('show');
    })
}



function Users(){
    $('#fileNav').hide();
    $('#fileFilt').hide();
    $('#sessionNav').hide();
    $('#sessionFilt').hide();
    $('#userNav').show();
    $('#userFilt').show();
    $('#navGroup').removeClass('fileSesNavGroup');
    $('#navGroup').addClass('navGroup');
    clearHighlight();
}

function Files(){
    $('#userNav').hide();
    $('#userFilt').hide();
    $('#sessionNav').hide();
    $('#sessionFilt').hide();
    $('#fileNav').show();
    $('#fileFilt').show();
    $('#navGroup').removeClass('navGroup');
    $('#navGroup').addClass('fileSesNavGroup');
    clearHighlight();
}

function Sessions(){
    $('#userNav').hide();
    $('#userFilt').hide();
    $('#fileNav').hide();
    $('#fileFilt').hide();
    $('#sessionNav').show();
    $('#sessionFilt').show();
    $('#navGroup').removeClass('navGroup');
    $('#navGroup').addClass('fileSesNavGroup');
    clearHighlight();
}

function clearHighlight(){
    var rows = $('tr.item');
    rows.removeClass("highlight")
    rows.removeClass("lightlight")
}

function addThing(button){
    waitHighlight = $.Deferred();
    if ($(button).parents('#nestedFileModal').length){
        var tableType = "#userFileTable";
        var nested = "#nestedFileTable";
        var origin = localStorage.getItem('location');
        var shortID = 'User';
        var nestedMod = "#nestedFileModal"
    }
    else if ($(button).parents('#nestedSessionModal').length){
        var tableType = "#userSessionTable";
        var nested = "#nestedSessionTable";
        var origin = localStorage.getItem('location');
        var shortID = 'User';
    }
    else if ($(button).parents('#nestedFUserModal').length){
        var tableType = "#fileNameTable";
        var nested = "#nestedFUserNav";
        var origin = localStorage.getItem('location');
        var shortID = 'File';
    }
    else{
        var tableType = "#sessionUserTable";
        var nested = "#nestedSUserNav";
        var origin = localStorage.getItem('location');
        var shortID = 'Session';
    }
    $.when(waitHighlight).done(function(){
        $(nested + " tr.item").each(function(){
            var row = $(this);
            if ($(row).hasClass( "highlight" )){
                var fid = $('td:first', $(row)).attr('id');
                var user = row[0].innerText
                $('.modal').modal('hide');
                $.post("/addThing", { id: fid, from: origin, table: tableType, user: user}, function(data){
                    $(tableType).load("/getInfo "+ tableType + ">*", {id: origin, table: shortID, user:data}, function(){
                        $('#basePage').load("/admin #basePage>*", function(){
                            setupRows();
                            setupClick();
                            if (tableType == "#userFileTable"){
                                Users();
                                $('.modal-backdrop').remove();
                                $('#userModal').modal('show');
                            }
                            else if (tableType == "#userSessionTable"){
                                Users();
                                $('.modal-backdrop').remove();
                                $('#userModal').modal('show');
                            }
                            else if (tableType == "#fileNameTable"){
                                Files();
                                $('.modal-backdrop').remove();
                                $('#fileModal').modal('show');
                            }
                            else{
                                Sessions();
                                $('.modal-backdrop').remove();
                                $('#sessionModal').modal('show');
                            }
                        });
                    })
                })
            }
        })
    });
    return waitHighlight.promise()
}

function removeThing(button){
    var found = 0;
    if ($(button).parents('#userFileID').length){
        var tableType = "#userFileTable";
        var origin = localStorage.getItem('location');
        var shortID = 'User';
    }
    else if ($(button).parents('#userSessionID').length){
        var tableType = "#userSessionTable";
        var origin = localStorage.getItem('location');
        var shortID = 'User';
    }
    else if ($(button).parents('#fileUserID').length){
        var tableType = "#fileNameTable";
        var origin = localStorage.getItem('location');
        var shortID = 'File';
    }
    else{
        var tableType = "#sessionUserTable";
        var origin = localStorage.getItem('location');
        var shortID = 'Session';
    }
    $(tableType + " tr.item").each(function(){
    var row = $(this);
    if ($(row).hasClass( "highlight" ))
    {
        found = 1;
        var fid = $('td:first', $(row)).attr('id');
        var user = row[0].innerText
        $.post( "/removeThing", { id: fid, from: origin, table: tableType, user: user}, function(data){
            $(tableType).load("/getInfo "+ tableType + ">*", {id: origin, table: shortID, user: data}, function(){
                $('#basePage').load("/admin #basePage>*", function(){
                    setupRows();
                    setupClick();
                    if (tableType == "#userFileTable"){
                        Users();
                    }
                    else if (tableType == "#userSessionTable"){
                        Users();
                    }
                    else if (tableType == "#fileNameTable"){
                        Files();
                    }
                    else{
                        Sessions();
                    }
                });
            });
        });
    }
    });
    if (found == 0)
    {
        alert('No File Selected')
    }
}

function showInfo(notifID){
    $('#notifModal').load('/notifInfo'+" #notifModal>*", { id: notifID}, function(){
        $('#notifModal').modal('show');
    })
}

function delUser(){
    BootstrapDialog.show({
        title: 'Delete User?',
        message: 'Are you sure you want to delete this User?\n\nThis is a dangerous action.',
        buttons: [{
            label: 'Yes',
            action: function(dialogItself){
                    dialogItself.close();
                    user = localStorage.getItem('location')
                    $.post("/delete", { delUser: user, table: 'User'}, function(){
                        $('#userModal').modal('hide');
                        $('#basePage').load("/admin #basePage>*");
                        $.getScript("/static/admin/admin.js");
                    })
                }
            }, {
            label: 'No',
            action: function(dialogItself){
                dialogItself.close();
            }
        }]
    });
}

function freezeUser(box){
    if (box.checked == false){
        freeze = 0;
    }
    else{
        freeze = 1;
    }
    user = localStorage.getItem('location')
    $.post('/freeze', {'user': user, freeze: freeze})
}

function approve(task){
    $.post('/solveNotif', {id: task, action: 1}, function(){
        $('#notifications').load("/admin #notifications>*");
        $.getScript("/static/admin/admin.js");
    })
}

function decline(task){
    $.post('/solveNotif', {id: task, action: 0}, function(){
        $('#notifications').load("/admin #notifications>*");
        $.getScript("/static/admin/admin.js");
    })
}