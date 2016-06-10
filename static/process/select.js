$(function (){
    $('#sel1').on('change', function(event){
        if ($('#sel1').val().length == 1){
            var ses = localStorage.getItem('usingSes');
            localStorage.setItem('previous3', this.value);
            $.post('/process', { idnext: this.value },
            function(data){
                $('#process_plot_spot').html( $(data).find('#process_plot_spot').html());
                $('#maxVal').html( $(data).find('#maxVal').html());
            })

            $.post('/show_comment', { idnext: this.value, format: 1, ses: ses},
            function(data){
                $('#comment').text(data);
            })
        }
        else{
            var ses = localStorage.getItem('usingSes');
            var ids = []
            $('#sel1 > option:selected').each(function(){
                ids.push(this.value);
            })
            //localStorage.setItem('previous3', this.value);
            var jIds = JSON.stringify(ids);
            $.post('/process', { idList: jIds },
            function(data){
                $('#process_plot_spot').html( $(data).find('#process_plot_spot').html());
                $('#maxVal').html( $(data).find('#maxVal').html());
                $('#comment').text('');
            });
        }
    });
})


$(document).ready( function() {
    asynchOnLoad()
    if (!localStorage.getItem('previous3') === null)
        localStorage.removeItem("previous3")
})

function asynchOnLoad(){
    var deferred = new $.Deferred(), completed = deferred.then(function(){
        $('#sel1 option:first').prop('selected', true);
        $('#sel1').trigger('change');
        return 1;
    });
    var saved_files = JSON.parse(localStorage.getItem('use_files'));
    $(saved_files).each(function(){
        var temp = this
        $.post("/make_name", {id: this},
        function(data){
        $('#sel1')
            .append($('<option></option')
            .text(data)
            .attr('value', temp))

        saved_files = removeID(temp.valueOf(), saved_files);
        if (saved_files.length == 0){
            deferred.resolve();
        }
        })
    })
    return deferred.promise()
}

function removeID(id, idArray){
    var result = $.grep(idArray, function(n, i){
        return (n !== id);
    })
    return result;
}


$(window).on('unload', function(){
    $.post('/close_plots');
    if (localStorage.getItem('previous3') === null)
    {
        return;
    }
    else
    {
        localStorage.removeItem('previous3');
    }
})

function log(){
    previous = localStorage.getItem('previous3');
    $.post('/add_entry', {id : previous},
    function(){
        $('#log_add').text('Added');
        $('#log_add').fadeOut(1000);
    })
}




