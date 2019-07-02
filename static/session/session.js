$x(document).ready(function() {
    $x("#search").on("keyup", function() {
        var value = $x(this).val().toLowerCase();
        $x("#sessionTable tr").filter(function() {
            $x(this).toggle($x(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    $x(".click-able").click(function() {
        $x(this).addClass('active').siblings().removeClass('active');
        var type = $x(this)[0].getAttribute("type");
        $x.post('/SDproc/get_session_comment', { id: $x(this).attr('id'), type: type }, function(data) {
            $x('#comment').val(data);
        });
    });

    $x(".click-user").click(function() {
        $x(this).addClass('active').siblings().removeClass('active');
    });
});


function get_selected() {
    var table = document.getElementById('sessionTable');
    var selected = false;
    var id = null;
    var type = null;
    var name = null;

    for (var i = 0, row; row = table.rows[i]; i++) {
        if (row.classList.contains('active')) {
            selected = true;
            id = $x(row).attr('id');
            type = $x(row)[0].getAttribute("type");
            name = $x(row)[0].getAttribute("name");
        }
    }

    return {
        selected: selected,
        id: id,
        type: type,
        name: name,
    }
}

function continue_session() {
    var values = get_selected();

    if (!values.selected) {
        alert('Please select a session or data file.');
    } else {
        $x.post("/SDproc/continue_session", { type: values.type, id: values.id }, function(data){
            if (values.type == 'dat') {
                localStorage.setItem("usingSes", 0);
                localStorage.setItem("usingDAT", 1);
                document.location.href="/SDproc/modifyDAT";
            } else {
                localStorage.setItem("usingDAT", 0);
                var parsed = $x.parseJSON(data);
                var files = [];
                $x(parsed).each(function() {
                    files.push(this);
                });
                localStorage.setItem('use_files', JSON.stringify(files));
                localStorage.setItem('usingSes', 1);
                window.location.href = ("data");
            }
        });
    }
}

function new_session() {
    document.location.href="/SDproc/data";
    $x.post('/SDproc/new_session2');
}

function delete_modal() {
    var values = get_selected();

    if (!values.selected) {
        alert('Please select a session or data file.');
    } else {
        $x("#deleteModal").modal('show');
        document.getElementById("delete-modal-body").innerHTML = "Are you sure you want to delete " + values.name + "?";
    }
}

function share_modal() {
    var values = get_selected();

    if (!values.selected) {
        alert('Please select a session or data file.');
    } else {
        $x("#shareModal").modal('show');
    }
}

function share_session() {
    var table = document.getElementById('usersTable');
    var selected = false;
    var user_id = null;

    for (var i = 0, row; row = table.rows[i]; i++) {
        if (row.classList.contains('active')) {
            selected = true;
            user_id = $x(row).attr('id');
        }
    }

    var values = get_selected();

    if (!values.selected) {
        alert('Please select a user.');
    } else {
        $x("#shareModal").modal('hide');
        $x.post("/SDproc/share_session", { user_id: user_id, type: values.type, session_id: values.id })
        .done(function() {
            document.location.reload(); // refreshes the whole page but just want to refresh the table
        });
    }
}

function delete_session(type, id) {
    var values = get_selected();

    $x("#deleteModal").modal('hide');
    $x.post("/SDproc/delete_session", { type: values.type, id: values.id })
    .done(function() {
        document.location.reload(); // refreshes the whole page but just want to refresh the table
    });
}

function save_comment() {
    var values = get_selected();

    if (!values.selected) {
        alert('Please select a session or data file.');
    } else {
        var comment = document.getElementById("comment").value;
        $x.post("/SDproc/save_session_comment", { type: values.type, id: values.id, comment: comment })
    }
}