from repofish.database import get_functions
from repofish.utils import save_json
import sklearn
import nilearn
import nipype
import theano
import gensim
import skimage
import numpy
import os

# Sklearn
module_folder = os.path.dirname(sklearn.__file__)
functions = get_functions(module_folder)
save_json(functions,"../repofish/lib/sklearn.json")

# Nilearn
module_folder = os.path.dirname(nilearn.__file__)
functions = get_functions(module_folder)
save_json(functions,"../repofish/lib/nilearn.json")

# Theano
module_folder = os.path.dirname(theano.__file__)
functions = get_functions(module_folder)
save_json(functions,"../repofish/lib/theano.json")

# Tensorflow
module_folder = os.path.dirname(tensorflow.__file__)
functions = get_functions(module_folder)
save_json(functions,"../repofish/lib/tensorflow.json")

# Gensim
module_folder = os.path.dirname(gensim.__file__)
functions = get_functions(module_folder)
save_json(functions,"../repofish/lib/gensim.json")

# Skimage
module_folder = os.path.dirname(skimage.__file__)
functions = get_functions(module_folder)
save_json(functions,"../repofish/lib/skimage.json")

# Numpy
module_folder = os.path.dirname(numpy.__file__)
functions = get_functions(module_folder)
save_json(functions,"../repofish/lib/numpy.json")

# nipype
module_folder = os.path.dirname(nipype.__file__)
functions = get_functions(module_folder)
save_json(functions,"../repofish/lib/nipype.json")

