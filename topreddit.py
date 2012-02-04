import codecs
import pprint

import reddit

LIMIT = 10000

r = reddit.Reddit(user_agent='my_cool_application')

#submissions = r.get_subreddit('all').get_hot(limit=5)
f = open('results%s.txt' % LIMIT, 'w')
submissions = r.get_subreddit('all').get_top(limit=LIMIT, url_data={"t": "all"})
all = []
for article in submissions:
    all.append(article)
    print str(article)
    f.write(str(article) + '\r\n')

f.close()

#open('list_1000.txt', 'w').write(pprint.pformat([i.title for i in all]))

import re
repeats = {}
for article in all:
    words = re.findall(ur'\w{2,}', article.title)
    for w in words:
        w = w.lower()
        repeats[w] = repeats.get(w, 0) + 1

open('repeats_dict_%s.txt' % LIMIT, 'w').write(pprint.pformat(repeats))

import operator
sorted_repeats = sorted(repeats.iteritems(), key=operator.itemgetter(1))

open('repeats_top_%s.txt' % LIMIT, 'w').write(pprint.pformat(sorted_repeats))



import nltk
import pprint

tokenizer = None
tagger = None


def init_nltk():
    global tokenizer
    global tagger
    tokenizer = nltk.tokenize.RegexpTokenizer(r'''[\w']+|[^\w\s]+''')
    tagger = nltk.UnigramTagger(nltk.corpus.brown.tagged_sents())


def tag(text):
    global tokenizer
    global tagger
    if not tokenizer:
        init_nltk()
    tokenized = tokenizer.tokenize(text)
    tagged = tagger.tag(tokenized)
    tagged.sort(lambda x,y:cmp(x[1],y[1]))
    return tagged

 
pd = {}


for article in all:
    parsed = tag(article.title)
    for word, part in parsed:
        word = word.lower()
        if part not in pd:
            d = dict()
            pd[part] = d
        else:
            d = pd[part]
        
        d[word] = d.get(word, 0) + 1


# kill the 1's

for part, d in pd.items():
    for word, count in d.items():
        if count < 3:
            del d[word]
    if len(d) < 3:
        del pd[part]


tagdict = nltk.data.load('help/tagsets/brown_tagset.pickle')
tagdict_b = nltk.data.load('help/tagsets/upenn_tagset.pickle')
tagdict_c = nltk.data.load('help/tagsets/claws5_tagset.pickle')




fixes = {
    'FW': 'foreign',
    'NC': 'citations',
    'HL': 'headlines',
    'TL': 'titles'
    }


def explain_one(part):
    """
    http://alias-i.com/lingpipe-3.9.3/docs/api/com/aliasi/corpus/parsers/BrownPosParser.html

    Each tag consists of a base tag and optional modifiers. This parser removes 
    all of the modifiers. The modifiers include multiple tags separated by plus-signs
    (eg. EX+BEZ), multiple tags concatenated in the case of negation (eg. BEZ*),
     the prefix modifier FW- for foreign words (e.g. FW-JJ), the suffix modifier -NC for citations (e.g. NN-NC),
     the suffix -HL for words in headlines (e.g. NN-HL-TL in titles (e.g. NNS-TL).
    """
    # Doesn't work because it only prints: nltk.help.upenn_tagset('JJ')
    if part is None:
        return 'Unidentified'
    if part in tagdict:
        data = tagdict[part]
    elif part in tagdict_b:
        data = tagdict_b[part]
    elif part in tagdict_c:
        data = tagdict_c[part]
    else:
        if part in fixes:
            return fixes[part]
        return '?'
    
    return data[0]



def part_explained(part):
    result = explain_one(part)
    if result == '?':
        multi = part.split('-')
        return ' '.join([explain_one(i) for i in multi])
    else:
        return result


#f = open('top_parts_%s.txt' % LIMIT, 'w', encoding='utf-8')
f = codecs.open('top_parts_%s.txt' % LIMIT, 'w', 'utf-8')

for part, d in pd.items():
    sorted_repeats = list(reversed(sorted(d.iteritems(), key=operator.itemgetter(1))))
    f.write('%s - %s' % (str(part), part_explained(part)))
    f.write('\n' + '-' * 50 + '\n')
    #f.write(pprint.pformat(sorted_repeats))
    for pair in sorted_repeats:
        f.write(u'%s\t%s\n' % pair)
    f.write('\n' * 10)


f.close()

ups = sum(i.ups for i in all)
downs = sum(i.downs for i in all)
first = min(i.created_utc for i in all)
last = max(i.created_utc for i in all)
dt = last - first
years = dt / (3600 * 24 * 365)






