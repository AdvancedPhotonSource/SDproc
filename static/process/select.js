/*
-    Copyright (c) UChicago Argonne, LLC. All rights reserved.
-
-    Copyright UChicago Argonne, LLC. This software was produced
-    under U.S. Government contract DE-AC02-06CH11357 for Argonne National
-    Laboratory (ANL), which is operated by UChicago Argonne, LLC for the
-    U.S. Department of Energy. The U.S. Government has rights to use,
-    reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR
-    UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
-    ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
-    modified to produce derivative works, such modified software should
-    be clearly marked, so as not to confuse it with the version available
-    from ANL.
-
-    Additionally, redistribution and use in source and binary forms, with
-    or without modification, are permitted provided that the following
-    conditions are met:
-
-        * Redistributions of source code must retain the above copyright
-          notice, this list of conditions and the following disclaimer.
-
-        * Redistributions in binary form must reproduce the above copyright
-          notice, this list of conditions and the following disclaimer in
-          the documentation and/or other materials provided with the
-          distribution.
-
-        * Neither the name of UChicago Argonne, LLC, Argonne National
-          Laboratory, ANL, the U.S. Government, nor the names of its
-          contributors may be used to endorse or promote products derived
-          from this software without specific prior written permission.
-
-    THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS
-    AS IS AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
-    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
-    FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago
-    Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
-    INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
-    BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
-    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
-    CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
-    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
-    ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
-    POSSIBILITY OF SUCH DAMAGE.
*/
function processor(){
    temp1 = $x('#cordData').val()
    var binWidth = $x('#binWidth').val();
    if ($x('#sel1 > tbody > tr').length == 1){
        var ses = localStorage.getItem('usingSes');
        alert(ses);
        localStorage.setItem('previous3', this.value);
        alert(this.value);
        $x.post('/SDproc/process', { idnext: this.value, output: 1, binWidth: binWidth},
        function(data){
            $x('#process_plot').html( $x(data).find('#process_plot').html());
            $x('#cordData').val( $x(data).find('#cordHolder').html());
            $x('#idnum').val(localStorage.getItem('previous3'));
            $x('#outType').val(4);
            $x('#DBSave').val(0);
            $x('#output-form').attr('action', '/SDproc/generateOutput')
            $x.post('/SDproc/generateOutput', $x('#output-form').serialize(), function(data){
                $x.post('/SDproc/setDAT', {DAT: data})
            })
        })

        $x.post('/SDproc/show_comment', { idnext: this.value, format: 1, ses: ses},
        function(data){
            $x('#comment').text(data);
        })
    }
    else{
        var ses = localStorage.getItem('usingSes');
        var ids = []
        $x('#sel1 > tbody > tr.highlight').each(function(){
            ids.push($x(this).data('value'));
        });
        var jIds = JSON.stringify(ids);
        localStorage.setItem('previous3', jIds);

        $x.post('/SDproc/process', {idList: jIds, output: 1, binWidth: binWidth},
        function(data){
            $x('#process_plot').html( $x(data).find('#process_plot').html());
            $x('#cordData').val( $x(data).find('#cordHolder').html());
            $x('#idnum').val(localStorage.getItem('previous3'));
            $x('#outType').val(5);
            $x('#DBSave').val(0);
            $x('#output-form').attr('action', '/SDproc/generateOutput')
            $x.post('/SDproc/generateOutput', $x('#output-form').serialize(), function(data){
                $x.post('/SDproc/setDAT', {DAT: data})
            })
        });
    }
}

function startProc(){
    processor();
    $x('#settingsBtn').show();
    $x('#outputBtn').prop('disabled', false);
    $x('#continue').prop('disabled', false);
    $x('#logbook').prop('disabled', false);
    //setcDAT();
}


$x(document).ready( function() {
    asynchOnLoad()
    $x('#settingsBtn').hide();
    $x('#outputBtn').prop('disabled', true);
    $x('#continue').prop('disabled', true);
    $x('#logbook').prop('disabled', true);
    $x('#linearRad').prop("checked", true)
    $x('#binWidth').attr('placeholder', 'Input width of bins');
    $x('#binWidth').prop('disabled', true);
    $x('#logbtn').prop('disabled', false);
    if (!localStorage.getItem('previous3') === null)
        localStorage.removeItem("previous3");
    if (localStorage.getItem('pltStat') === null)
        localStorage.setItem('pltStat', 1);
})

function asynchOnLoad(){
    var deferred = new $x.Deferred(), completed = deferred.then(function(){
        $x('#sel1 > tbody > tr > td > input').each(function(){
            if ($x(this).is(':checked')){
                $x(this).parent().parent().addClass('highlight');
            }
        });
        sortTable($x('#sel1'));
        return 1;
    });
    if (localStorage.getItem('use_files')){
        $x.post("/SDproc/make_name", {ids: localStorage.getItem('use_files')},
        function(data){
            data = JSON.parse(data)
            for(i = 0; i < data.length; i++){
                if (data[i][1] == true){
                    $x('#sel1 > tbody:last-child')
                    .append('<tr style="cursor: pointer;" data-value="'+data[i][2]+'" class="file"><td class="fileNameCell">' + data[i][0] + '<td><input onclick="updateSumCheck(this)" checked type="checkbox"></td></tr>')
                }
                else{
                    $x('#sel1 > tbody:last-child')
                    .append('<tr style="cursor: pointer;" data-value="'+data[i][2]+'" class="file"><td class="fileNameCell">' + data[i][0] + '<td><input onclick="updateSumCheck(this)" type="checkbox"></td></tr>')
                }
            }
            $x('#pane').show();
            deferred.resolve();
        })
    }
    return deferred.promise()
}

function updateSumCheck(checkbox){
    if ($x(checkbox).is(':checked')){
        idnum = $x(checkbox).parent().parent().data('value');
        $x(checkbox).parent().parent().addClass('highlight');
        $x.post('/SDproc/updateSumCheck', {id: idnum, check: "True"});
    }
    else{
        idnum = $x(checkbox).parent().parent().data('value');
        $x(checkbox).parent().parent().removeClass('highlight');
        $x.post('/SDproc/updateSumCheck', {id: idnum, check: "False"});
    }
}

function removeID(id, idArray){
    var result = $x.grep(idArray, function(n, i){
        return (n !== id);
    })
    return result;
}


$x(window).on('unload', function(){
//    $x.post('/SDproc/close_plots');
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
    $x.post('/SDproc/add_entry', {process: 1},
    function(){
        $x('#log_add').text('Added');
        $x('#log_add').fadeOut(1000);
        $x('#logbtn').prop('disabled', true);
    })
}

function saveSettings(){
    if ($x('#binRad').is(':checked')){
        var id = JSON.parse(localStorage.getItem('previous3'));
        var binWidth = $x('#binWidth').val();
        if ($x.isNumeric(binWidth)){
            if (id.length > 1){
                var id = JSON.stringify(id);
                $x.post('/SDproc/process', { idList: id , binWidth: binWidth},
                    function(data){
                        $x('#process_plot').html( $x(data).find('#process_plot').html());
                        $x('#maxes').html( $x(data).find('#maxes').html());
                        $x('#maxVal').html( $x(data).find('#maxVal').html());
                    })
                $x('#ssModal').modal('hide');
            }
            else{
                $x.post('/SDproc/process', { idnext: id , binWidth: binWidth},
                    function(data){
                        $x('#process_plot').html( $x(data).find('#process_plot').html());
                        $x('#maxes').html( $x(data).find('#maxes').html());
                        $x('#maxVal').html( $x(data).find('#maxVal').html());
                    })
                $x('#ssModal').modal('hide');
            }
            $x('#logbtn').prop('disabled', false);
        }
        else
        {
            alert('Please enter a bin width')
        }
    }
    else
    {
        processor();
    }
}


$x(function (){
    $x('input[type=radio][name=methodRad]').on('change', function(event){
        if ($x('#binRad').is(':checked')){
            $x('#binWidth').prop('disabled', false);
        }
        if ($x('#linearRad').is(':checked')){
            $x('#binWidth').prop('disabled', true);
        }
    })
})

function setcDAT(){
    id = localStorage.getItem('previous3');
    var binWidth = $x('#binWidth').val();
    temp1 = $x('#cordData').val()
    if ($x('#sel1').val().length == 1){
        $x.post('/SDproc/process', {idnext: id , output: 1, binWidth: binWidth}, function(data){
            $x('#idnum').val(id);
            temp = $x('#cordData').val()
            $x('#cordData').val(data);
            $x('#outType').val(4);
            $x('#DBSave').val(0);
            $x('#output-form').attr('action', '/SDproc/generateOutput')
            $x.post('/SDproc/generateOutput', $x('#output-form').serialize(), function(data){
                $x.post('/SDproc/setDAT', {DAT: data})
            })
        })
    }
    else{
        $x.post('/SDproc/process', {idList: id , output: 1, binWidth: binWidth}, function(data){
            $x('#idnum').val(id);
            $x('#cordData').val(data);
            $x('#outType').val(5);
            $x('#DBSave').val(0);
            $x('#output-form').attr('action', '/SDproc/generateOutput')
            $x.post('/SDproc/generateOutput', $x('#output-form').serialize(), function(data){
                $x.post('/SDproc/setDAT', {DAT: data})
            })
        })
    }
}

function sortTable(table){
    tbody = table.find('tbody')
    tbody.find('tr').sort(function(a, b){
        return $x('td:first', a).text().localeCompare($x('td:first', b).text());
    }).appendTo(tbody);
}


function logout(){
    if (localStorage.getItem('previous3') === null){
        window.location.href = ("logout");
    }
    else{
        previous = localStorage.getItem('previous3');
        $x.post("/SDproc/save_comment", { idprev: previous, comment: $x('#comment').val(), format: 1}, function(){
            window.location.href = ("logout")
        });
    }
}




function advance(){
    window.location.href = ("modifyDAT");
}

function outputFile(){
    if (localStorage.getItem('previous3') === null){
        alert('No file loaded');
    }
    else{
        BootstrapDialog.show({
            title: 'Save Options',
            message: function(dialog){
                var $xcontent = $x('<input type="text" id="DATname" placeholder="Name of DAT file">')
                return $xcontent
            },
            buttons: [{
                label: 'Save to Server',
                action: function(dialogItself){
                    if ($x('#binRad').is(':checked')){
                        var binWidth = $x('#binWidth').val();
                        if ($x('#sel1').val().length == 1){
                            id = localStorage.getItem('previous3');
                            $x.post('/SDproc/process', {idnext: id , output: 1, binWidth: binWidth}, function(data){
                                $x('#idnum').val(id);
                                $x('#cordData').val($x(data).find('#cordHolder').html());
                                $x('#outType').val(4);
                                $x('#DBSave').val(1);
                                $x('#output-form').attr('action', '/SDproc/generateOutput')
                                $x('#datFName').val($x('#DATname').val())
                                if (jQuery.type($x('#DATname').val()) === "string" && $x('#DATname').val().length > 0){
                                    $x.post('/SDproc/generateOutput', $x('#output-form').serialize(), function(data){
                                        $x.post('/SDproc/setDAT', {DAT: data, DName: $x('#DATname').val()}, function(){
                                            dialogItself.close();
                                            alert('Saved');
                                        });
                                    });
                                }
                                else{
                                    alert('Enter a name for the DAT file')
                                }
                            });
                        }
                        else{
                            var ids = []
                            $x('#sel1 > tbody > tr.highlight').each(function(){
                                ids.push($x(this).data('value'));
                            })
                            var jIds = JSON.stringify(ids);
                            $x.post('/SDproc/process', {idList: jIds, output: 1, binWidth: binWidth}, function(data){
                                $x('#idnum').val(jIds);
                                $x('#cordData').val($x(data).find('#cordHolder').html());
                                $x('#outType').val(5);
                                $x('#DBSave').val(1);
                                $x('#output-form').attr('action', '/SDproc/generateOutput')
                                $x('#datFName').val($x('#DATname').val())
                                if (jQuery.type($x('#DATname').val()) === "string" && $x('#DATname').val().length > 0){
                                    $x.post('/SDproc/generateOutput', $x('#output-form').serialize(), function(data){
                                        $x.post('/SDproc/setDAT', {DAT: data, DName: $x('#DATname').val()}, function(){
                                            dialogItself.close();
                                            alert('Saved');
                                        });
                                    });
                                }
                                else{
                                    alert('Enter a name for the DAT file')
                                }
                            });
                        }
                    }
                    else{
                        if ($x('#sel1').val().length == 1){
                            id = localStorage.getItem('previous3');
                            $x.post('/SDproc/process', {idnext: id , output: 1}, function(data){
                                $x('#idnum').val(id);
                                $x('#cordData').val($x(data).find('#cordHolder').html());
                                $x('#outType').val(4);
                                $x('#DBSave').val(1);
                                $x('#output-form').attr('action', '/SDproc/generateOutput')
                                $x('#datFName').val($x('#DATname').val())
                                if (jQuery.type($x('#DATname').val()) === "string" && $x('#DATname').val().length > 0){
                                    $x.post('/SDproc/generateOutput', $x('#output-form').serialize(), function(data){
                                        $x.post('/SDproc/setDAT', {DAT: data, DName: $x('#DATname').val()}, function(){
                                            dialogItself.close();
                                            alert('Saved');
                                        });
                                    });
                                }
                                else{
                                    alert('Enter a name for the DAT file')
                                }
                            });
                        }
                        else{
                            var ids = []
                            $x('#sel1 > tbody > tr.highlight').each(function(){
                                ids.push($x(this).data('value'));
                            })
                            var jIds = JSON.stringify(ids);
                            $x.post('/SDproc/process', {idList: jIds, output: 1}, function(data){
                                $x('#idnum').val(jIds);
                                $x('#cordData').val($x(data).find('#cordHolder').html());
                                $x('#outType').val(5);
                                $x('#DBSave').val(1);
                                $x('#output-form').attr('action', '/SDproc/generateOutput')
                                $x('#datFName').val($x('#DATname').val())
                                if (jQuery.type($x('#DATname').val()) === "string" && $x('#DATname').val().length > 0){
                                    $x.post('/SDproc/generateOutput', $x('#output-form').serialize(), function(data){
                                        $x.post('/SDproc/setDAT', {DAT: data, DName: $x('#DATname').val()}, function(){
                                            dialogItself.close();
                                            alert('Saved');
                                        });
                                    });
                                }
                                else{
                                    alert('Enter a name for the DAT file')
                                }
                            });
                        }
                    }
                }
            }, {
                label: 'Save Locally',
                action: function(dialogItself){
                    if ($x('#binRad').is(':checked')){
                        var binWidth = $x('#binWidth').val();
                        if ($x('#sel1').val().length == 1){
                            id = localStorage.getItem('previous3');
                            $x.post('/SDproc/process', {idnext: id , output: 1, binWidth: binWidth}, function(data){
                                $x('#idnum').val(id);
                                $x('#cordData').val($x(data).find('#cordHolder').html());
                                $x('#outType').val(2);
                                $x('#output-form').attr('action', '/SDproc/generateOutput')
                                $x('#datFName').val($x('#DATname').val())
                                if (jQuery.type($x('#DATname').val()) === "string" && $x('#DATname').val().length > 0){
                                    $x('#output-form')[0].submit();
                                    dialogItself.close();
                                }
                                else{
                                    alert('Enter a name for the DAT file')
                                }
                            });
                        }
                        else{
                            var ids = []
                            $x('#sel1 > tbody > tr.highlight').each(function(){
                                ids.push($x(this).data('value'));
                            })
                            var jIds = JSON.stringify(ids);
                            $x.post('/SDproc/process', {idList: jIds, output: 1, binWidth: binWidth}, function(data){
                                $x('#idnum').val(jIds);
                                $x('#cordData').val($x(data).find('#cordHolder').html());
                                $x('#outType').val(3);
                                $x('#output-form').attr('action', '/SDproc/generateOutput')
                                $x('#datFName').val($x('#DATname').val())
                                if (jQuery.type($x('#DATname').val()) === "string" && $x('#DATname').val().length > 0){
                                    $x('#output-form')[0].submit();
                                    dialogItself.close();
                                }
                                else{
                                    alert('Enter a name for the DAT file')
                                }
                            });
                        }
                    }
                    else{
                        if ($x('#sel1').val().length == 1){
                            id = localStorage.getItem('previous3');
                            $x.post('/SDproc/process', {idnext: id , output: 1}, function(data){
                                $x('#idnum').val(id);
                                $x('#cordData').val($x(data).find('#cordHolder').html());
                                $x('#outType').val(2);
                                $x('#output-form').attr('action', '/SDproc/generateOutput')
                                $x('#datFName').val($x('#DATname').val())
                                if (jQuery.type($x('#DATname').val()) === "string" && $x('#DATname').val().length > 0){
                                    $x('#output-form')[0].submit();
                                    dialogItself.close();
                                }
                                else{
                                    alert('Enter a name for the DAT file')
                                }
                            });
                        }
                        else{
                            var ids = []
                            $x('#sel1 > tbody > tr.highlight').each(function(){
                                ids.push($x(this).data('value'));
                            })
                            var jIds = JSON.stringify(ids);
                            $x.post('/SDproc/process', {idList: jIds, output: 1}, function(data){
                                $x('#idnum').val(jIds);
                                $x('#cordData').val($x(data).find('#cordHolder').html());
                                $x('#outType').val(3);
                                $x('#output-form').attr('action', '/SDproc/generateOutput')
                                $x('#datFName').val($x('#DATname').val())
                                if (jQuery.type($x('#DATname').val()) === "string" && $x('#DATname').val().length > 0){
                                    $x('#output-form')[0].submit();
                                    dialogItself.close();
                                }
                                else{
                                    alert('Enter a name for the DAT file')
                                }
                            })
                        }
                    }
                }
            }]
        })
    }
}