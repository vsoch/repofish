from repofish.utils import save_json, save_txt, convert_unicode
from repofish.wikipedia import get_page
from exceptions import KeyError
import matplotlib.pyplot as plt
import pandas
import numpy
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
len(results)
#2786


## STEP 2: BUILD MODELS ############################################################################

# build a word embedding model based on ALL of the text, let's try LDA and word2vec. We will then be able to generate
# a feature vector for a single text entry.

from wordfish.analysis import build_models, save_models, export_models_tsv, \
  DeepTextAnalyzer, export_vectors #pip install wordfish

# First save sentences to one massive file
filey = open("method_sentences.txt","w")
for method,result in results.iteritems():
    summary = convert_unicode(result["summary"]).replace("\n"," ")
    filey.write("%s\n" %summary)
filey.close()

base_dir = "/home/vanessa/Documents/Dropbox/Code/Python/repofish"
method_names = ["lda","word2vec"]
models = dict()

for method_name in method_names:
    corpus = {"methods_%s" %method_name:["method_sentences.txt"]}
    model = build_models(corpus,model_type=method_name)
    models.update(model)

# Save models and vectors
export_models_tsv(models,base_dir)
save_models(models,base_dir)
vectors_dir = "%s/analysis/models/vectors" %base_dir
os.mkdir(vectors_dir)
export_vectors(models,output_dir=vectors_dir)

## Now for each method, save a vector representation
vectors = pandas.DataFrame(columns=range(300))
model = models["methods_word2vec"]
tempfile = "/tmp/repofish.txt"
analyzer = DeepTextAnalyzer(model)

for method,result in results.iteritems():
    print "Generating model for method %s" %(method)
    summary = convert_unicode(result["summary"]).replace("\n"," ")
    save_txt(summary,tempfile)
    vectors.loc[method] = analyzer.text2mean_vector(tempfile)


vectors.to_csv("%s/method_vectors.tsv" %model_dir,sep="\t",encoding="utf-8")

# Compare similarity, for kicks and giggles
sim = vectors.T.corr()
sim.to_csv("%s/method_vectors_similarity.tsv" %model_dir,sep="\t",encoding="utf-8")

# GRAPHISTRY VISUALIZATION ###############################################
df = pandas.DataFrame(columns=["source","target","value"])

count=1
thresh=0.9
seen = []
for row in sim.iterrows():
    method1_name = row[0]
    similar_methods = row[1][row[1].abs() >= thresh]
    for method2_name,v in similar_methods.iteritems():
        pair_id = "_".join(numpy.sort([method1_name,method2_name]))
        if method2_name != method1_name and pair_id not in seen:
            seen.append(pair_id)
            df.loc[count] = [method1_name,method2_name,v] 
            count+=1

# Make a lookup
lookup = dict()
unique_methods = numpy.unique(df["source"].tolist() + df["target"].tolist()).tolist()
for u in range(len(unique_methods)):
    lookup[unique_methods[u]] = unique_methods[u].decode('utf-8').encode('ascii',errors='replace').replace('?',' ')
    

# Replace sources and targets with lookups
sources = [lookup[x] for x in df["source"]]
targets = [lookup[x] for x in df["target"]]
df2=pandas.DataFrame()

df2["source"] = sources
df2["target"] = targets
df2["value"] = df["value"]
df2.to_csv("method_sims_graphistry_pt9.csv",index=False,encoding='utf-8')
