from repofish.database import get_functions
from repofish.utils import save_json
import sklearn
import nilearn
import theano
import gensim
import os

# Sklearn
module_folder = os.path.dirname(sklearn.__file__)
functions = get_functions(module_folder)
save_json(functions,"lib/sklearn.json")

# Nilearn
module_folder = os.path.dirname(nilearn.__file__)
functions = get_functions(module_folder)
save_json(functions,"lib/nilearn.json")

# Theano
module_folder = os.path.dirname(theano.__file__)
functions = get_functions(module_folder)
save_json(functions,"lib/theano.json")

# Tensorflow
module_folder = os.path.dirname(tensorflow.__file__)
functions = get_functions(module_folder)
save_json(functions,"lib/tensorflow.json")

# Gensim
module_folder = os.path.dirname(gensim.__file__)
functions = get_functions(module_folder)
save_json(functions,"lib/gensim.json")

