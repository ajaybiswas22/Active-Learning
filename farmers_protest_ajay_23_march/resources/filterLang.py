from langdetect import detect
import pandas as pd
from resources.tokTT import CommentTokenizer

# Language detection and filteration class
class FilterLanguage(object):
    # detects language
    def detect_language(line):
        return detect(line)
    
    # converts text to ascii (may remove incompatible letters)
    def to_ascii(string_with_nonASCII):
        encoded_string = string_with_nonASCII.encode("ascii", "ignore")
        decode_string = encoded_string.decode()
        return decode_string
    
    # filters lines of a text file and stores in the outfile
    def filter_lang_text(infile,outfile,enc='utf-8'):
        text_file = open(infile, "r", encoding=enc)
        no_str = text_file.read()
        text_file.close()
        # make a list
        lines = no_str.split("\n")

        # remove duplicates
        lines = list(set(lines))

        comments = []

        for i in range(0, len(lines)):
            line2 = lines[i]
            line = FilterLanguage.to_ascii(line2)
            try:
                if(len(line) > 0 and FilterLanguage.detect_language(line) == 'en'):
                    comments.append(line)
            except:
                pass

        with open(outfile, mode='wt', encoding=enc) as myfile:
            myfile.write('\n'.join(comments))

    # filters csv file texts based on column name (colname)
    def filter_lang_csv(infile, outfile, colname):

        df = pd.read_csv(infile)
        lines = df[colname]

        # remove duplicates
        lines = list(set(lines))

        comments = []

        for i in range(0, len(lines)):
            line2 = lines[i]
            line = FilterLanguage.to_ascii(line2)
            try:
                if(len(line) > 0 and FilterLanguage.detect_language(line) == 'en'):
                    comments.append(line)
            except:
                pass

        df2 = pd.DataFrame({colname: comments})
        df2.to_csv(outfile, index=False)

    def hasKeyword(patterns, word, lvl=2): 
        if(lvl >= 1):
            if(word.lower() in patterns):
                return True
        if(lvl >= 2):
            patterns_space_delimited = ''.join(patterns)
            if(patterns_space_delimited.find(word) != -1):
                return True

        return False

    # filters a text file based on keyword
    def filter_text_keywords(infile, outfile, keywords, threshold, stopwords=['0','1'],enc='utf-8'):

        text_file = open(infile, "r", encoding=enc)
        no_str = text_file.read()
        text_file.close()
        lines = no_str.split("\n")
        filtered_lines = []
        for sentence in lines:
            count = 0
            tokenize_sentence = CommentTokenizer.tokenize(sentence,stopwords)
            patterns = tokenize_sentence.split(' ')
            for word in keywords:
                status = FilterLanguage.hasKeyword(patterns, word)
                if(status == True):
                    count += 1             
                if(count >= threshold):
                    filtered_lines.append(sentence)
                    break
        
        with open(outfile, mode='wt', encoding=enc) as myfile:
            myfile.write('\n'.join(filtered_lines))

