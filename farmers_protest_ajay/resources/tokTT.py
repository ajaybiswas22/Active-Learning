import re
from string import punctuation
from nltk import TweetTokenizer
from nltk.tokenize.stanford import StanfordTokenizer
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet

nltk.download('stopwords')
cachedStopWords = stopwords.words("english")
CLEANR = re.compile('<.*?>')


R_patterns = [
    (r'won\'t', 'will not'),
    (r'can\'t', 'cannot'),
    (r'i\'m', 'i am'),
    (r'(\w+)\'ll', '\g<1> will'),
    (r'(\w+)n\'t', '\g<1> not'),
    (r'(\w+)\'ve', '\g<1> have'),
    (r'(\w+)\'s', '\g<1> is'),
    (r'(\w+)\'re', '\g<1> are'),
]

class REReplacer(object):
   def __init__(self, pattern=R_patterns):
      self.pattern = [(re.compile(regex), repl) for (regex, repl) in pattern]

   def replace(self, text):
      s = text
      for (pattern, repl) in self.pattern:
         s = re.sub(pattern, repl, s)
      return s

class CommentTokenizer(object):

    def remove_punctuation(text):
        punct_list = list(punctuation)
        for punc in punct_list:
            if punc in text:
                text = text.replace(punc, ' ')
        return text.strip()


    def remove_html_tags(raw_html):
        cleantext = re.sub(CLEANR, '', raw_html)
        return cleantext

    def format_token(token):
        """"""
        if token == '-LRB-':
            token = '('
        elif token == '-RRB-':
            token = ')'
        elif token == '-RSB-':
            token = ']'
        elif token == '-LSB-':
            token = '['
        elif token == '-LCB-':
            token = '{'
        elif token == '-RCB-':
            token = '}'
        return token

    # Returns the tokenized sentence
    def tokenize(sentence, to_lower=True, tknzr=TweetTokenizer()):
        """Arguments:
            - tknzr: a tokenizer implementing the NLTK tokenizer interface
            - sentence: a string to be tokenized
            - to_lower: lowercasing or not
        """
        rep_word = REReplacer()
        sentence = rep_word.replace(sentence)
        sentence = sentence.strip()
        sentence = ' '.join([CommentTokenizer.format_token(x) for x in tknzr.tokenize(sentence)])
        if to_lower:
            sentence = sentence.lower()
        # replace urls by <url>
        sentence = re.sub(
            '((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))', '', sentence)
        # replace @user268 by <user>
        sentence = re.sub('(\@[^\s]+)', '', sentence)

        filter(lambda word: ' ' not in word, sentence)

        #remove single letter words
        sentence = ' '.join([w for w in sentence.split() if len(w) > 1])

        sentence = CommentTokenizer.remove_html_tags(sentence)
        sentence = CommentTokenizer.remove_punctuation(sentence)
        sentence = ' '.join([word for word in sentence.split()
                            if word not in cachedStopWords])
        return sentence

    # Loads a textfile, tokenizes it, and converts it into a list
    def cleaned(filename):
       # Load
        text_file = open(filename, "r")
        no_str = text_file.read()
        text_file.close()
        # make a list
        lines = no_str.split("\n")

        #cleanup
        temp = []
        for comment in lines:
            tok_comment = CommentTokenizer.tokenize(comment)
            temp.append(tok_comment)
        lines = temp

        return lines

