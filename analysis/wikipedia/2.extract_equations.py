# Here we want to extract equations from wikipedia article pages

from repofish.wikipedia import get_page
from repofish.utils import save_json, save_txt
from BeautifulSoup import BeautifulSoup
import pandas
import json
import time
import re

### EQUATION EXTRACTION ###############################################################

methods = pandas.read_csv("wikipedia_methods.tsv",sep="\t",index_col=0)
skip = ['1.96','PARAFAC','Safety in numbers','T distribution (disambiguation)']

results = dict()

for method in methods["methods"]:
    if method not in results and method not in skip:
        print "Extracting equations from %s" %(method)
        result = get_page(method)
        html = result.html()
        soup = BeautifulSoup(html)

        equations = []

        # Equations are represented as images
        images = soup.findAll('img')
        for image in images:
            image_class = image.get("class")
            if image_class != None:
                if re.search("tex|math",image_class):
                    png = image.get("src")
                    tex = image.get("alt")
                    entry = {"png":png,
                             "tex":tex}
                    equations.append(entry)

        if len(equations) > 0:
            results[method] = equations
        else:
            skip.append(method)

save_json(results,"wikipedia_equations.json")


### MODEL BUILDING ####################################################################

# Here we want to parse the equations to build a word2vec model based on equation symbols

from wordfish.analysis import build_models, save_models, export_models_tsv, \
  DeepTextAnalyzer, export_vectors #pip install wordfish

# First save sentences to one massive file
filey = open("equation_sentences.txt","w")
for method,equations in results.iteritems():
    for equation in equations:
        # if this fails, there is text in the field and not latex, just skip
        try:
            tex = equation["tex"].decode('utf-8').encode('ascii',errors='replace').replace('\n',' ')
            tex = tex.replace(" ","").replace(",","")
            characters = " ".join([t for t in tex])
            filey.write("%s\n" %characters)
        except:
            print "skipping %s" %(equation["tex"])

# skipping MS estimator of a is the minimal x minus the sample range divided by n−1; MS estimator of b is the maximal x plus the sample range divided by n−1
# skipping ML estimate of a is the smallest of x’s
# skipping ML estimate of b is the largest of x’s
# skipping χ²
# skipping χ²
# skipping χ²
# skipping ±1.58*IQR/sqrt(n)

filey.close()

base_dir = "/home/vanessa/Documents/Dropbox/Code/Python/repofish"
method_names = ["lda","word2vec"]
models = dict()

for method_name in method_names:
    corpus = {"equations_%s" %method_name:["equation_sentences.txt"]}
    model = build_models(corpus,method_name,False,False) # Don't remove stop words or non english chars
    models.update(model)

# Save models and vectors
export_models_tsv(models,base_dir)
save_models(models,base_dir)
model_dir = "%s/analysis/models" %base_dir
vectors_dir = "%s/vectors" %model_dir
if not os.path.exists(vectors_dir):
    os.mkdir(vectors_dir)
export_vectors(models,output_dir=vectors_dir)

## Now for each method, save a vector representation based on the equations
vectors = pandas.DataFrame(columns=range(300))
model = models["equations_word2vec"]

embeddings = pandas.read_csv("%s/equations_word2vec.tsv" %vectors_dir,sep="\t",index_col=0)

def text2mean_vector(characters,embeddings):
    '''text2mean_vector_weighted maps a new text (characters) onto vectors (a word2vec word embeddings model) by taking a mean of the vectors that are words in the text
    :param characters: a list of characters or words (from equations)
    :param embeddings: a pandas data frame of vectors, index should be words/characters in model
    '''
    characters = [c for c in characters if c in embeddings.index.tolist()]
    if len(characters) != 0:
        return embeddings.loc[characters].mean().tolist()
    return None

for method,equations in results.iteritems():
    print "Generating equations models for method %s" %(method)
    count = 0
    for equation in equations:
        try:
            tex = equation["tex"].decode('utf-8').encode('ascii',errors='replace').replace('\n',' ')
            tex = tex.replace(" ","").replace(",","")
            characters = [t for t in tex]
            # We take a mean vector from the word embeddings, weighted by character counts
            vector = text2mean_vector(characters,embeddings)
            if vector != None:
                method_id = "%s_%s" %(method,count)
                vectors.loc[method_id] = vector    
                count+=1
        except:
            print "skipping %s" %(equation["tex"])


vectors.to_csv("%s/equations_vectors.tsv" %model_dir,sep="\t",encoding="utf-8")

# Compare similarity, for kicks and giggles
sim = vectors.T.corr()
sim.to_csv("%s/equations_vectors_similarity.tsv" %model_dir,sep="\t",encoding="utf-8")

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
