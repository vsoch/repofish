
from exceptions import KeyError
from repofish.wikipedia import get_page
from repofish.utils import save_json, save_txt
import pandas
import time

## STEP 1: PARSE METHOD TEXT #######################################################################

methods_url = "https://en.wikipedia.org/wiki/List_of_statistics_articles"
topic = "List_of_statistics_articles"
result = get_page(topic)

# Save list of methods in case it changes
methods = pandas.DataFrame()
methods["methods"] = result.links

# This is manual parsing to resolve disambiguation errors - we will have redundancy here, 
# but not an issue as results object is a dictionary
methods[methods.methods=="A posteriori probability (disambiguation)"] = "posterior probability"
methods[methods.methods=="ANCOVA"] = "Analysis of covariance" # ANCOVA would return "Angola"
methods[methods.methods=="Data generating process"] = "data collection"
methods[methods.methods=="Data generating process (disambiguation)"] = "data collection"
methods[methods.methods=="Deviation analysis"] = "absolute difference"
methods[methods.methods=="Deviation analysis (disambiguation)"] = "absolute difference"
methods[methods.methods=="Double exponential distribution"] = "Laplace distribution"
methods[methods.methods=="Double exponential distribution (disambiguation)"] = "Laplace distribution"
methods[methods.methods=="Lambda distribution (disambiguation)"] = "Tukey's lambda distribution"
methods[methods.methods=="Lambda distribution"] = "Tukey's lambda distribution"
methods[methods.methods=="Linear least squares"] = "Linear least squares (mathematics)"
methods[methods.methods=="Linear least squares (disambiguation)"] = "Linear least squares (mathematics)"
methods[methods.methods=="MANCOVA"] = "Multivariate analysis of covariance"
methods[methods.methods=="MANCOVA (disambiguation)"] = "Multivariate analysis of covariance"
methods[methods.methods=="Mean deviation"] = "Mean signed deviation"
methods[methods.methods=="Mean deviation (disambiguation)"] = "Mean signed deviation"
methods[methods.methods=="Safety in numbers (disambiguation)"] = "Safety in numbers"
methods[methods.methods=="Safety in numbers"] = "Safety in numbers"
methods[methods.methods=="T distribution"] = "Student's t-distribution"
methods[methods.methods=="T distribution (disambiguation)"] = "Student's t-distribution"

methods.to_csv("wikipedia_methods.tsv",sep="\t",encoding="utf-8")

# Now let's generate a data structure with all content, links, etc.
results = dict()

for method in methods["methods"]:
    if method not in results:
        entry = {}
        result = get_page(method)
        print "Matching %s to %s" %(method,result.title) # Manual checking
        entry["categories"] = result.categories
        entry["title"] = result.title
        entry["method"] = method
        # url can let us parse for equation content
        entry["url"] = result.url

        # We can use links to calculate relatedness
        try:
            entry["links"] = result.links
        except KeyError:
            entry["links"] = []

        try:
            entry["references"] = result.references
        except KeyError:
            entry["references"] = []

        # save just summary for now.
        entry["summary"] = result.summary
        entry["images"] = result.images
        results[method] = entry

del results["Safety in numbers"]
save_json(results,"wikipedia_methods.json")

## STEP 2: BUILD MODELS ############################################################################

# build a word embedding model based on ALL of the text, let's try LDA and word2vec. We will then be able to generate
# a feature vector for a single text entry.

from wordfish.analysis import build_models, save_models, export_models_tsv, \
  DeepTextAnalyzer, export_vectors #pip install wordfish

# First save sentences to one massive file
filey = open("method_sentences.txt","w")
for method,result in results.iteritems():
    filey.writelines(result["summary"])
filey.close()

base_dir = "/home/vanessa/Documents/Dropbox/Code/Python/repofish"
method_names = ["lda","word2vec"]
models = dict()

for method_name in method_names:
    corpus = {"methods_%s" %model_name:["method_sentences.txt"]}
    model = build_models(corpus,model_type=method_name)
    models.update(model)

# Save models and vectors
export_models_tsv(models,base_dir)
model_dir = "%s/analysis/models" %base_dir
export_vectors(models,output_dir=model_dir)


## Now for each method, save a vector representation
vectors = pandas.DataFrame()
model = models["methods_word2vec"]
tempfile = "/tmp/repofish.txt"

for method,result in results.iteritems():
    print "Generating model for method %s" %(method)
    analyzer = DeepTextAnalyzer(model)
    save_txt(tempfile,result["summary"])
    vectors.loc[method] = analyzer.text2mean_vector(tempfile)

# Need to fillna?
vectors.to_tsv("%s/method_vectors.tsv" %model_dir,sep="\t")

# Compare similarity, for kicks and giggles
