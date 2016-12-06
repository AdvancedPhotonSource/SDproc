$(document).ready( function() {
    if (jQuery.trim($('#process_plot').text()) == "No DAT selected"){
        alert('Please select or generate a DAT file');
    }
})

function averageRange(){
    BootstrapDialog.show({
        title: 'Average Range',
        message: function(dialog){

            var $form = $('<form></form>');
            var $leftIn = $('<input type="text" id="leftIn" class="floatL leftIn" placeholder="X-Point from plot(meV)">')
            var $rightIn = $('<input type="text" id="rightIn" class="floatL rightIn" placeholder="X-Point from plot(meV)">')


            $form.append('<label class="leftIn">Left Inpoint</label>').append($leftIn)
            $form.append('<br/>').append($leftIn)

            $form.append('<label class="rightIn">Right Inpoint</label>').append($rightIn)
            $form.append('<br/>').append($rightIn)
            return $form;
        },
        buttons: [{
            label: 'Average',
            action: function(dialogItself){
                alert($('#leftIn').val() + ' ' + $('#rightIn').val())
            }
        },{
            label: 'Close',
            action: function(dialogItself){
                dialogItself.close();
            }
        }]
    })
}

function remBackground(){

}