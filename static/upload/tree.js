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

    $y("#3id_tree").jstree({
        'core' : {
            'data' : {
               "url" : "3id_tree",
               "data" : function (node) {
                    return { "id" :  node.id };
                },
                "dataType" : "json"
            }
        },
        'types' : {
            'Folder' : { "icon" : "/static/images/root.png" },
            'File' : { "icon" : "jstree-icon jstree-file", "valid_children" : [] },
            'Root' : { "icon" : "static/images/root.png" }
        },
        'plugins' : [ "types", "sort" ]
    });

    $y("#30id_tree").jstree({
        'core' : {
            'data' : {
               "url" : "30id_tree",
               "data" : function (node) {
                    return { "id" :  node.id };
                },
                "dataType" : "json"
            }
        },
        'types' : {
            'Folder' : { "icon" : "/static/images/root.png" },
            'File' : { "icon" : "jstree-icon jstree-file", "valid_children" : [] },
            'Root' : { "icon" : "static/images/root.png" }
        },
        'plugins' : [ "types", "sort" ]
    });
});

function deselect() {
    $y("#3id_tree").jstree().deselect_all(true);
    $y("#30id_tree").jstree().deselect_all(true);
}

function download() {
    if ($y("#3id_tree").jstree("get_selected") == false && $y("#30id_tree").jstree("get_selected") == false) {
        alert("Please select a file.")
    } else {
        if ($y("#3id_tree").jstree("get_selected") == "") {
            var files = $y('#30id_tree').jstree("get_selected", true);
            var station = "30ID";
        } else if ($y("#30id_tree").jstree("get_selected") == "") {
            var files = $y('#3id_tree').jstree("get_selected", true);
            var station = "3ID";
        }

        for(var x = 0; x < files.length; x++) {
            var fileType = files[x].text.substr(files[x].text.length - 3);
            if (files[x].type == 'File' && (fileType == 'mda' || fileType == 'dat' || fileType == 'txt')) {
                $y.post('/SDproc/get_dm_file', { path: files[x].data.path, exp: files[x].data.expName, type: fileType,
                 parents: String(files[x].parents), station: station })
                .done(function (d) {
                    $y('#file_tree').jstree(true).refresh();
                });
            }
        }
        $x("#modal_3id").modal("hide");
        $x("#modal_30id").modal("hide");
        deselect();
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