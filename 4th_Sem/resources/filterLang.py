from langdetect import detect

class FilterLanguage(object):
    
    def detect_language(line):
        return detect(line)

    def to_ascii(string_with_nonASCII):
        encoded_string = string_with_nonASCII.encode("ascii", "ignore")
        decode_string = encoded_string.decode()
        return decode_string

    def filter_lang_text(filename,outfilename,enc='utf-8'):
        text_file = open(filename, "r", encoding=enc)
        no_str = text_file.read()
        text_file.close()
        # make a list
        lines = no_str.split("\n")

        comments = []

        for i in range(0, len(lines)):
            line2 = lines[i]
            line = FilterLanguage.to_ascii(line2)
            try:
                if(len(line) > 0 and FilterLanguage.detect_language(line) == 'en'):
                    comments.append(line)
            except:
                pass

        with open(outfilename, mode='wt', encoding=enc) as myfile:
            myfile.write('\n'.join(comments))
