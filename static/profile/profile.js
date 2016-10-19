function updateProf(){
    var proChar = 0;
    var proPass = 0;
    var proEmail = 0;
    if ($('#proChar').val().length > 0){
        proChar = $('#proChar').val();
    }
    if ($('#proPass').val().length > 0){
        proPass = $('#proPass').val();
    }
    if ($('#proEmail').val().length > 0){
        proEmail = $('#proEmail').val();
    }

    $.post('/updateProf', {comChar: proChar, pass: proPass, email: proEmail}, function(){
        $('#profileInfo').load(location.href+" #profileInfo>*","");
    });
}