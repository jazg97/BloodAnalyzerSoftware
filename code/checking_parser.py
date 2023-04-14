import sys
from utils import *

print(type(sys.argv))

print('Command line input:', sys.argv[-1])

print(os.path.join(root_dir, sys.argv[-1]))
