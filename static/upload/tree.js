$y(document).ready(function(){

     $y("#tree").jstree({
        'core' : {
            "check_callback" : function(o, n, p, i, m) {
                if (m && m.dnd && m.pos !== 'i') { return false; }
            },
            'data' : {
               "url" : "jsonData",
               "dataType" : "json"
            }
        },
        'contextmenu' : {
            'items' : function(node) {
                var tmp = $y.jstree.defaults.contextmenu.items();
                delete tmp.ccp;

                if(this.is_disabled(node)) {
                    delete tmp.rename;
                    delete tmp.remove;
                }

                return tmp;
            }
        },
        'dnd' : {
            'is_draggable' : function(node) {


                if(node[0].type == 'Root') {
                    alert("Sorry you cannot move the root directory.");
                    return false;
                }
                return true;
            }
        },
        'types' : {
            'Folder' : { "icon" : "/static/images/root.png" },
            'File' : { "icon" : "jstree-icon jstree-file", "valid_children" : [] },
            'Root' : { "icon" : "static/images/root.png" }
        },
        'plugins' : [ "dnd", "contextmenu", "wholerow", "unique", "types" ]
    })
    .on('rename_node.jstree', function (e, data) {
        $y.post("/SDproc/rename", { node: data.node.id, newName: data.text })
        .done(function (d) {
            $y('#tree').jstree(true).refresh();
        })
    })
    .on('create_node.jstree', function (e, data) {
        $y.post("/SDproc/createNode", { parent: data.node.parent, title: data.node.text })
    })
    .on('move_node.jstree', function (e, data) {
        $y.post("/SDproc/moveNode", { parent: data.parent, node: data.node.id });
    })
    .on('delete_node.jstree', function (e, data) {
        $y.post("/SDproc/deleteNode", { node: data.node.id });
    })
    .on("select_node.jstree", function (e, data) {
        //alert(data.node.id);
        $y.post('/SDproc/show_NewComment', { id: data.node.id },
                function(data){
                    $y('#comment').val(data);
                });
    });


});

function saveNewComment() {
    if ($y("#tree").jstree("get_selected") == false) {
        alert("Please select a file or folder to view comment(s) or save new comment(s).")
    } else {
        var nodeID = $y("#tree").jstree("get_selected")[0];
        var x = document.getElementById("comment").value;
        $y.post("/SDproc/saveNC", { id : nodeID, comment : x });
    }
}