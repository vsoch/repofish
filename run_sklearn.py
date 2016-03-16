import sklearn
from repofish import get_functions

# Get functions data structure for sklearn
module_folder = os.path.dirname(sklearn.__file__)
functions = get_functions(module_folder)

#TODO: retrieve Github repos from database / pubmed

#TODO: search for words in repos in database

#module_folder = ''
# Figure out CURL call from within Python

#curl -H 'Accept: application/vnd.github.v3.text-match+json' \
#  'https://api.github.com/search/repositories?q=tetris+language:assembly&sort=stars&order=desc'

# First find repos
#https://api.github.com/search/repositories?q=scikit-learn+language:python&sort=stars&order=desc

# Then search code
