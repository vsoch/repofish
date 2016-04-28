### Idea 1: Can we find similar repos/functions based on context from papers?

I would want a web interface where I can go, select some word or n-gram (likely a method, keyword, or domain, e.g., linear regression or sequence alignment) and immediately be shown Github repos that serve that purpose. If we can map out research software based on these groupings, we can then look at subsets and start to ask questions that quantify and compare reproducible practices, patterns in scripting, etc. The steps to complete this are as follows:

- First we need a list of methods that we want to understand. We can use wikipedia to build simple models that represent the pattern of terms (and even equations) that are definitive of the method.
- We then want to match methods sections of papers (that cite Github repos) to these different models. By way of being a citation, we make the assumption that the Github repos cited are relevant to what is being talked about. In terms of scope, I think we want as much text as possible, and it would be dangerous to limit lines to those within some distance of the citation. I think we should just associate Github repos cited in a paper with all the text, and maximally parse down to methods if possible. We can do a fuzzy classification so that each "matching" is just a probability that the Github repo is related to some Wikipedia term model, as determined by matching text in the paper to text that describes the method.
- Once we have Github repos matched to methods, then we can do two things. 1) We can try to use features of the repos to build models that can classify a repo method based on its features (and this means you can classify any new repo sans a paper), and 2) we can look into the subsets and derive metrics that try to rank which is best (based on reproducibility, documentation, etc).

The end product is classifying Github repos into methods and/or domains, and then ranking. This would be hugely useful for people to find software to accomplish some task.


### Idea 2: Can we find similar repos/functions based on equations from papers?
An additional (cool) component to the above would be to try and parse equations in papers, and then match them to features of equations (and we could use Wikipedia or Wolfram Alpha, or something else). If we start by not caring about Github repos, this would significantly increase the size of the analysis set. We would use the equations to match papers to methods, and use this grouping to drive some further analysis of the text. I think this could be a feature set to supplement the goal for idea 1, but likely I could think of other uses for this (not reliant on having access to code repos).


### Idea 3: Can we identify components of good software?
A very salient observation about the repos that I parsed from Pubmed Central is that there were several that were cited hundreds of times, especially related to biology / genomics - based software. This introduces huge opportunity, because we can use this as a metric that "this is good software" - many researchers using it means that it must be useful/good for something! As before, we would first want to group the software into categories based on the text context, a much easier task given each will have many citations. We would then want to derive some "control set" for comparison - e.g., software that is referenced in a similar context, but is not cited more than once (and we would want to set some date threshold to prevent false negatives - software that is great but is just newly released). The workflow would be as follows:

- Find software repos that are cited above some threshold, parse contexts to build a model (e.g., word2vec) that represents the context the software is found in.
- Match this context to methods via wikipedia, wolphram alpha, as before (to give a grouping)
- Derive a set for comparison - software in the same context that is not widely cited.
- Extract repo features for both sets, and find distinguishing features.

We would (hopefully) at the end be able to make a statement about the features of the software that distinguish it. We could then look for these features in newer repos to predict usage, etc, or even give people a metric to evaluate the potential usability of their software.

