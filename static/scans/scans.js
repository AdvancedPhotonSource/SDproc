$x(document).ready(function() {
});

function remove_file() {
    selected = localStorage.getItem('previous2');

    if (selected) {
        alert(selected);
        $x.post("/SDproc/clearPart_cmeta", { id: id });
    } else {
        alert("no file");
    }
}