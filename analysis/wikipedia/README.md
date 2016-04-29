# Ideas

### Idea 1: Can we find similar repos/functions based on context from papers?

I would want a web interface where I can go, select some word or n-gram (likely a method, keyword, or domain, e.g., linear regression or sequence alignment) and immediately be shown Github repos that serve that purpose. If we can map out research software based on these groupings, we can then look at subsets and start to ask questions that quantify and compare reproducible practices, patterns in scripting, etc. The steps to complete this are as follows:

- First we need a list of methods that we want to understand. We can use wikipedia to build simple models that represent the pattern of terms (and even equations) that are definitive of the method.
- We then want to match methods sections of papers (that cite Github repos) to these different models. By way of being a citation, we make the assumption that the Github repos cited are relevant to what is being talked about. In terms of scope, I think we want as much text as possible, and it would be dangerous to limit lines to those within some distance of the citation. I think we should just associate Github repos cited in a paper with all the text, and maximally parse down to methods if possible. We can do a fuzzy classification so that each "matching" is just a probability that the Github repo is related to some Wikipedia term model, as determined by matching text in the paper to text that describes the method.
- Once we have Github repos matched to methods, then we can do two things. 1) We can try to use features of the repos to build models that can classify a repo method based on its features (and this means you can classify any new repo sans a paper), and 2) we can look into the subsets and derive metrics that try to rank which is best (based on reproducibility, documentation, etc).

The end product is classifying Github repos into methods and/or domains, and then ranking. This would be hugely useful for people to find software to accomplish some task. It would also allow for being able to take a paper, and overlay a "heatmap" for different method probabilities discussed in the text.


### Idea 2: Can we find similar repos/functions based on equations from papers?
An additional (cool) component to the above would be to try and parse equations in papers, and then match them to features of equations (and we could use Wikipedia or Wolfram Alpha, or something else). If we start by not caring about Github repos, this would significantly increase the size of the analysis set. We would use the equations to match papers to methods, and use this grouping to drive some further analysis of the text. I think this could be a feature set to supplement the goal for idea 1, but likely I could think of other uses for this (not reliant on having access to code repos).


### Idea 3: Can we identify components of good software?
A very salient observation about the repos that I parsed from Pubmed Central is that there were several that were cited hundreds of times, especially related to biology / genomics - based software. This introduces huge opportunity, because we can use this as a metric that "this is good software" - many researchers using it means that it must be useful/good for something! As before, we would first want to group the software into categories based on the text context, a much easier task given each will have many citations. We would then want to derive some "control set" for comparison - e.g., software that is referenced in a similar context, but is not cited more than once (and we would want to set some date threshold to prevent false negatives - software that is great but is just newly released). The workflow would be as follows:

- Find software repos that are cited above some threshold, parse contexts to build a model (e.g., word2vec) that represents the context the software is found in.
- Match this context to methods via wikipedia, wolphram alpha, as before (to give a grouping)
- Derive a set for comparison - software in the same context that is not widely cited.
- Extract repo features for both sets, and find distinguishing features.

We would (hopefully) at the end be able to make a statement about the features of the software that distinguish it. We could then look for these features in newer repos to predict usage, etc, or even give people a metric to evaluate the potential usability of their software.


# Analysis

### Step 1: Develop vector representations of methods
I first found [a list of statistical methods](https://en.wikipedia.org/wiki/List_of_statistics_articles) on wikipedia, and [used repofish](0.make_method_models.py) to extract [images, links, and text](wikipedia_methods.json) for these different methods, and build [vector representations](../models/method_vectors.tsv) of the methods. I did this by [compiling all summary text](method_sentences.txt) of the methods to build a [word2vec model](../models/methods_word2vec.word2vec), and mapping each individual method to the model to generate [vector representations](../models/method_vectors.tsv) for them. I could then calculate pairwise similarities for the vector representations, and threshold the matrix at similarity scores of 0.8 and 0.9 to make graphs that show the similarity of the methods as determined by the different summary (text) contexts.

- [similarity graph of statistical methods, threshold = 0.9](https://labs.graphistry.com/graph/graph.html?type=vgraph&viztoken=acabb667a7d268b52caf34c67f1c86de6177f5d6&usertag=72805b68-pygraphistry-0.9.27&info=true&dataset=Users%2FRKRIEGOLNR_lwxhqwbjpfee2d9rudi&play=0)
- [similarity graph of statistical methods, threshold = 0.8](https://labs.graphistry.com/graph/graph.html?type=vgraph&viztoken=2f7e6fb4440069813acdd10d8bc79ac4156fee00&usertag=72805b68-pygraphistry-0.9.27&info=true&dataset=Users%2FWVVV9SXTAS_h4dn3ln5n4dt49uow29&play=0)

### Step 2: Assess method similarity based on equations
I wrote [a script](2.extract_equations.py) to extract equations from these same methods pages, and will use [this data](wikipedia_methods.json) to derive equivalent comparisons between methods based on the equations (LaTEx). (in progress)


### Step 3: Mapping pubmed papers into the method space
I will derive a vector representation of text from papers in pubmed central to map them onto this method space, and I might also do the same if equations are present.


### Step 4: Map associated code to methods
Based on locations of citations in a subset of the papers, I can possibly infer that the code referenced is related to what is being discussed in the text. This will allow me to map repos to the equivalent method space via the text.

And more TBA!
