$x(document).ready(function(){
          $x("#search").on("keyup", function() {
            var value = $x(this).val().toLowerCase();
            $x("#sessionTable tr").filter(function() {
              $x(this).toggle($x(this).text().toLowerCase().indexOf(value) > -1)
            });
          });

          $x(".click-able").click(function() {
            $x(this).addClass('active').siblings().removeClass('active');
            var type = $x(this)[0].getAttribute("type");

            $x.post('/SDproc/get_session_comment', { id: $x(this).attr('id'), type: type },
                function(data) {
                    $x('#comment').val(data);
                });
          });

          $x(".click-user").click(function() {
            $x(this).addClass('active').siblings().removeClass('active');
          });
        });

function continue_session() {
    var table = document.getElementById('sessionTable');
    var selected = false;
    var id = null;
    var type = null;

    for (var i = 0, row; row = table.rows[i]; i++) {
        if (row.classList.contains('active')) {
            selected = true;
            id = $x(row).attr('id');
            type = $x(row)[0].getAttribute("type");
        }
    }

    if (!selected) {
        alert('Please select a session or data file.');
    } else {
        $x.post("/SDproc/continue_session", { type: type, id: id }, function(data){
            if (type == 'dat') {
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

    if (!selected) {
        alert('Please select a session or data file.');
    } else {

        $x("#deleteModal").modal('show');
        document.getElementById("delete-modal-body").innerHTML = "Are you sure you want to delete " + name + "?";
    }
 }

function share_modal() {
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

    if (!selected) {
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

    var session_id = null;
    var session_type = null;
    var session_table = document.getElementById('sessionTable');
    for (var i = 0, row; row = session_table.rows[i]; i++) {
        if (row.classList.contains('active')) {
            session_id = $x(row).attr('id');
            session_type = $x(row)[0].getAttribute("type");
        }
    }



    if (!selected) {
        alert('Please select a user.');
    } else {
        $x("#shareModal").modal('hide');
        $x.post("/SDproc/share_session", { user_id: user_id, type: session_type, session_id: session_id })
        .done(function() {
            document.location.reload(); // refreshes the whole page but just want to refresh the table
        });
    }
}

function delete_session(type, id) {
    var table = document.getElementById('sessionTable');
    var selected = false;
    var id = null;
    var type = null;

    for (var i = 0, row; row = table.rows[i]; i++) {
        if (row.classList.contains('active')) {
            selected = true;
            id = $x(row).attr('id');
            type = $x(row)[0].getAttribute("type");
            if (type == null) {
                type = "session"
            }
        }
    }

    $x("#deleteModal").modal('hide');
    $x.post("/SDproc/delete_session", { type: type, id: id })
    .done(function() {
        document.location.reload(); // refreshes the whole page but just want to refresh the table
    });
}

function save_comment() {
    var table = document.getElementById('sessionTable');
    var selected = false;
    var id = null;
    var type = null;

    for (var i = 0, row; row = table.rows[i]; i++) {
        if (row.classList.contains('active')) {
            selected = true;
            id = $x(row).attr('id');
            type = $x(row)[0].getAttribute("type");
        }
    }

    if (!selected) {
        alert('Please select a session or data file.');
    } else {
        var comment = document.getElementById("comment").value;
        $x.post("/SDproc/save_session_comment", { type: type, id: id, comment: comment })
    }
}