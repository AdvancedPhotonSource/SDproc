$x(document).ready(function(){
    var HRM = document.getElementById("HRM");
    HRM.style.display = "none"; // fix this with CSS instead

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
    });

    $x(".click-hrm").click(function() {
        $x(this).addClass('active').siblings().removeClass('active');
    });
});

function show_user() {
    var user = document.getElementById("user");
    var HRM = document.getElementById("HRM");

    HRM.style.display = "none";
    user.style.display = "block";
}

function show_HRM() {
    var user = document.getElementById("user");
    var HRM = document.getElementById("HRM");

    user.style.display = "none";
    HRM.style.display = "block";
}