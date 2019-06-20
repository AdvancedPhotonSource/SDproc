$x(document).ready(function(){
//    var HRM = document.getElementById("HRM");
//    HRM.style.display = "none"; // fix this with CSS instead

    $x("#searchUser").on("keyup", function() {
        var value = $x(this).val().toLowerCase();
        $x("#userTable tr").filter(function() {
            $x(this).toggle($x(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    $x("#searchHRM").on("keyup", function() {
        var value = $x(this).val().toLowerCase();
        $x("#hrmTable tr").filter(function() {
            $x(this).toggle($x(this).text().toLowerCase().indexOf(value) > -1)
        });
    });

    $x(".click").click(function() {
        $x(this).addClass('active').siblings().removeClass('active');
    });

    $x(".click-user").click(function() {
        $x(this).addClass('active').siblings().removeClass('active');
        var modal = $x(this)[0].getAttribute('name');
        $x('#userModal-' + modal).modal('show');
    });

    $x(".click-hrm").click(function() {
        $x(this).addClass('active').siblings().removeClass('active');
        var modal = $x(this)[0].getAttribute('name');
        $x('#' + modal).modal('show');
    });
});

function show_user() {
    var user = document.getElementById("user");
    var HRM = document.getElementById("HRM");
    var search_bar = document.getElementById("searchUser");

    search_bar.value = "";
    $x("#userTable tr").filter(function() {
            $x(this).toggle($x(this).text().toLowerCase().indexOf(search_bar.value) > -1)
        });
    HRM.style.display = "none";
    user.style.display = "block";
}

function show_HRM() {
    var user = document.getElementById("user");
    var HRM = document.getElementById("HRM");
    var search_bar2 = document.getElementById("searchHRM");
    search_bar2.value = "";
    $x("#hrmTable tr").filter(function() {
            $x(this).toggle($x(this).text().toLowerCase().indexOf(search_bar2.value) > -1)
        });

    user.style.display = "none";
    HRM.style.display = "block";
}

function decline(notification_id) {
    $x.post("/SDproc/decline_user", { notification_id: notification_id })
    .done(function (d) {
        location.reload();
    });
}

function approve(notification_id) {
    $x.post("/SDproc/approve_user", { notification_id: notification_id })
    .done(function (d) {
        location.reload();
    });
}
