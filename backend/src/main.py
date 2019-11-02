from server.instance import server
import sys, os

# Need to import all resources
# so that they register with the server

#from resources.routes import *
from resources.update import *
from resources.delete import *
from resources.create import *
from resources.status import *
from resources.health import *
from resources.configof import *
from resources.list import *

if __name__ == '__main__':
    server.run()