import string
import spacy
from spacy.vocab import Vocab
from sense2vec import Sense2VecComponent
import difflib
import re

from ai_chatbot.scripts.QuestionDomain.Question import Question
from ai_chatbot.scripts.QuestionDomain.QuestionNode import QuestionNode
import csv

class QuestionProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        s2v = Sense2VecComponent('/path/to/reddit_vectors-1.1.0')
        self.nlp.add_pipe(s2v)
        self.elements = {}
        with open('ai_chatbot/scripts/QuestionDomain/csv/TAG_ELEMENT.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                self.elements[row[0]] = row[1:-1]

        self.ordinal = {}
        with open('ai_chatbot/scripts/QuestionDomain/csv/TAG_ORDINAL.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                self.ordinal[row[0]] = int(row[1])

    def searchprocess(self, tree, question=''):
        path = self.generatePath(question)
        print('Path : {0}'.format(path))
        if tree.pathExist(path):
            node = tree.goto(path)
            closest = self.getClosestMatch(node.getQuestionList(), question)
            found = node.fetchQuestion(closest)
            return found.answer
        else:
            Exception('Question not found')

    def generatePath(self, question=''):
        processed = self.processquestion(question)
        print('question processed : {0}'.format(processed))
        return self.constructPath(processed)

    def processquestion(self, quest=''):
        # apply lower case
        question = quest.lower()
        # Remove punctuation
        question = self.removePunctuation(question)
        question = self.removePunctuation(question)
        processlist = question.split(' ')
        # remove duplicate
        processlist = self.removeDuplicate(processlist)
        # remove synonyms
        processlist = self.removeSynonym(processlist)
        return processlist

    def constructPath(self, sentence=[]):
        pathATR = {}
        for word in sentence:
            for key, lst in self.elements.items():
                if word in lst:
                    pathATR[key] = word
                    sentence.remove(word)
                    break
        print('Path pre-sort: {0}'.format(pathATR.values()))
        sortedPath = {k: v for k, v in sorted(pathATR.items(), key=lambda item: self.getOrdinalByKey(item[0]))}
        return self.unpackNestedList(list(sortedPath.values()))

    def removeDuplicate(self, input=[]):
        return list(dict.fromkeys(input))

    def removePunctuation(self, sentence=''):
        punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
        result = ''
        for char in sentence:
            if char not in punctuations:
                result = result + char
        return result

    def removeSynonym(self, input=[]):
        result = []
        while len(input) > 0:
            word = input.pop(0)
            synonymDictionary = self.getSynonymList(word)
            for compareword in input:
                if compareword in synonymDictionary:
                    input.remove(compareword)
            result.append(word)
        return result

    def getSynonymList(self, word):
        synonyms = self.most_similar(self.nlp.vocab[word])
        queries = [syn.text for syn in synonyms]
        return queries

    def most_similar(self, word):
        queries = [w for w in word.vocab if w.is_lower == word.is_lower and w.prob >= -15]
        by_similarity = sorted(queries, key=lambda w: word.similarity(w), reverse=True)
        return by_similarity[:7]

    def getOrdinalByKey(self, key):
        return self.ordinal[key]

    def getClosestMatch(self,lst, sentence):
        print('finding "{0}" in {1}'.format(sentence,lst))
        result =  difflib.get_close_matches(sentence, lst)
        print('result : {0}'.format(result))
        return result[0]

    def unpackNestedList(self, lst):
        res = []
        for item in lst:
            if isinstance(item, list):
                res += item
            else:
                res.append(item)
        return res

    def simiplifySentence(self, inp=''):
        doc = self.nlp(inp)
        removeword = ''
        for token in doc:
            if token.pos_ in ['DET', 'CCONJ']:
                inp = inp.replace(token.text, '')
            elif token.text != token.lemma_:
                inp = inp.replace(token.text, token.lemma_)
            inp = re.sub(' +', ' ', inp)
        return inp
