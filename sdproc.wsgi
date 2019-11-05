import sys
import os

sys.path.insert(0, '/Public/SDproc/sdprocApp')

virtual_env = 'myenv'

py_version = '%d.%d' % (sys.version_info.major, sys.version_info.minor)

base_path = os.path.dirname( os.path.abspath(__file__) )

sys.path.insert( 0, base_path )
sys.path.insert( 0, base_path + '/' + virtual_env + '/lib/python' + py_version + '/site-packages' )

activate_this = base_path + '/' + virtual_env + '/bin/activate_this.py'
execfile(activate_this,dict(__file__=activate_this))

from test import app as application
