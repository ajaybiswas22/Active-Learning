import re
import os
import num2words
import numpy as np
from tqdm.notebook import tqdm
from utility.twokenize import tokenizeRawTweetText as tknzr
from bs4 import BeautifulSoup

def removeMarkup(string:str):
    soup = BeautifulSoup(string)
    return soup.getText()

def regexOr(items:tuple):
	regex = '|'.join(items)
	regex = '(' + regex + ')'
	return regex

def pos_lookahead(regex:str):
	return '(?=' + regex + ')'

def optional(regex:str):
	return '(%s)?' % regex

PunctChars = r'''[`'“".?!,:;]'''
Punct = '%s+' % PunctChars
Entity = '&(amp|lt|gt|quot);'

def removeUrls(string:str):
	UrlStart1 = regexOr('https?://', r'www\.',r'bit.ly/')
	CommonTLDs = regexOr('com','co\\.uk','org','net','info','ca','biz','info','edu','in','au')
	UrlStart2 = r'[a-z0-9\.-]+?' + r'\.' + CommonTLDs + pos_lookahead(r'[/ \W\b]')
	UrlBody = r'[^ \t\r\n<>]*?'
	UrlExtraCrapBeforeEnd = '%s+?' % regexOr(PunctChars, Entity)
	UrlEnd = regexOr( r'\.\.+', r'[<>]', r'\s', '$')
	Url = optional(r'\b') + regexOr(UrlStart1, UrlStart2) + UrlBody + pos_lookahead(optional(UrlExtraCrapBeforeEnd) + UrlEnd)

	Url_RE = re.compile("(%s)" % Url, re.U|re.I)
	string = re.sub(Url_RE, " constanturl ", string)

	URL_regex2 = r'\b(htt)[p\:\/]*([\\x\\u][a-z0-9]*)*'
	string = re.sub(URL_regex2, " constanturl ", string)
	return string

def removeEscapes(string:str):
    escapes = ''.join([chr(x) for x in range(1, 32)])
    translator = str.maketrans('', '', escapes)
    string = string.translate(translator)
    return string

def clearExtraSpaces(string:str):
    counter = 16
    while counter>0:
        counter -= 1
        string = string.replace("  "," ")
    return string.strip()

def removeSymbols(string):
    string = re.sub(re.compile(r'[\(\)\[\]\{\}\\\"\-]'),' ',string)
    string = re.sub(re.compile(r'[\+\*\?\|\.\$\^\'\`]'),' ',string)
    string = re.sub(re.compile(r'[!#&/<>;:,@%=_~]'),' ',string)
    string = clearExtraSpaces(string)
    return string

def replacePatterns(string:str):
    commonPatterns = [(r' won\'t', ' will not '), (r' can\'t ', ' cannot '), (r' i\'m ', ' i am '), (r' any1 ', ' anyone '),
                    (r' every1 ', ' everyone '), (r' (\w+)\'ll ', ' \g<1> will '), (r' (\w+)n\'t ', ' \g<1> not '),
                    (r' (\w+)\'ve ', ' \g<1> have '), (r' (\w+)\'re ', ' \g<1> are '), (r' (\d+)x ', ' \g<1> times '),
                    (r' (\d+)k ', ' \g<1> thousand '), (r' (\d+)m ', ' \g<1> million '), (r' (\d+)b ', ' \g<1> billion ')]
    for (pattern, replacement) in commonPatterns:
        string = re.sub(re.compile(pattern), replacement, string)
    return string

def num2Words(string:str):
    if string.isalpha() is True:
        return string
    string = string.replace(',','')
    while len(string) % 3 != 0:
        string = "0" + string

    numInWords = ""
    tokens = [string[ix:ix+3] for ix in range(0, len(string), 3)]
    suffixes = [" ", " thousand ", " million ", " billion ", " trillion ",
                " quadrillion ", " quintillion ", " sextillion ", " septillion "][:len(tokens)][::-1]
    
    for x in range(len(tokens)):
        if num2words.num2words(tokens[x]) != "zero":
            numInWords += num2words.num2words(tokens[x]) + suffixes[x]
    return numInWords.replace('-',' ')

def splitAlphanumeric(string:str):
    if string.isnumeric() or string.isalpha():
        return [string]
    else:
        token = ""
        tokenList = []
        for char in string:
            if len(token) == 0:
                token += char
            else:
                if token[-1].isnumeric() and char.isnumeric():
                    token += char
                elif token[-1].isalpha() and char.isalpha():
                    token += char
                elif token[-1].isnumeric() and char.isalpha():
                    tokenList.append(token)
                    token = "" + char
                elif token[-1].isalpha() and char.isnumeric():
                    tokenList.append(token)
                    token = "" + char
        tokenList.append(token)
        return tokenList

def processNumbersInString(string:str):
    tokenized = []
    for token in tknzr(string):
        tokenized.extend(splitAlphanumeric(token))
    
    textOnlyTokenized = []
    for token in tokenized:
        try:
            textOnlyTokenized.append(num2Words(token))
        except:
            continue
    string = ' '.join(textOnlyTokenized)
    string = clearExtraSpaces(string)
    return string

def unifyLanguage(string:str):
    englishChars = englishWithoutSymbols()
    hindiChars = hindiWithoutSymbols()
    englishCount = sum([(char in englishChars) for char in string])
    hindiCount = sum([(char in hindiChars) for char in string])
    if englishCount > hindiCount:
        string = ''.join([char for char in string if char in englishChars+" "])
    else:
        string = ''.join([char for char in string if char in hindiChars+" "])
    string = clearExtraSpaces(string)
    return string

def simplePreprocess(corpus:list[str]):
    processedCorpus = []
    for x in tqdm(range(len(corpus))):
        processedComment = lowercase(clearExtraSpaces(' '.join([token for token in tknzr(corpus[x]) if token.isalpha() is True])))
        if len(processedComment) != 0:
            processedCorpus.append(processedComment)
    return processedCorpus

def simplePreprocess2(corpus:list[str]):
    processedCorpus = []
    keptComments = []
    for x in tqdm(range(len(corpus))):
        processedComment = lowercase(clearExtraSpaces(' '.join([token for token in tknzr(corpus[x]) if token.isalpha() is True])))
        if len(processedComment) != 0:
            processedCorpus.append(processedComment)
            keptComments.append(x)
    return processedCorpus, keptComments

def lowercase(string:str):
    return string.lower()

def checkAlphaWord(string:str):
    return string.isalpha()

def checkAlphaPhrase(string:str):
    tokenized = tknzr(string)
    alphaStatus = [str(x).isalpha() for x in tokenized]
    if False in alphaStatus:
        return False
    return True

def restrictVocabularyString(string:str, vocabulary:list[str]):
    return ' '.join(x for x in tknzr(string) if x in vocabulary)

def restrictVocabularyCorpus(corpus:list[str], vocabulary:list[str]):
    return [restrictVocabularyString(string, vocabulary) for string in corpus]

def listIntersection(listA:list, listB:list):
    listA, listB = (listA, listB) if len(listA) < len(listB) else (listB, listA)
    return set(listA).intersection(listB)
    
def listIntersectionLength(listA:list, listB:list):
    listA, listB = (listA, listB) if len(listA) < len(listB) else (listB, listA)
    return len(set(listA).intersection(listB))

def collapseString(string:str):
    return string.replace(" ","")

def makeDirectory(folderPath:str):
    try:
        os.mkdir(folderPath)
    except FileExistsError:
        return

def charRange(ucx1:int, ucx2:int):
        for c in range(ucx1, ucx2+1):
            yield chr(c)
        
def englishWithSymbols():
    allowedChars = ""  
    for c in charRange(0x00000020, 0x0000007E):
        allowedChars += c
    return allowedChars

def hindiWithSymbols():
    allowedChars = ""
    for c in charRange(0x00000900, 0x0000097F):
        allowedChars += c
    return allowedChars

def englishWithoutSymbols():
    allowedChars = ""  
    for c in charRange(0x00000041, 0x0000005A):
        allowedChars += c
    for c in charRange(0x00000061, 0x0000007A):
        allowedChars += c
    return allowedChars

def hindiWithoutSymbols():
    allowedChars = ""
    for c in charRange(0x00000900, 0x00000950):
        allowedChars += c
    for c in charRange(0x00000955, 0x00000963):
        allowedChars += c
    for c in charRange(0x00000970, 0x0000097F):
        allowedChars += c
    return allowedChars