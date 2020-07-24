import spacy
import csv
from spacy.pipeline import EntityRuler
from spacy.tokens.span import Span
from spacy.tokens import Token
from ai_chatbot.nlp.Locations import StationDictionary


class PatternMaker:
    def __init__(self):

        self.locations = StationDictionary.station_dictionary_builder()
        self.nlp = spacy.load("en_core_web_lg")
        self.ruler = EntityRuler(self.nlp)

        # Station and Station code rules
        self.patterns = []
        for loc in self.locations:
            tokens = loc.name.split(' ')
            pattern = []
            for word in tokens:
                pattern.append({"LOWER": word.lower()})
            name = {"label": "STN", "pattern": pattern, "id": loc.station_code.lower()}
            station_code = {"label": "STN", "pattern": [{"TEXT": loc.station_code.upper()}],
                            "id": loc.station_code.lower()}
            self.patterns.append(name)
            self.patterns.append(station_code)

        self.patterns.append({"label": "DATE", "pattern": [
            {"TEXT": {"REGEX": "^([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)\d{4}$"}}], "id": "dat"})
        self.patterns.append(
            {"label": "TIME", "pattern": [{"TEXT": {"REGEX": "^([0-9][0-9])(\:)([0-9][0-9])$"}}], "id": "tim"})
        self.patterns.append(
            {"label": "TIME", "pattern": [{"TEXT": {"REGEX": "^([0-2][0-9]|[0-9])(\:?)([0-9][0-9])?(\ ?)(am|a\.m\.|a\.m|pm|p\.m\.|p\.m)$"}}], "id": "tim"})


        # Booking state rules
        pattern_loader("ai_chatbot/nlp/PatternRules/booking_words.csv", "BOK", "bok", self.patterns)
        pattern_loader("ai_chatbot/nlp/PatternRules/delay_words.csv", "DEL", "del", self.patterns)
        pattern_loader("ai_chatbot/nlp/PatternRules/question_words.csv", "QUE", "que", self.patterns)
        pattern_loader("ai_chatbot/nlp/PatternRules/exit_words.csv", "EXT", "ext", self.patterns)
        pattern_loader("ai_chatbot/nlp/PatternRules/accept_words.csv", "TRUE", "true", self.patterns)
        pattern_loader("ai_chatbot/nlp/PatternRules/deny_words.csv", "FALSE", "false", self.patterns)
        pattern_loader("ai_chatbot/nlp/PatternRules/ticket_return.csv", "TICKET", "return", self.patterns)
        pattern_loader("ai_chatbot/nlp/PatternRules/ticket_single.csv", "TICKET", "single", self.patterns)

        self.ruler.add_patterns(self.patterns)
        self.nlp.add_pipe(self.ruler, before="ner")
        self.nlp.add_pipe(to_and_from, after="ner")
        self.nlp.add_pipe(time_detection, after="ner")

def to_and_from(doc):
    new_ents = []
    for ent in doc.ents:
        # Only check for title if it's a station and not the first token
        if ent.label_ == "STN" and ent.start != 0:
            prev_token = doc[ent.start - 1]
            if prev_token.text.lower() in ("to", "at"):
                new_ent = Span(doc, ent.start, ent.end, label="ARR")
                new_ents.append(new_ent)
            elif prev_token.text.lower() in "from":
                new_ent = Span(doc, ent.start, ent.end, label="DEP")
                new_ents.append(new_ent)
            else:
                new_ents.append(ent)
        else:
            new_ents.append(ent)
    doc.ents = new_ents
    return doc


def time_detection(doc):
    new_ents = []
    for ent in doc.ents:
        if ent.label_ == "CARDINAL":
            next_token = doc[ent.start + 1]
            if next_token.text.lower() in ("pm", "p.m", "p.m.", "am", "a.m", "a.m."):
                new_ent = Span(doc, ent.start, ent.end+1, label="TIME")
                new_ents.append(new_ent)
            else:
                new_ents.append(ent)
        else:
            new_ents.append(ent)
    doc.ents = new_ents
    return doc


def pattern_loader(doc_loc, label, id, patterns):
    with open(doc_loc) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            pattern = []
            for word in row:
                pattern.append({"LOWER": word.lower()})
            patterns.append({"label": label, "pattern": pattern, "id": id})
