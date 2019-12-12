$y(document).ready(function() {

     $y("#file_tree").jstree({
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
        'plugins' : [ "dnd", "contextmenu", "wholerow", "sort", "types", "unique" ]
    })
    .on('rename_node.jstree', function (e, data) {
        $y.post("/SDproc/renameN", { node: data.node.id, newName: data.text });
    })
    .on('create_node.jstree', function (e, data) {
        $y.post("/SDproc/createNode", { parent: data.node.parent, title: data.node.text })
            .done(function (d) {
                data.instance.set_id(data.node, Number(d));
            });
    })
    .on('move_node.jstree', function (e, data) {
        $y.post("/SDproc/moveNode", { parent: data.parent, node: data.node.id });
    })
    .on('delete_node.jstree', function (e, data) {
        $y.post("/SDproc/deleteNode", { nodes: JSON.stringify(data.node.children_d), node: data.node.id });
    })
    .on("select_node.jstree", function (e, data) {
        $y.post('/SDproc/get_file_comments', { id: data.node.id },
                function(data){
                    $y('#comment').val(data);
                });
    });

    $y("#globus_tree").jstree({
        'core' : {
            'data' : {
               "url" : "globus_tree",
               "dataType" : "json"
            }
        },
        'types' : {
            'Folder' : { "icon" : "/static/images/root.png" },
            'File' : { "icon" : "jstree-icon jstree-file", "valid_children" : [] },
            'Root' : { "icon" : "static/images/root.png" }
        },
        'plugins' : [ "wholerow", "types", "sort" ]
    });
});

function download() {
    if ($y("#globus_tree").jstree("get_selected") == false) {
        alert("Please select a file.")
    } else {
        var files = $y("#globus_tree").jstree("get_selected");
        for(var x = 0; x < files.length; x++) {
            $y.post("/SDproc/globus_file", { f_id: files[x] }).done(function (d) {
                $y('#file_tree').jstree(true).refresh();
            });
        }
        $x("#globusModal").modal("hide");
    }
}

function saveNewComment() {
    if ($y("#file_tree").jstree("get_selected") == false) {
        alert("Please select a file or folder to view comment(s) or save new comment(s).")
    } else {
        var nodeID = $y("#file_tree").jstree("get_selected")[0];
        var x = document.getElementById("comment").value;
        $y.post("/SDproc/save_file_comments", { id : nodeID, comment : x });
    }
}