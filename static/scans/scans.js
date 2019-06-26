$x(document).ready(function() {
});

function remove_file() {
    var table = document.getElementById('sel1');
    var selected = false;
    var id = null;

    for (var i = 0, row; row = table.rows[i]; i++) {
        if (row.classList.contains('highlight')) {
            selected = true;
            id = $x(row).attr('data-value');
        }
    }

    if (selected) {
        alert(id);
        $x.post("/SDproc/remove_current_meta", { id: id });
    } else {
        alert("no file");
    }
}