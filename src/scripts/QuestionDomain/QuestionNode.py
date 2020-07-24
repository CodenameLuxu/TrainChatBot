from scripts.QuestionDomain.Question import Question


class QuestionNode:
    headerTag = '' #Header tags
    questions = [] #list of question and answers
    branch= {}    # tag : QuestionNode

    def __init__(self, nodeTag='root' ,question=Question(), subbranch={}):
        self.headerTag = nodeTag.lower()
        self.questions = []
        self.branch = subbranch

    def branchExists(self,tag):
        if tag in self.branch.keys():
            return true
        return false;

    def getBranch(self, tag):
        return self.branch[tag]

    def addbranch(self,tag,questionNode):
        if tag in self.branch:
            return 0
        else:
            self.branch[tag] = QuestionNode(nodeTag=tag)

    def pathExist(self,path=[]):
        nexttag =path.pop(0)
        if len(path) == 0 :
            return True
        elif self.branchExists(nexttag):
            return self.branch[next].pathExist(path)
        else:
            return False

    def fetchQuestion(self,incoming=''):
        for entry in self.questions:
            if entry.equalTo(incoming):
                return entry
        return 0

    def addQuestion(self, question=Question(), toVisit=[]):
        if len(toVisit) == 0:
            self.questions.append(question)
            return 1
        else:
            tovisitTag = toVisit.pop(0)
            if not self.branchExists(tovisitTag):
                self.addbranch(tovisitTag)
            self.addbranch(tovisitTag)
            self.getBranch(tovisitTag).addQuestion(question,toVisit)

    def getQuestionList(self):
        lst = []
        for entry in self.questions:
            lst.append(entry.question)
        return lst

    def goto(self, toVisit=[]):
        if len(toVisit) == 0:
            return self
        else:
            tovisitTag = toVisit.pop(0)
            if self.branchExists(tovisitTag):
                return self.getBranch(tovisitTag).goto(toVisit)
            else:
                raise Exception('Path not found')
