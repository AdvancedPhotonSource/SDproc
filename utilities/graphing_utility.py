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

from operator import and_

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mpld3
from sdproc.forms.input_form import InputForm
from utilities.file_utility import FileUtility
from flask_login import current_user
from db.db_model import db, CurrentDAT, DataFile, CurrentMeta
import json
import math
import numpy
import uuid
import copy
from scipy import stats
from utilities.sdproc_mpld3.hide_legend import HideLegend
from utilities.sdproc_mpld3.interactive_legend import InteractiveLegend


class GraphingUtility():

    @staticmethod
    def simple_plot(data, xmax, filename, linenames, legend, sized):
        plt.close('all')
        fig = plt.figure(figsize=(10, 7))
        css = """
        .legend-box{
            cursor: pointer;
        }
        """
        labels = []
        lines = []
        name_id = str(uuid.uuid4())
        if legend == 0:
            fig, ax = plt.subplots()
            xs = data[0]
            ys = data[1]
            plt.plot(xs, ys)
        else:
            fig, ax = plt.subplots()
            xs = data[0]
            ys = data[1]
            line = ax.plot(xs, ys, alpha=0, label=filename)
            lines.append(line[0])
            labels.append(filename)

            mpld3.plugins.connect(fig, InteractiveLegend(lines, labels, sized, name_id, css))
            mpld3.plugins.connect(fig, HideLegend(name_id))
        plt.xlabel('meV')
        code = mpld3.fig_to_html(fig)
        plt.close('all')
        return code

    @staticmethod
    def mergePlots(allycords, allxmax, allagainstE, alldata, allLegendNames, allFileNames, pltLeg):
        '''Merges a list of plots using linear interpolation then plots the result'''
        plt.close('all')
        fig = plt.figure(figsize=(10, 7))
        css = """
	    .legend-box{
	        cursor: pointer;
	    }
	    """
        count1 = 0
        count2 = 0
        labels = []
        lines = []
        nameID = str(uuid.uuid4())
        if pltLeg == 0:
            for plot in alldata:
                xs = range(1, len(plot) + 1)
                ys = plot
                if allagainstE[count1] == 'Energy' or allagainstE[count1] == 'Energy xtal' or allagainstE[
                    count1] == 'Energy xtal w/T':
                    xs = alldata[count1][1]
                    xs = numpy.multiply(xs, 1000000)
                plt.plot(xs, ys)
                # plt.plot(xs[allxmax[count1][count2]], ys[allxmax[count2]], '-bD')
                count2 += 1
        else:
            fig, ax = plt.subplots()
            for oneDat in allycords:
                xs = oneDat[0]
                ys = oneDat[1]
                line = ax.plot(xs, ys, alpha=0, label=allFileNames[count1])
                lines.append(line[0])
                # point = ax.plot(xs[allxmax[count1][1]], ys[allxmax[count1][1]], '-bD')
                labels.append(allFileNames[count1])
                # lines.append(point[0])
                count1 += 1
            sumNumpy = []
            YVals = []
            for i in allycords:
                sumNumpy.append(i[0])
                YVals.append(i[1])
                if len(sumNumpy) == 2:
                    numCat = numpy.array(sumNumpy)
                    numCat[0] = numpy.array(numCat[0])
                    numCat[1] = numpy.array(numCat[1])
                    YVals[0] = numpy.array(YVals[0])
                    YVals[1] = numpy.array(YVals[1])
                    if numCat[0].size > numCat[1].size:
                        smallerx = numCat[1]
                        smallery = YVals[1]
                        largerx = numCat[0]
                        largery = YVals[0]
                    else:
                        smallerx = numCat[0]
                        smallery = YVals[0]
                        largerx = numCat[1]
                        largery = YVals[1]
                    smallLeft = (GraphingUtility.find_nearest(largerx, smallerx[0]))
                    smallRight = (GraphingUtility.find_nearest(largerx, smallerx[-1]))
                    largeLeft = (GraphingUtility.find_nearest(smallerx, largerx[0]))
                    largeRight = (GraphingUtility.find_nearest(smallerx, largerx[-1]))
                    smallleftPad = 0
                    smallrightPad = 0
                    largeleftPad = 0
                    largerightPad = 0
                    largeInnerX = []
                    largeInnerY = []
                    smallInnerX = []
                    smallInnerY = []
                    first = 0
                    smallRightPadIndex = 'None'
                    largeRightPadIndex = 'None'
                    for element in largerx:
                        if element < smallLeft:
                            smallleftPad += 1
                        elif element > smallRight:
                            if first == 0:
                                smallRightPadIndex = numpy.where(largerx == element)[0][0]
                                first = 1
                            smallrightPad += 1
                        else:
                            largeInnerX.append(element)
                            atIndex = numpy.where(largerx == element)[0][0]
                            largeInnerY.append(largery[atIndex])
                    first = 0
                    for element in smallerx:
                        if element < largeLeft:
                            largeleftPad += 1
                        elif element > largeRight:
                            if first == 0:
                                largeRightPadIndex = numpy.where(smallerx == element)[0][0]
                                first = 1
                            largerightPad += 1
                        else:
                            smallInnerX.append(element)
                            atIndex = numpy.where(smallerx == element)[0][0]
                            smallInnerY.append(smallery[atIndex])

                    smallInnerX = numpy.array(smallInnerX)
                    smallInnerY = numpy.array(smallInnerY)
                    largeInnerX = numpy.array(largeInnerX)
                    largeInnerY = numpy.array(largeInnerY)

                    if largeInnerX.size > smallInnerX.size:
                        smallInnerY = numpy.interp(largeInnerX, smallInnerX, smallInnerY)
                        adjLargex = largerx
                        if largeRightPadIndex != 'None':
                            adjSmallx = numpy.concatenate(
                                (smallerx[:largeleftPad], largeInnerX, smallerx[largeRightPadIndex:]))
                            smallery = numpy.concatenate(
                                (smallery[:largeleftPad], smallInnerY, smallery[largeRightPadIndex:]))
                        else:
                            adjSmallx = numpy.concatenate((smallerx[:largeleftPad], largeInnerX))
                            smallery = numpy.concatenate((smallery[:largeleftPad], smallInnerY))
                    elif largeInnerX.size < smallInnerX.size:
                        adjSmallx = smallerx
                        largeInnerY = numpy.interp(smallInnerX, largeInnerX, largeInnerY)
                        if smallRightPadIndex != 'None':
                            adjLargex = numpy.concatenate(
                                (largerx[:smallleftPad], smallInnerX, largerx[smallRightPadIndex:]))
                            largery = numpy.concatenate(
                                (largery[:smallleftPad], largeInnerY, largery[smallRightPadIndex:]))
                        else:
                            adjLargex = numpy.concatenate((largerx[:smallleftPad], smallInnerX))
                            largery = numpy.concatenate((largery[:smallleftPad], largeInnerY))
                    else:
                        if smallRightPadIndex != 'None':
                            adjLargex = numpy.concatenate(
                                (largerx[:smallleftPad], largeInnerX, largerx[smallRightPadIndex:]))
                        else:
                            adjLargex = numpy.concatenate((largerx[:smallleftPad], largeInnerX))
                        if largeRightPadIndex != 'None':
                            adjSmallx = numpy.concatenate(
                                (smallerx[:largeleftPad], largeInnerX, smallerx[largeRightPadIndex:]))
                        else:
                            adjSmallx = numpy.concatenate((smallerx[:largeleftPad], largeInnerX))

                    smallPady = numpy.pad(smallery, (smallleftPad, smallrightPad), 'constant', constant_values=(0, 0))
                    largePady = numpy.pad(largery, (largeleftPad, largerightPad), 'constant', constant_values=(0, 0))

                    if largeRightPadIndex != 'None':
                        largePadx = numpy.concatenate(
                            (smallerx[:largeleftPad], adjLargex, smallerx[largeRightPadIndex:]))
                    else:
                        largePadx = numpy.concatenate((smallerx[:largeleftPad], adjLargex))
                    if smallRightPadIndex != 'None':
                        smallPadx = numpy.concatenate((largerx[:smallleftPad], adjSmallx, largerx[smallRightPadIndex:]))
                    else:
                        smallPadx = numpy.concatenate((largerx[:smallleftPad], adjSmallx))

                    small = numpy.array((smallPadx, smallPady))
                    large = numpy.array((largePadx, largePady))
                    ySummed = numpy.add(small[1], large[1])
                    sum2D = numpy.array((largePadx, ySummed))
                    sumNumpyStep = largePadx.tolist()
                    YValsStep = ySummed.tolist()
                    sumNumpy = []
                    YVals = []
                    sumNumpy.append(sumNumpyStep)
                    YVals.append(YValsStep)

            sum2Dymax = numpy.amax(sum2D)
            sum2Dxmax = numpy.ndarray.argmax(sum2D)
            line = ax.plot(largePadx, ySummed, color='k', alpha=0, label='Sum of selected')
            lines.append(line[0])

            # point = ax.plot(sum2D[0][sum2Dxmax - largePadx.size], sum2Dymax, '-bD')
            labels.append('Sum of selected')
            # lines.append(point[0])
            mpld3.plugins.connect(fig, InteractiveLegend(lines, labels, 1, nameID, css))
        mpld3.plugins.connect(fig, HideLegend(nameID))
        code = mpld3.fig_to_html(fig)
        plt.close('all')
        return code, sum2D[0][sum2Dxmax - largePadx.size], sum2Dymax, largePadx, ySummed

    @staticmethod
    def find_nearest(array, value):
        idx = (numpy.abs(array - value)).argmin()
        return array[idx]

    @staticmethod
    def mergeBin(allycords, allxmax, allagainstE, alldata, allLegendNames, allFileNames, pltLeg, binWidth):
        '''Merges a list of plots with binning and plots the result'''
        plt.close('all')
        fig = plt.figure(figsize=(10, 7))
        css = """
	    .legend-box{
	        cursor: pointer;
	    }
	    """
        count1 = 0
        count2 = 0
        labels = []
        lines = []
        nameID = str(uuid.uuid4())
        if pltLeg == 0:
            for plot in alldata:
                xs = range(1, len(plot) + 1)
                ys = plot
                if allagainstE[count1] == 'Energy' or allagainstE[count1] == 'Energy xtal' or allagainstE[
                    count1] == 'Energy xtal w/T':
                    xs = alldata[count1][1]
                plt.plot(xs, ys)
                # plt.plot(xs[allxmax[count1][count2]], ys[allxmax[count2]], '-bD')
                count2 += 1
        else:
            fig, ax = plt.subplots()
            for oneDat in allycords:
                xs = oneDat[0]
                ys = oneDat[1]
                line = ax.plot(xs, ys, alpha=0, label=allFileNames[count1])
                lines.append(line[0])
                # point = ax.plot(xs[allxmax[count1][1]], ys[allxmax[count1][1]], '-bD')
                labels.append(allFileNames[count1])
                # lines.append(point[0])
                count1 += 1
            minValue = 0
            maxValue = 0
            endX = []
            endY = []
            for i in allycords:
                if i[0][0] < minValue:
                    minValue = i[0][0]
                if i[0][-1] > maxValue:
                    maxValue = i[0][-1]
            bins = numpy.arange(minValue, maxValue, binWidth)
            for i in range(len(allycords)):
                sumNumpy = []
                YVals = []
                endX.append([])
                endY.append([])
                binnedIdx = numpy.digitize(allycords[i][0], bins)
                resultIdx = 0
                for j in range(len(binnedIdx)):
                    if j == 0:
                        YVals.append([allycords[i][1][j], binnedIdx[j], 1])
                        sumNumpy.append([allycords[i][0][j], binnedIdx[j], 1])
                        continue
                    if binnedIdx[j] == binnedIdx[j - 1]:
                        YVals[resultIdx][0] += allycords[i][1][j]
                        YVals[resultIdx][2] += 1
                        sumNumpy[resultIdx][0] += allycords[i][0][j]
                        sumNumpy[resultIdx][2] += 1
                    else:
                        resultIdx += 1
                        YVals.append([allycords[i][1][j], binnedIdx[j], 1])
                        sumNumpy.append([allycords[i][0][j], binnedIdx[j], 1])
                for k in range(len(sumNumpy)):
                    endX[i].append([sumNumpy[k][0] / sumNumpy[k][2], sumNumpy[k][1]])
                    endY[i].append([YVals[k][0] / YVals[k][2], YVals[k][1]])
            sumXvals = []
            sumYvals = []
            binIdx = 1
            for i in range(len(bins)):
                sumXvals.append(None)
                sumYvals.append(None)
                for j in range(len(endX)):
                    for k in range(len(endX[j])):
                        if endX[j][k][1] == binIdx:
                            if sumXvals[binIdx - 1] == None:
                                sumXvals[binIdx - 1] = endX[j][k][0]
                                sumYvals[binIdx - 1] = endY[j][k][0]
                            else:
                                sumXvals[binIdx - 1] = (sumXvals[binIdx - 1] + endX[j][k][0]) / 2
                                sumYvals[binIdx - 1] = sumYvals[binIdx - 1] + endY[j][k][0]
                binIdx += 1
            sumXvals = [value for value in sumXvals if value != None]
            sumYvals = [value for value in sumYvals if value != None]
            line = ax.plot(sumXvals, sumYvals, color='k', alpha=0, label='Sum of selected')
            lines.append(line[0])

            sum2D = numpy.array((sumXvals, sumYvals))
            sum2Dymax = numpy.amax(sum2D)
            sum2Dxmax = numpy.ndarray.argmax(sum2D)

            # point = ax.plot(sum2D[0][sum2Dxmax - len(sumXvals)], sum2Dymax, '-bD')
            labels.append('Sum of selected')
            # lines.append(point[0])
            mpld3.plugins.connect(fig, InteractiveLegend(lines, labels, 1, nameID, css))
        mpld3.plugins.connect(fig, HideLegend(nameID))
        code = mpld3.fig_to_html(fig)
        plt.close('all')
        return code, sum2D[0][sum2Dxmax - len(sumXvals)], sum2Dymax, sumXvals, sumYvals

    @staticmethod
    def plotData(data, used, againstE, additional, lineNames, eType, unit):
        plt.close('all')
        fig = plt.figure(figsize=(10, 7))
        css = """
	    .legend-box{
	        cursor: pointer;
	    }
	    """
        xs = []
        ys = []
        labels = []
        lines = []
        count = 0
        nameID = str(uuid.uuid4())
        fig, ax = plt.subplots()
        for i in used:
            xs = range(1, len(data[i]) + 1)
            ys = data[i]
            plt.xlabel('Point #')
            if againstE == 'Energy' or againstE == 'Energy xtal' or againstE == 'Energy xtal w/T':
                xs = [float(x) for x in eType]
                if unit == 'keV':
                    xs = numpy.subtract(xs, xs[0])
                    plt.xlabel('keV')
                else:
                    xs = numpy.multiply(xs, 1000000)
                    xs = numpy.subtract(xs, xs[0])
                    plt.xlabel('meV')
            elif againstE == 'Energy Fitted':
                xs = [float(x) for x in eType]
                plt.xlabel('meV')
            line = ax.plot(xs, ys, alpha=0, label=lineNames[0][count])
            lines.append(line[0])
            labels.append(lineNames[0][count])
            count += 1

        if additional:
            for i in range(len(additional)):
                xs = range(1, len(additional[i]) + 1)
                ys = additional[i]
                plt.xlabel('Point #')
                if againstE == 'Energy' or againstE == 'Energy xtal' or againstE == 'Energy xtal w/T':
                    xs = [float(x) for x in eType]
                    if unit == 'keV':
                        xs = numpy.subtract(xs, xs[0])
                        plt.xlabel('keV')
                    else:
                        xs = numpy.multiply(xs, 1000000)
                        xs = numpy.subtract(xs, xs[0])
                        plt.xlabel('meV')
                elif againstE == 'Energy Fitted':
                    xs = [float(x) for x in eType]
                    plt.xlabel('meV')
                line = ax.plot(xs, ys, alpha=0, label=lineNames[1][i])
                lines.append(line[0])
                labels.append(lineNames[1][i])

        if not used and not additional:
            ax = plt.plot(ys, ys)
        else:
            mpld3.plugins.connect(fig, InteractiveLegend(lines, labels, 0, nameID, css))
            mpld3.plugins.connect(fig, HideLegend(nameID))
        code = mpld3.fig_to_html(fig)
        plt.close('all')
        return code

    @staticmethod
    def convert_Numpy(used, data, additional):
        toNumpy = []

        if additional:
            for i in range(len(additional)):
                dat = additional[i]
                toNumpy.append(dat)

        for idx, column in enumerate(data):
            for i in used:
                if (idx) == i:
                    dat = [float(j) for j in data[i]]
                    toNumpy.append(dat)
        npData = numpy.array(toNumpy)
        max = []
        xcord = []
        for plot in npData:
            max.append(numpy.amax(plot))
            xcord.append(numpy.argmax(plot))
        return max, xcord, toNumpy

    @staticmethod
    def energy_xtal(data, a1, a2, hrm):
        hrm = json.loads(hrm)
        energy = []
        a1Dat = data[a1]
        a2Dat = data[a2]
        a1Dat = [hrm['hrm_theta1_sign'] * float(i) for i in a1Dat]
        a2Dat = [hrm['hrm_theta2_sign'] * float(i) for i in a2Dat]
        hrm_tan1 = math.tan(math.radians(hrm['hrm_bragg1']))
        hrm_tan2 = math.tan(math.radians(hrm['hrm_bragg2']))

        if hrm['hrm_geo'] == '++':
            a = 1.0e-6 * hrm['hrm_e0'] / (hrm_tan1 + hrm_tan2)
            b = a1Dat[0] - a2Dat[0]
            for i in range(len(a1Dat)):
                energy.append(a * (a1Dat[i] - a2Dat[i] - b))
        else:
            a = 1.0e-6 * hrm['hrm_e0'] / (hrm_tan1 - hrm_tan2)
            b = a1Dat[0] + a2Dat[0]
            for i in range(len(a1Dat)):
                energy.append(a * (a1Dat[i] + a2Dat[i] - b))
        return energy

    @staticmethod
    def energy_xtal_temp(data, a1, a2, t1, t2, hrm):
        energy = []
        xtal = GraphingUtility.energy_xtal(data, a1, a2, hrm)
        corr = GraphingUtility.temp_corr(data, t1, t2, hrm)
        for i in range(len(xtal)):
            energy.append(xtal[i] + corr[i])
        return energy

    @staticmethod
    def temp_corr(data, t1, t2, hrm):
        hrm = json.loads(hrm)
        corr = []
        t1Dat = data[t1]
        t2Dat = data[t2]
        t1Dat = [float(i) for i in t1Dat]
        t2Dat = [float(i) for i in t2Dat]
        hrm_tan1 = math.tan(math.radians(hrm['hrm_bragg1']))
        hrm_tan2 = math.tan(math.radians(hrm['hrm_bragg2']))
        at1 = hrm['hrm_alpha1'] * hrm_tan1
        at2 = hrm['hrm_alpha2'] * hrm_tan2

        if hrm == '++':
            a = - hrm['hrm_e0'] / (hrm_tan1 + hrm_tan2)
            b = at1 * t1Dat[0] + at2 * t2Dat[0]
            for i in range(len(t1Dat)):
                corr.append(a * (at1 * t1Dat[i] + at2 * t2Dat[i] - b))
        else:
            a = - hrm['hrm_e0'] / (hrm_tan1 - hrm_tan2)
            b = at1 * t1Dat[0] - at2 * t2Dat[0]
            for i in range(len(t1Dat)):
                corr.append(a * (at1 * t1Dat[i] - at2 * t2Dat[i] - b))
        return corr

    @staticmethod
    def signal_normalized(data, sCol, nCol):
        signal = []
        sDat = data[sCol]
        nDat = data[nCol]
        sDat = [float(i) for i in sDat]
        nDat = [float(i) for i in nDat]

        normFac = GraphingUtility.norm_factors(data, nCol)

        for i in range(len(sDat)):
            signal.append(sDat[i] * normFac[i])
        return signal

    @staticmethod
    def norm_factors(data, nCol):
        norm = []
        nDat = data[nCol]
        nDat = [float(i) for i in nDat]

        ave = numpy.mean(nDat)
        for i in range(len(nDat)):
            norm.append(ave / nDat[i])
        return norm

    @staticmethod
    def calcAverageBack(leftIn, rightIn):
        DAT = db.session.query(CurrentDAT).filter(CurrentDAT.user == current_user).first()
        leftCords = [[] for _ in xrange(2)]
        rightCords = [[] for _ in xrange(2)]
        data = json.loads(DAT.DAT)
        for i in range(len(data[0])):
            if data[0][i] <= leftIn:
                leftCords[0].append(data[0][i])
                leftCords[1].append(data[1][i])
            if data[0][i] >= rightIn:
                rightCords[0].append(data[0][i])
                rightCords[1].append(data[1][i])
        try:
            linRegLeft = stats.linregress(leftCords[0], leftCords[1])
            (slope, intercept, rvalue, pvalue, stderr) = linRegLeft
            Lx1 = data[0][1]
            Lx2 = leftIn
            Ly1 = data[1][1]
            try:
                Ly2 = linRegLeft.slope * (Lx2 - Lx1) + Ly1
            except AttributeError:
                Ly2 = slope * (Lx2 - Lx1) + Ly1
        except ValueError:
            print('No points less than left value')
            raise ValueError(
                'Average can not be found when there are no points smaller than the given left to average.')
        try:
            linRegRight = stats.linregress(rightCords[0], rightCords[1])
            (slope, intercept, rvalue, pvalue, stderr) = linRegRight
            Rx1 = rightIn
            Rx2 = data[0][-1]
            Ry2 = data[1][-1]
            try:
                Ry1 = linRegRight.slope * (Rx1 - Rx2) + Ry2
            except AttributeError:
                Ry1 = slope * (Rx1 - Rx2) + Ry2
        except ValueError:
            print('No points greater than right value')
            raise ValueError(
                'Average can not be found when there are no points greater than the given right to average.')

        fig = plt.figure(figsize=(10, 7))
        css = """
	        .legend-box{
	            cursor: pointer;
	        }
	        """
        labels = []
        lines = []
        nameID = str(uuid.uuid4())
        fig, ax = plt.subplots()
        xs = data[0]
        ys = data[1]
        line = ax.plot(xs, ys, alpha=0, label='Summed')
        lines.append(line[0])
        labels.append('Summed')

        line = ax.plot([Lx1, Lx2], [Ly1, Ly2], alpha=0, label='Left Lin Reg')
        lines.append(line[0])
        labels.append('Left Lin Reg')
        line = ax.plot([Rx1, Rx2], [Ry1, Ry2], alpha=0, label='Right Lin Reg')
        lines.append(line[0])
        labels.append('Right Lin Reg')
        mpld3.plugins.connect(fig, InteractiveLegend(lines, labels, 1, nameID, css))
        mpld3.plugins.connect(fig, HideLegend(nameID))
        code = mpld3.fig_to_html(fig)
        plt.close('all')
        averaged = [Lx1, Lx2, Rx1, Rx2, Ly1, Ly2, Ry1, Ry2]
        sending = averaged
        return sending

    @staticmethod
    def addLines(line1, line2):
        fig = plt.figure(figsize=(10, 7))
        css = """
	            .legend-box{
	                cursor: pointer;
	            }
	            """
        labels = []
        lines = []
        nameID = str(uuid.uuid4())
        fig, ax = plt.subplots()
        xs = line1[0]
        ys = line1[1]
        line = ax.plot(xs, ys, alpha=0, label='Summed')
        lines.append(line[0])
        labels.append('Summed')
        xs = []
        ys = []
        try:
            for i in range(len(line2)):
                if i < len(line2) / 2:
                    xs.append(line2[i])
                else:
                    ys.append(line2[i])
            line = ax.plot(xs, ys, alpha=0, label='Background')
        except TypeError:
            line = ax.plot(line1[0], [line2] * len(line1[0]), alpha=0, label='Background')

        lines.append(line[0])
        labels.append('Background')
        mpld3.plugins.connect(fig, InteractiveLegend(lines, labels, 1, nameID, css))
        mpld3.plugins.connect(fig, HideLegend(nameID))
        code = mpld3.fig_to_html(fig)
        plt.close('all')
        return code

    @staticmethod
    def peakFit(idthis, energyType, signalType, unit, fitType, fitRange, inputCord, localRange):
        if fitType == 'Unfit':
            fitType = 'AtMax'
        file_instance = db.session.query(DataFile).filter_by(id=idthis).first()
        format_instance = db.session.query(CurrentMeta).filter(and_(CurrentMeta.user_id == current_user.get_id(),
                                                                    CurrentMeta.file_id == file_instance.id,
                                                                    CurrentMeta.session == current_user.current_session)).first()
        if str(file_instance.type) == 'mda':
            data, name, unusedpath = FileUtility.readMda(file_instance.path)
        else:
            data, name, unusedpath = FileUtility.readAscii(file_instance.path, file_instance.comChar)
        form = GraphingUtility.populate_from_instance(format_instance)
        columns, bools = GraphingUtility.splitForm(form)
        basedColumns = GraphingUtility.zeroBaseColumns(columns)
        used = []
        additional = []
        legendNames = []
        if energyType == 'Energy xtal':
            energy = numpy.divide(
                GraphingUtility.energy_xtal(data, GraphingUtility.unicode_to_int(basedColumns[3].data),
                                            GraphingUtility.unicode_to_int(basedColumns[4].data), format_instance.hrm),
                1000000)
            additional.append(energy)
            legendNames.append(basedColumns[1].id)
        elif energyType == 'Energy xtal w/T':
            energy = numpy.divide(
                GraphingUtility.energy_xtal_temp(data, GraphingUtility.unicode_to_int(basedColumns[3].data),
                                                 GraphingUtility.unicode_to_int(basedColumns[4].data),
                                                 GraphingUtility.unicode_to_int(basedColumns[5].data),
                                                 GraphingUtility.unicode_to_int(basedColumns[6].data),
                                                 format_instance.hrm), 1000000)
            additional.append(energy)
            legendNames.append(basedColumns[2].id)
        else:
            used.append(GraphingUtility.unicode_to_int(basedColumns[0].data))
            legendNames.append(basedColumns[0].id)
        if signalType == 'Signal Normalized':
            signal = GraphingUtility.signal_normalized(data, GraphingUtility.unicode_to_int(basedColumns[8].data),
                                                       GraphingUtility.unicode_to_int(basedColumns[10].data))
            additional.append(signal)
            legendNames.append(basedColumns[9].id)
        else:
            used.append(GraphingUtility.unicode_to_int(basedColumns[8].data))
            legendNames.append(basedColumns[8].id)
        max, xmax, ycords = GraphingUtility.convert_Numpy(used, data, additional)
        npXcords = numpy.array(ycords[0])
        if unit == 'keV':
            npYcords = numpy.array(ycords[1])
        else:
            npXcords = numpy.multiply(npXcords, 1000000)
            npYcords = numpy.array(ycords[1])
        if fitType == 'AtMax':
            leftBound = (GraphingUtility.find_nearest(npXcords, npXcords[xmax[1]] - (fitRange / 2)))
            rightBound = (GraphingUtility.find_nearest(npXcords, npXcords[xmax[1]] + (fitRange / 2)))
            targetRange = [x for x in npXcords if x >= leftBound]
            targetRange = [x for x in targetRange if x <= rightBound]
            npData = []
            for xcord in targetRange:
                oneCord = numpy.where(npXcords == xcord)[0][0]
                npData.append(ycords[1][oneCord])
            targetX = numpy.array(targetRange)
            targetY = numpy.array(npData)
            center = GraphingUtility.centroid(targetX, targetY)
            ycords[0] = npXcords
            GraphingUtility.moveXcords(ycords, center)
            format_instance.fit_type = 'AtMax'
            format_instance.fit_pos = center
            format_instance.fit_range = fitRange
        elif fitType == 'AtPoint':
            leftBound = (GraphingUtility.find_nearest(npXcords, inputCord + npXcords[0] - (fitRange / 2)))
            rightBound = (GraphingUtility.find_nearest(npXcords, inputCord + npXcords[0] + (fitRange / 2)))
            targetRange = [x for x in npXcords if x >= leftBound]
            targetRange = [x for x in targetRange if x <= rightBound]
            npData = []
            for xcord in targetRange:
                oneCord = numpy.where(npXcords == xcord)[0][0]
                npData.append(ycords[1][oneCord])
            targetX = numpy.array(targetRange)
            targetY = numpy.array(npData)
            center = GraphingUtility.centroid(targetX, targetY)
            ycords[0] = npXcords
            GraphingUtility.moveXcords(ycords, center)
            format_instance.fit_type = 'AtPoint'
            format_instance.fit_pos = center
            format_instance.fit_range = fitRange
        else:
            leftBound = (GraphingUtility.find_nearest(npXcords, inputCord + npXcords[0] - (localRange / 2)))
            rightBound = (GraphingUtility.find_nearest(npXcords, inputCord + npXcords[0] + (localRange / 2)))
            targetRange = [x for x in npXcords if x >= leftBound]
            targetRange = [x for x in targetRange if x <= rightBound]
            npData = []
            for xcord in targetRange:
                oneCord = numpy.where(npXcords == xcord)[0][0]
                npData.append(ycords[1][oneCord])
            npData = numpy.array(npData)
            max = numpy.argmax(npData)
            maxIndex = oneCord - len(targetRange) + max + 1

            leftBound = (GraphingUtility.find_nearest(npXcords, npXcords[maxIndex] - (fitRange / 2)))
            rightBound = (GraphingUtility.find_nearest(npXcords, npXcords[maxIndex] + (fitRange / 2)))
            targetRange = [x for x in npXcords if x >= leftBound]
            targetRange = [x for x in targetRange if x <= rightBound]
            npData = []
            for xcord in targetRange:
                oneCord = numpy.where(npXcords == xcord)[0][0]
                npData.append(ycords[1][oneCord])
            targetX = numpy.array(targetRange)
            targetY = numpy.array(npData)
            center = GraphingUtility.centroid(targetX, targetY)
            ycords[0] = npXcords
            GraphingUtility.moveXcords(ycords, center)
            format_instance.fit_type = 'AtPoint'
            format_instance.fit_pos = center
            format_instance.fit_range = fitRange
        db.session.commit()
        code = GraphingUtility.simple_plot(ycords, xmax, file_instance.name, legendNames, 0, 0)
        return code, ycords, form

    @staticmethod
    def atMax(ycords, npXcords, xmax, fitRange):
        '''
	    Finds the center of the npXcords that fall within the fitRange

	    Calls centroid to get the actual center while this primarily does the bounding to collect the points to pass to centroid.
	    '''
        leftBound = (GraphingUtility.find_nearest(npXcords, xmax[1] - (fitRange / 2)))
        rightBound = (GraphingUtility.find_nearest(npXcords, xmax[1] + (fitRange / 2)))
        targetRange = [x for x in npXcords if x >= leftBound]
        targetRange = [x for x in targetRange if x <= rightBound]
        npData = []
        for xcord in targetRange:
            oneCord = numpy.where(npXcords == xcord)[0][0]
            npData.append(ycords[1][oneCord])
        targetX = numpy.array(targetRange)
        targetY = numpy.array(npData)
        center = GraphingUtility.centroid(targetX, targetY)
        return center

    @staticmethod
    def moveXcords(data, max):
        data[0] = numpy.subtract(data[0], max)
        return data

    @staticmethod
    def centroid(xVals, yVals):
        bot = numpy.sum(yVals)
        topArray = numpy.multiply(xVals, yVals)
        top = numpy.sum(topArray)
        shiftVal = top / bot
        return shiftVal

    @staticmethod
    def unicode_to_int(unicode):
        convertI = int(unicode)
        return convertI

    @staticmethod
    def splitForm(form):
        columns = []
        bools = []
        for field in form:
            if field.type == 'IntegerField':
                columns.append(field)
            else:
                bools.append(field)
        return columns, bools

    @staticmethod
    def zeroBaseColumns(columns):
        zColumns = copy.deepcopy(columns)
        for zColumn in zColumns:
            if zColumn.data is not None:
                zColumn.data -= 1
        return zColumns

    @staticmethod
    def populate_from_instance(instance):
        form = InputForm()
        for field in form:
            try:
                field.data = getattr(instance, field.name)
            except AttributeError:
                continue
        return form
