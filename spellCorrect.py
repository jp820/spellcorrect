# -*- coding: utf-8 -*-
"""
Created on Mon Jun 24 19:48:23 2019

@author: PravinJadhav
"""

################ Spelling Corrector 

import re
from collections import Counter
from wordsegment import load, segment
from flask import Flask, request, Response
from flask_restful import reqparse, abort, Api, Resource
import json

app = Flask(__name__)
api = Api(app)

load()

#%%
### Correction funtions using norvig's spell correct
def words(text): return re.findall(r'\w+', text.lower())

## Get the dictionary 
WORDS = Counter(words(open('english_words_479k.txt').read()))

def P(word, N=sum(WORDS.values())): 
    "Probability of `word`."
    return WORDS[word] / N

def correction(word): 
    "Most probable spelling correction for word."
    return max(candidates(word), key=P)

def candidates(word): 
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

#%%
# Flask method
@app.route('/api/spellCorrect', methods=['GET'])
    
def spellCorrect():
#    iword = "homassignment"
    cor_list = []
    iword = request.args.get("word")
    print (iword)
    ## First try to segment the input word to see it's a combination of two words
    s1 =segment(iword)
    s1_len = [len(s111) for s111 in s1 if len(s111) <=3]
    
    ## If its a single word, reutrn the possible corrected words.
    if len(s1)==1:
        print (candidates(s1[0]))
        cor_list.append(list(candidates(s1[0])))
    
    ## If inpt word is segmented into more than 3 words, it means it is a single word which was broken 
    ## into small words because of wrong spelling and needs to be corrected.
    elif len(s1)>=3 & len(s1_len) >1:
        print (candidates(iword))
        cor_list.append(list(candidates(iword)))
    
    ### If the input word is a combination of two words, check for segmented words if present in known words.
    else:
        kset = list(known(s1))
        ## If all segmented words are known words, it means there is no need to correction.
        if len(s1) == len(kset):
            print (s1)
            cor_list.append(list(s1))
            
        ## If one of the words is known, form a word from remaining segments and correct it     
        else:
            kset2 = [k1 for k1 in kset if len(k1) >=2 ]
            ukset = [e for e in s1 if e not in kset2]
            ukw = "".join(ukset)
            print ([list(candidates(a22)) for a22 in kset2])
            print (list(candidates(ukw)))
            cor_list.append([list(candidates(a22)) for a22 in kset2])
            cor_list.append(list(candidates(ukw)))
            
    final_dict = {"Corrections" : cor_list}            
    print (final_dict)     
    final_json = json.dumps(final_dict)
    print (final_json)     
          
    return Response(response=final_json, status=200, mimetype="application/json")

app.run(host="0.0.0.0", port=8000)
