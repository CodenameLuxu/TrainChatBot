

class Question:
    question = ""
    answer = ""
    tags = []

    def __init__(self, question='Empty Question', answer='', tags=[]):
        self.question = question
        self.answer   = answer
        self.tags = tags

    def isEmptyQuestion(self):
        return question.answer == ''

    def addTag(self, newTag=''):
        # Empty string check
        if newTag == '':
            return 0
        # Existent check
        if not (newTag.lower() in self.tags):
            self.tags.append(newTag.lower())
        return 1

    def addTags(self, newTags=[]):
        if len(newTags) < 1:
            return 0

        for tag in newTags:
            self.addTag(tag)
        return 1

    def equalTo(self,incoming=''):
        if isinstance(incoming, str):
            return self.question == incoming

        elif isinstance(incoming, Question):
            return self.question == incoming.question

        return False

