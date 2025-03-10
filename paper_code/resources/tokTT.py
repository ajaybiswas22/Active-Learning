from audioop import reverse
import re
from string import punctuation
from nltk import TweetTokenizer
import twokenize
from nltk.tokenize.stanford import StanfordTokenizer
import preprocessor as p
import nltk
import string
nltk.download('wordnet')
lemmatizer = nltk.stem.wordnet.WordNetLemmatizer()
from resources.basicIO import InputOutput as IO

posMapping = {
    # "First_Letter by nltk.pos_tag":"POS_for_lemmatizer"
    "N": 'n',
    "V": 'v',
    "J": 'a',
    "R": 'r'
}

CLEANR = re.compile('<.*?>')

R_patterns = [
    (r'won\'t', 'will not'),
    (r'can\'t', 'cannot'),
    (r'ain\'t', 'am not'),
    (r'i\'m', 'i am'),
    (r'(\w+)\'ll', '\g<1> will'),
    (r'(\w+)n\'t', '\g<1> not'),
    (r'(\w+)\'ve', '\g<1> have'),
    (r'(\w+)\'s', '\g<1> is'),
    (r'(\w+)\'re', '\g<1> are'),
]

emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)

#HappyEmoticons
emoticons_happy = set([
    ':-)', ':)', ';)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}',
    ':^)', ':-D', ':D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D',
    '=-3', '=3', ':-))', ":'-)", ":')", ':*', ':^*', '>:P', ':-P', ':P', 'X-P',
    'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-b', ':b', '>:)', '>;)', '>:-)',
    '<3'
    ])

# Sad Emoticons
emoticons_sad = set([
    ':L', ':-/', '>:/', ':S', '>:[', ':@', ':-(', ':[', ':-||', '=L', ':<',
    ':-[', ':-<', '=\\', '=/', '>:(', ':(', '>.<', ":'-(", ":'(", ':\\', ':-c',
    ':c', ':{', '>:\\', ';('
])

emoticons = emoticons_happy.union(emoticons_sad)

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

    def removeEmojis(text):
        pattern = re.compile(
            r'[\U0001F300-\U0001F5FF|\U0001F1E6-\U0001F1FF|\U00002700-\U000027BF|\U0001F900-\U0001F9FF|\U0001F600-\U0001F64F|\U0001F680-\U0001F6FF|\U00002600-\U000026FF]')
        return re.sub(pattern, '', text)
    
    def removeStopWords(text,lvl):
        # lvl 0 eng 1 heng 2 hindi
        if(lvl == None):
            return text
        
        for item in lvl:
            text_file = open('resources/stop_words/'+str(item)+'.txt', "r", encoding='utf-8')
            no_str = text_file.read()
            text_file.close()
            # make a list
            lines = no_str.split("\n")
            
            text = ' '.join([word for word in text.split()
                                 if word not in lines])
        return text

    def tokenize(texts, stop_words_lvl=None, to_lower=True, tknzr=TweetTokenizer()):
        
        text = texts
        rep_word = REReplacer()
        text = rep_word.replace(text)
        text = text.strip()

        if(to_lower == True):
            text = text.lower()

        text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))', '', text)
        text = re.sub('(\@[^\s]+)', '', text)
        text = CommentTokenizer.remove_html_tags(text)
        text = CommentTokenizer.remove_punctuation(text)
        text = CommentTokenizer.removeEmojis(text)
        
        if(stop_words_lvl!=None):
            text = CommentTokenizer.removeStopWords(text,stop_words_lvl)

        text = str(re.sub(' +', ' ', text))
        text = text.strip()

        # create tokens
        tokens = nltk.word_tokenize(text.lower())

        output = []

        # populate output
        for token, tag in nltk.pos_tag(tokens):
            try:
                output.append(lemmatizer.lemmatize(token, posMapping.get(tag[0], 'n')))
            except:
                pass

        return ' '.join(output)

    # Loads a textfile, tokenizes it, and converts it into a list
    def cleaned(filename, lvl=None, enc='utf-8'):
       # Load
        text_file = open(filename, "r",encoding=enc)
        no_str = text_file.read()
        text_file.close()
        # make a list
        lines = no_str.split("\n")

        #cleanup
        temp = []
        for comment in lines:
            tok_comment = CommentTokenizer.tokenize(comment,lvl)
            if(len(tok_comment) == 0):
                continue
            temp.append(tok_comment)
        lines = temp

        return lines

    def get_word_frequency(filename):
        huge_list = []

        with open(filename, "r", encoding='utf-8') as f:
            for line in f:
                line = CommentTokenizer.tokenize(line)
                huge_list.extend(line.split())

        frequency = {}
        # iterating over the list
        for item in huge_list:
            # checking the element in dictionary
            if item in frequency:
                # incrementing the count
                frequency[item] += 1
            else:
                # initializing the count
                frequency[item] = 1

        frequency = {k: v for k, v in sorted(frequency.items(), key=lambda item: item[1], reverse=True)}
        return frequency

