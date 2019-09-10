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

import os
import secrets
from datetime import datetime

from flask_login import current_user
from flask import current_app

from db.db_model import db, DataFile
from flask_app import app
from utilities import mda, mdaAscii

ALLOWED_EXTENSIONS = {'txt', 'mda', 'dat'}


class FileUtility:

    def __init__(self):
        pass

    @staticmethod
    def modified(path):
        """Returns modified time of this."""
        return datetime.now().strftime("%d/%m/%Y")

    # return datetime.fromtimestamp(os.path.getmtime(path))

    @staticmethod
    def getTime():
        return datetime.now()

    @staticmethod
    def size(path):
        """A size of this file."""
        return os.path.getsize(path)

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    @staticmethod
    def readAscii(path, comChar):
        count = 0
        name = path.split("/")
        name = name[-1]
        with open(path) as f:
            for line in f:
                line = line.rstrip()
                if line.startswith(comChar):
                    continue
                if len(line) == 0:
                    continue
                line = line[1:]
                line = line.split()
                if count == 0:
                    data = [[] for x in xrange(len(line))]
                count += 1
                for i in range(len(line)):
                    data[i].append(line[i])
        return data, name, path

    @staticmethod
    def readMdaAscii(path):
        count = 0
        name = path.split("/")
        name = name[-1]
        with open(path) as f:
            for line in f:
                line = line.rstrip()
                if line.startswith("#"):
                    continue
                if len(line) == 0:
                    continue
                line = line.split(" ")
                if count == 0:
                    data = [[] for x in xrange(len(line))]
                count += 1
                for i in range(len(line)):
                    data[i].append(line[i])
        return data, name, path

    @staticmethod
    def readMda(path):
        name = path.split("/")
        name = name[-1]
        endData = []
        mdaData = mda.readMDA(path, 1, 0, 0)
        for column in mdaData[1].p:
            endData.append(column.data)
        for column in mdaData[1].d:
            endData.append(column.data)
        return endData, name, path

    @staticmethod
    def getHeader(fileName, filePath):
        d = mda.readMDA(filePath, 4, 0, 0)
        if not d:
            return 0

        rank = d[0]['rank']
        (phead_fmt, dhead_fmt, pdata_fmt, ddata_fmt, columns) = mdaAscii.getFormat(d, 1)
        output = "### " + fileName + " is a " + str(d[0]['rank']) + "dimensional file.\n"
        if (rank > len(d) - 1):
            output += "file doesn't contain the data that it claims to contain\n"
            output += "rank=%d, dimensions found=%d" % (rank, len(d) - 1)
            return output
        output += "### Number of data points = ["
        for i in range(d[0]['rank'], 1, -1):
            output += "%-d," % str(d[i].curr_pt)
        output += str(d[1].curr_pt) + "]\n"

        output += "### Number of detector signals = ["
        for i in range(d[0]['rank'], 1, -1): output += "%-d," % d[i].nd
        output += str(d[1].nd) + "]\n"
        output += "#\n# Scan-environment PV values:\n"
        ourKeys = d[0]['ourKeys']
        maxKeyLen = 0
        for i in d[0].keys():
            if (i not in ourKeys):
                if len(i) > maxKeyLen: maxKeyLen = len(i)
        for i in d[0].keys():
            if (i not in ourKeys):
                output += "#" + str(i) + str((maxKeyLen - len(i)) * ' ') + str(d[0][i]) + "\n"
        output += "#\n# " + str(d[1]) + "\n"
        output += "#  scan date, time: " + str(d[1].time) + "\n"
        output += "#\n"
        for j in range(d[1].np):
            output += phead_fmt[j] % (d[1].p[j].fieldName) + "\n"
        for j in range(d[1].nd):
            output += dhead_fmt[j] % (d[1].d[j].fieldName) + "\n"

        output += "#\n"
        for j in range(d[1].np):
            output += phead_fmt[j] % (d[1].p[j].name) + "\n"
        for j in range(d[1].nd):
            output += dhead_fmt[j] % (d[1].d[j].name) + "\n"

        output += "#\n"
        for j in range(d[1].np):
            output += phead_fmt[j] % (d[1].p[j].desc) + "\n"
        for j in range(d[1].nd):
            output += dhead_fmt[j] % (d[1].d[j].desc) + "\n"
        return output

    @staticmethod
    def writeOutput(output, colNames, name, lname):
        """
        Writes a .txt output file based on the location that the user is requesting the output from.
        Leave the name of the file(s) as a comment on the top of the file using the user's comment character as saved on their profile
        If the user does not have a comment character saved on their profile it defaults to #
        """
        comChar = current_user.commentChar
        if comChar is None:
            comChar = '#'

        if isinstance(name, list):
            random_hex = secrets.token_hex(4)
            x = str(datetime.now().strftime("%d-%m-%Y"))
            filename = x + '_' + random_hex + ".dat"
            path = os.path.join(current_app.root_path, 'static/saved_files', "dat", filename)
        else:
            random_hex = secrets.token_hex(4)
            filename = name[:-4] + "_" + random_hex + ".dat"
            path = os.path.join(current_app.root_path, 'static/saved_files', "dat", filename)

        f = open(path, 'w')

        if isinstance(name, list):
            f.write('#Files Included:')
            f.write('\n')
            for id in name:
                file = db.session.query(DataFile).filter_by(id=id).first()
                f.write('#' + file.name)
                f.write('\n')
        else:
            f.write('#' + name)
            f.write('\n')

        for i in range(len(output)):
            if isinstance(colNames[i], str):
                f.write(comChar + str(colNames[i]) + '= Column: ' + str(i + 1))
            else:
                f.write(comChar + str(colNames[i].text) + '= Column: ' + str(i + 1))
            f.write('\n')

        for i in range(len(output[0])):
            for j in range(len(output)):
                f.write(str(output[j][i]) + (' ' * 10))
            f.write('\n')

        f.close()

        return filename
