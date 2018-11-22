'''

nlp:part of the repofish python package: extracting relationships of terms from corpus
functions for simple natural language processing

Copyright (c) 2016-2018 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from textblob import TextBlob, Word
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.stem import *
import nltk.data
import pandas
import re


def remove_nonenglish_chars(text):
    return re.sub("[^a-zA-Z]", " ", text)

    
def text2sentences(text,remove_non_english_chars=True):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')    
    if remove_non_english_chars:
        text = remove_nonenglish_chars(text)
    for s in tokenizer.tokenize(text):
        yield s


def processText(text):
    '''combines text2sentences and sentence2words'''
    vector = []
    for line in text2sentences(text):            
        words = sentence2words(line)
        vector = vector + words
    return vector



def sentence2words(sentence,remove_stop_words=True,lower=True):
    if isinstance(sentence,list): sentence = sentence[0]
    re_white_space = re.compile("\s+")
    stop_words = set(stopwords.words("english"))
    if lower: sentence = sentence.lower()
    words = re_white_space.split(sentence.strip())
    if remove_stop_words:
        words = [w for w in words if w not in stop_words]
    return words


def unicode2str(unicodestr):
    '''unicode2str decodes unicode into standard string, replacing errors with space
    :param unicodestr: the unicode to convert
    '''
    return unicodestr.decode('utf-8').encode('ascii',errors='replace').replace('?',' ')


def do_stem(words,return_unique=True,remove_non_english_words=True):
    '''do_stem
    Parameters
    ==========    
    words: str/list
        one or more words to be stemmed
    return_unique: boolean (default True)
        return unique terms
    '''
    stemmer = PorterStemmer()
    if isinstance(words,str):
        words = [words]
    stems = []
    for word in words:
        if remove_non_english_words:
            word = re.sub("[^a-zA-Z]", " ", word)
        stems.append(stemmer.stem(word))
    if return_unique:
        return list(set([s.lower() for s in stems]))
    else:
        return stems


def get_total_words(text):
    '''get_total_words:
    get total words in a text (dict, string, or list)
    Parameters
    ==========
    text: str,dict,list
        some text content to parse to count total words
    Returns
    =======
    totalwords: int
        total count of words
    '''
    totalwords = 0

    # Dictionary
    if isinstance(text,dict):
        for label,sentences in text.iteritems():
            if isinstance(sentences,str):
                sentences = [sentences]
            for sentence in sentences:
                blob =  TextBlob(sentence)
                words = do_stem(blob.words)
                totalwords += len(words)
        return totalwords    

    # String or list
    elif isinstance(text,str):
        text = [text]
    for sentence in text:
        blob =  TextBlob(sentence)
        words = do_stem(blob.words)
        totalwords += len(words)
    return totalwords


def get_term_counts(terms,text):
    '''get_term_counts:
    a wrapper for get_term_counts_dict and get_term_counts_list
    will return a pandas data frame of counts for a list of terms of interst
    Parameters
    ==========
    text: dict,list,str
        some text content to parse to count a number of terms
    terms: str,list
        one or more terms to be stemmed and counted in the text
    Returns
    =======
    totalwords: int
        total count of words
    '''
    if isinstance(text,dict):
        return get_term_counts_dict(terms,text)
    elif isinstance(text,str):
        text = [text]
    elif isinstance(text,list):
        return get_term_counts_list(terms,text)


def get_term_counts_list(terms,text):
    # Convert words into stems
    stems = do_stem(terms)

    # data frame hold counts
    counts = pandas.DataFrame(0,columns=["count"],index=stems)

    for sentence in text:
        blob =  TextBlob(sentence)
        words = do_stem(blob.words)
        words = [w for w in words if w in stems]
        counts.loc[words] = counts.loc[words] + 1
    return counts        
    

def get_term_counts_dict(terms,text):
    # Convert words into stems
    stems = do_stem(terms)

    # data frame hold counts
    counts = pandas.DataFrame(0,columns=["count"],index=stems)

    for label,sentences in text.iteritems():
        if isinstance(sentences,str):
            sentences = [sentences]
        for sentence in sentences:
            blob =  TextBlob(sentence)
            words = do_stem(blob.words)
            words = [w for w in words if w in stems]
            counts.loc[words] = counts.loc[words] + 1
    return counts

# Return list of stemmed phrases
def stem_phrases(phrases):
    stemmed = []
    for phrase in phrases:
        phrase = phrase.split(" ")
        if isinstance(phrase,str):
            phrase = [phrase]
        single_stemmed = do_stem(phrase)
        stemmed.append(" ".join(single_stemmed).encode("utf-8"))
    return stemmed

def get_match(phrasematch,entirephrase,found_indices):
    '''
    get_match:

    Function to get a match: start, length, text, from a sentence

    Returns dictionary with:
  
    start_index
    length
    text
    found_indices: updated binary [0,1] list of found indices in entirephrase

    '''

    full_concept = phrasematch.split(" ")
    foundmatch = True
    # We should not find words that have already been found :)
    findices = [i for i in range(0,len(found_indices)) if found_indices[i] == 1]
    for found_index in findices:
        entirephrase[found_index] = "XXXXXXXXXXXXXXXX"
    indices = []
    for word in full_concept:
        if word in entirephrase:
            indices.append(entirephrase.index(word))
        # Missing any one word, not a match
        else:
            foundmatch = False
    if len(set(indices)) == len(full_concept):
        for i in range(0,len(indices)-1):
            # Not in chronological order +1, not a match
            if indices[i]+1 != indices[i+1]:
                foundmatch=False
    # Missing any one word, not a match
    else:
        foundmatch = False
    if foundmatch == True:
        start_index = entirephrase.index(full_concept[0])
        length = len(full_concept)
        text = entirephrase[start_index:start_index+length]   
        # Update found indices
        found_indices[start_index:start_index+length]=1   
    else:
        start_index = 0
        length = 0
        text = ""
    result = {"start_index":start_index,
              "length":length,
              "text":text,
              "found_indices":found_indices}
    return result

def find_phrases(words,vocabulary,repeat=1):
    '''
    words: a list of words
    vocabulary: a list of words / phrases to find in the words
    repeat: the number of times to run over the phrase
    (in case of repeats of same in one sentence)
    
    Returns:
    
    (words_index,vocab_index,word,vocab)
    
    '''
    vocabulary = list(set(vocabulary))
    vocabulary = [v.encode("utf-8") for v in vocabulary]
    # We will stem phrases, and search for them across the stemmed words
    vocab_stemmed = stem_phrases(vocabulary)
    stemmed = [s.encode("utf-8") for s in do_stem(words,return_unique=False)]
    # Make a long regular expression
    regexp = "*|".join(vocab_stemmed) + "*"
    phrases = []

    # Make lookups to return to original vocab and terms
    vocab_lookup = make_lookup(vocabulary,vocab_stemmed)
    words_lookup = make_lookup(words,stemmed)

    # We run it twice in case of repeats in a sentence
    for r in range(0,repeat):
        # Search the sentence for any concepts:
        if re.search(regexp," ".join(stemmed)):
            for c in range(0,len(stemmed)):
                for v in range(len(vocab_stemmed)):
                    single_stemmed = vocab_stemmed[v]
                    if re.match("%s" %(stemmed[c]),single_stemmed):
                        phrases.append((c, v, words_lookup[stemmed[c]],vocab_lookup[vocab_stemmed[v]]))            
    return phrases

def make_lookup(original_list,new_list):
    lookup = dict()
    for x in range(len(new_list)):
        lookup[new_list[x]] = original_list[x]
    return lookup
