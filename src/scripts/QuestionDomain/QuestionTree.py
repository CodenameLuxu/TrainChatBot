
from scripts.QuestionDomain.QuestionNode import QuestionNode
from scripts.QuestionDomain.Question import Question
from scripts.QuestionDomain.QuestionProcessor import QuestionProcessor
from scripts import REResponseCode as Header
import csv

class QuestionTree:
    def __init__(self,root=QuestionNode('root')):
        self.root = root
        self.processor = QuestionProcessor()
    def loadTree(self):
        with open('csv/questionsfile.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                question = row[0]
                answer = row[1]
                tags = self.processor.generatePath(question)
                self.root.addQuestion(Question(question, answer, tags), tags)
                ++line_count
        print('Question tree loaded : {0} lines loaded'.format(line_count))

    def bfs_paths(self , start, goal):
        notFound = True
        queue = [ (start, [start.tag]) ]
        visited = []
        while queue and notFound:
            currentNode, currentPath = queue.pop(0)
            visited.append(currentNode)
            if goal in currentNode.questions:
                notFound = False
                return currentPath,currentNode
            else: 
                if currentNode.branches:
                    for tag, destinationNode in currentNode.branches.items():
                        if destinationNode not in visited:
                            queue.append((destinationNode, currentPath + [tag]))
        return ['X'],Question('404','Not found')
    def pathExist(self, path=[]):
        return self.root.pathExist(path)

    def pathExist(self, path=[]):
        return self.root.pathExist(path)

    def searchfor(self,question=''):
        return self.processor.searchprocess(self,question)

    def find(self,incoming=''):
        resultPath, resultNode  = [],QuestionNode()
        if isinstance(incoming, str):
            resultPath, resultNode = self.bfs_paths(self.root,incoming)
        elif isinstance(incoming, Question):
            resultPath, resultNode = self.bfs_paths(self.root,incoming.question)

        if resultPath[0] == 'X':
            return Header.QUESTION_NOTFOUND
        else:
            return resultNode.fetchQuestion(incoming)

    def goto(self,tags=[]):
        return self.root.goto(tag)
