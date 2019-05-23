$x(document).ready(function(){
          $x("#search").on("keyup", function() {
            var value = $(this).val().toLowerCase();
            $("#sessionTable tr").filter(function() {
              $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
            });
          });

          $x(".click-able").click(function() {
            $x(this).addClass('active').siblings().removeClass('active');
            var type = null;
            if ($x(this)[0].getAttribute("type") == null) {
                type = "session";
            } else {
                type = "dat"
            }
            $x.post('/session_comment', { id: $x(this).attr('id'), type: type },
                function(data) {
                    $x('#comment').val(data);
                });
          });
        });

 function delete_modal() {
    var table = document.getElementById('sessionTable');
    var selected = false;

    for (var i = 0, row; row = table.rows[i]; i++) {
        if (row.classList.contains('active')) {
            selected = true;
        }
    }

    if (!selected) {
        alert('Please select a session or data file.');
    } else {

        $x("#exampleModalCenter").modal('show');
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

    $x("#exampleModalCenter").modal('hide');
    $x.post("/delete_session", { type: type, id: id })
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
            if (type == null) {
                type = "session"
            }
        }
    }

    if (!selected) {
        alert('Please select a session or data file.');
    } else {
        var comment = document.getElementById("comment").value;
        $x.post("/save_session_comment", { type: type, id: id, comment: comment })
    }
}