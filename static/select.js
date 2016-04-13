$(document).ready( function() {
    populateView()

})

function populateView()
{
    var saved_files = JSON.parse(localStorage.getItem('use_files'));
    $(saved_files).each(function(){
        var temp = this
        $.post("/make_name", {id: this},
        function(data){
        //idval = parseInt(temp);
        $('#sel1')
            .append($('<option></option')
            .text(data)
            .attr('value', temp))
        })
    })
}

function log(){
    previous = localStorage.getItem('previous2');
    $.post('/add_entry', {id : previous},
    function(){
        $('#log_add').text('Added');
        $('#log_add').fadeOut(1000);
    })
}


$(function(){
    $('#meta-form').on('submit', function(event){
        event.preventDefault();
        $.post('/save_graph', $(this).serialize(),
        function(){
            nextID = localStorage.getItem('previous2');
            $.post('/data', { idnext: nextID , plot: 1},
            function(data){
                $.getScript( "https://gitcdn.github.io/bootstrap-toggle/2.2.2/js/bootstrap-toggle.min.js" );
                $('#metaForm_id').html( $(data).find('#metaForm_id').html());
                $('#plot_spot').html( $(data).find('#plot_spot').html());
            })
        });
    });
})


$(function(){
    $('#meta-form').on('change', function(event){
        previous = localStorage.getItem('previous2');
        $('#idnum').val(previous);
        $.post('/save_graph', $('#meta-form').serialize(),
        function(){
            $.post('/data', { idnext: previous , plot: 1},
            function(data){
                $.getScript( "https://gitcdn.github.io/bootstrap-toggle/2.2.2/js/bootstrap-toggle.min.js" );
                $('#metaForm_id').html( $(data).find('#metaForm_id').html());
                $('#plot_spot').html( $(data).find('#plot_spot').html());
            })
        })
    })
})

$(function(){
    $('#comment').on('change', function(){
        previous = localStorage.getItem('previous2');
        $('#idnum').val(previous);
        $.post('/save_comment', {idprev: previous, comment: $('#comment').val(), format: 1});
    })
})



$(function ()
{
        $('#sel1').on('change', function(event){
        var temp = event.target.value;
        if (localStorage.getItem('previous2') === null)
        {
            localStorage.setItem('previous2', this.value);
            $.post('/data', { idnext: this.value , plot: 1},
            function(data){
                $.getScript( "https://gitcdn.github.io/bootstrap-toggle/2.2.2/js/bootstrap-toggle.min.js" );
                $('#metaForm_id').html( $(data).find('#metaForm_id').html());
                $('#plot_spot').html( $(data).find('#plot_spot').html());
            })

            $.post('/show_comment', { idnext: this.value },
            function(data){
            $('#comment').val(data)
            })
        }
        else
        {
            var nextID = this.value
            previous = localStorage.getItem('previous2');
            $('#idnum').val(previous);
            //$('#meta-form').append("<input type='hidden' name='idnum' value='" + previous + "' />");
            $.post( "/save_comment", { idprev: previous, comment: $('#comment').val()},
            function(){
                $.post('/show_comment', { idnext: nextID },
                function(data){
                    $('#comment').val(data)
                })
            })
            localStorage.setItem('previous2', this.value);
            $('#meta-form').submit();
        }
    });
})
