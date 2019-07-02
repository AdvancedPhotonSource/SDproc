'''
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
'''

import mpld3


class InteractiveLegend(mpld3.plugins.PluginBase):
    """"A plugin that allows the user to toggle lines though clicking on the legend"""

    JAVASCRIPT = """
        mpld3.register_plugin("interactive_legend", InteractiveLegend);
        InteractiveLegend.prototype = Object.create(mpld3.Plugin.prototype);
        InteractiveLegend.prototype.constructor = InteractiveLegend;
        InteractiveLegend.prototype.requiredProps = ["line_ids", "labels", "sized", "nameID"];
        InteractiveLegend.prototype.defaultProps = {};
        function InteractiveLegend(fig, props){
           mpld3.Plugin.call(this, fig, props);
        };
        InteractiveLegend.prototype.draw = function(){
            if (this.props.sized == 1){
                var svg = document.getElementsByClassName("mpld3-figure");
                svg[0].setAttribute("viewBox", "0 0 600 480");
                svg[0].setAttribute("width", 700);
                svg[0].setAttribute("height", 600);
            }
            var labels = new Array();
            var lineCount = this.props.labels.length
            for(var i=1; i<=lineCount; i++){
                var obj = {};
                obj.label = this.props.labels[i - 1];
                line = mpld3.get_element(this.props.line_ids[i - 1], this.fig);
                obj.line1 = line
                //point = mpld3.get_element(this.props.line_ids[(i * 2) - 1], this.fig);
                //obj.line2 = point;
                obj.visible = false;
                obj.lineNum = i;
                //var outer = point.parent.baseaxes[0][0].children[1];
                //var points = outer.getElementsByTagName("g");
                //if (typeof InstallTrigger !== 'undefined'){
                    //Firefox
                //    points[i-1].firstChild.style.setProperty('stroke-opacity', 0, 'important');
                //    points[i-1].firstChild.style.setProperty('fill-opacity', 0, 'important');
                //}
                //else if (!!window.chrome && !!window.chrome.webstore){
                    //Chrome
                 //   points[(lineCount)-i].firstChild.style.setProperty('stroke-opacity', 0, 'important');
                 //   points[(lineCount)-i].firstChild.style.setProperty('fill-opacity', 0, 'important');
                //}
                //else{
                    //implement more if needed
                 //   points[i-1].firstChild.style.setProperty('stroke-opacity', 0, 'important');
                 //   points[i-1].firstChild.style.setProperty('fill-opacity', 0, 'important');
                //}

               labels.push(obj);
            }
            var ax = this.fig.axes[0];
            if (this.props.sized == 1){
                var foreign = this.fig.canvas.append('foreignObject')
                                        .attr("name", "legendHolder")
                                        .attr("x", 200)
                                        .attr("y", 30)
                                        .attr("width", 400)
                                        .attr("height", 200)
                                        .append("xhtml:div")
                                        .style("max-height", "180px")
                                        .style("overflow-y", "scroll")

                var legend = foreign.append("svg")
                                        .attr("name", this.props.nameID)
                                        .attr("id", "legendSVG")
                                        .attr("width", 387)
                                        .attr("height", labels.length * 25)
                                        .attr("x", 0)
                                        .attr("y", 0)
            }
            else{
                var legend = this.fig.canvas.append("svg")
                                        .attr("name", this.props.nameID)
                                        .attr("id", "legendSVG")
            }


            legend.selectAll("rect")
                        .data(labels)
                    .enter().append("rect")
                        .attr("height", 10)
                        .attr("width", 25)
                        .attr("x", ax.width+10+ax.position[0] - 150)
                        .attr("y", function(d, i){
                            return ax.position[1] + i * 25 - 10;})
                        .attr("stroke", function(d){
                            return d.line1.props.edgecolor})
                        .attr("class", "legend-box")
                        .style("fill", "white")
                        .on("click", click)

            legend.selectAll("text")
                        .data(labels)
                    .enter().append("text")
                        .attr("x", function(d){
                            return ax.width+10+ax.position[0] + 25 + 15 - 150
                            })
                        .attr("y", function(d, i){
                            return ax.position[1] + i * 25
                            })
                        .text(function(d){return d.label})

            if (this.props.sized == 1){
                legend.selectAll("rect")
                            .attr("x", ax.width+10+ax.position[0] - 400)
                            .attr("y", function(d, i){
                                return ax.position[1] + (i * 25) - 40
                                })

                legend.selectAll("text")
                            .attr("x", ax.width+10+ax.position[0] - 350)
                            .attr("y", function(d, i){
                                return ax.position[1] + (i * 25) - 30
                            })
            }

            if (this.props.sized == 1){
                var boxes = legend.selectAll("rect");
                var lastbox = $x(boxes[0]).last();
                lastbox[0].__onclick();
            }
            else{
                var boxes = legend.selectAll("rect")
                var tempboxes = boxes[0]
                for (var i = 0; i < tempboxes.length; i++){
                    var temp = tempboxes[i];
                    temp.__onclick();
                }

            }


            function click(d, i){
                d.visible = !d.visible;
                d3.select(this)
                    .style("fill", function(d, i){
                        var color = d.line1.props.edgecolor;
                        return d.visible ? color : "white";
                    })
                d3.select(d.line1.path[0][0])
                    .style("stroke-opacity", d.visible? 1 : d.line1.props.alpha)

                //if(d.visible == true){
                    //var outer = d.line2.parent.baseaxes[0][0].children[1];
                    //var points = outer.getElementsByTagName("g");

                    //if (typeof InstallTrigger !== 'undefined'){
                        //Firefox
                        //points[d.lineNum-1].firstChild.style.setProperty('stroke-opacity', 1, 'important');
                        //points[d.lineNum-1].firstChild.style.setProperty('fill-opacity', 1, 'important');
                    //}
                    //else if (!!window.chrome && !!window.chrome.webstore){
                        //Chrome
                       // points[(lineCount)-d.lineNum].firstChild.style.setProperty('stroke-opacity', 1, 'important');
                      //  points[(lineCount)-d.lineNum].firstChild.style.setProperty('fill-opacity', 1, 'important');
                    //}
                    //else{
                        //implement more if needed
                      //  points[d.lineNum-1].firstChild.style.setProperty('stroke-opacity', 1, 'important');
                      //  points[d.lineNum-1].firstChild.style.setProperty('fill-opbacity', 1, 'important');
                    //}

                //}
                //else{
                    //var outer = d.line2.parent.baseaxes[0][0].children[1];
                   // var points = outer.getElementsByTagName("g");

                    //if (typeof InstallTrigger !== 'undefined'){
                        //Firefox
                     //   points[d.lineNum-1].firstChild.style.setProperty('stroke-opacity', 0, 'important');
                     //   points[d.lineNum-1].firstChild.style.setProperty('fill-opacity', 0, 'important');
                    //}
                    //else if (!!window.chrome && !!window.chrome.webstore){
                        //Chrome
                       // points[(lineCount)-d.lineNum].firstChild.style.setProperty('stroke-opacity', 0, 'important');
                       // points[(lineCount)-d.lineNum].firstChild.style.setProperty('fill-opacity', 0, 'important');
                    //}
                    //else{
                        //implement more if needed
                       // points[d.lineNum-1].firstChild.style.setProperty('stroke-opacity', 0, 'important');
                      //  points[d.lineNum-1].firstChild.style.setProperty('fill-opacity', 0, 'important');
                   // }
                //}
            }
        };
    """

    def __init__(self, lines, labels, sized, nameID, css):
        self.css_ = css or ""

        self.lines = lines

        self.dict_ = {"type": "interactive_legend",
                      "line_ids": [mpld3.utils.get_id(line) for line in lines],
                      "labels": labels,
                      "nameID": nameID,
                      "sized": sized}
