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


class HideLegend(mpld3.plugins.PluginBase):
	"""mpld3 plugin to hide legend on plot"""

	JAVASCRIPT = """
    var my_icon = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAABVklEQVR42pXTO0sDQRSG4dmsyXptQ8BKCwsbq4CCiPgDrOwkIsTSf2Ul2KidhaAWYiFBFC1UWKN4VzTeQ0DfDd8u47gpLB4yc3Zy9szMWWOM8ZARz/ltFRvGlmJJ8D928axxy0UDKGMdo8gqfo66te7Xn9owhX3c4AWXGl/hBA1ne8kkh2+8KtEsPpXkHmP4wiN60iq4xYTGG1i1ys6jigX040kvaSbI6y1lBbpQsRIHOMAi9hQbwUec4B13mvgoIbTmb6rGtxJH4zPMG2UqKBg9nMGpxnVtx76+uPROVW6KOES3kkzjAkuqzLcSVKwDj148GB9iUYtzmofOQWV0eNtKeI1l9xYmdeeB9ldDu571qfM6dM1zSvSnlaP7fcAKhtRAUWWbGNezNWdbycBXt4Uq8Rg7cqTu7E1p+WRQ06nH2bPaTmA1lKu5BU+ZG1pof762tJj3A656Tx0L91EcAAAAAElFTkSuQmCC";
    mpld3.register_plugin("hidelegend", HideLegend);
    HideLegend.prototype = Object.create(mpld3.Plugin.prototype);
    HideLegend.prototype.constructor = HideLegend;
    HideLegend.prototype.requiredProps = ["nameID"];
    HideLegend.prototype.defaultProps = {};
    function HideLegend(fig, props){
        var tempName = props.nameID
        mpld3.Plugin.call(this, fig, props);
        var HideLegendButton = mpld3.ButtonFactory({
            buttonID: "hideLegend",
            sticky: false,
            onActivate: function(){
                var legend = $('[name=' + tempName + ']');
                var holder = $('[name=legendHolder]');
                var pltStat = localStorage.getItem('pltStat');
                if (pltStat == 0){
                    legend[0].style.visibility = "visible";
                    holder[0].style.visibility = "visible";
                    localStorage.setItem('pltStat', 1);
                }
                else{
                    legend[0].style.visibility = "hidden";
                    holder[0].style.visibility = "hidden";
                    localStorage.setItem('pltStat', 0);
                }
            },
            icon: function(){
                return my_icon;
            }
        });
        this.fig.buttons.push(HideLegendButton);
    }
    """

	def __init__(self, nameID):
		self.dict_ = {'type': 'hidelegend',
		              'nameID': nameID}