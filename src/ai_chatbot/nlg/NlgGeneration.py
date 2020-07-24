import csv
import random


class NlgGeneration:
    def __init__(self):
        self.helloPhrase = []
        self.errorPhrase = []
        self.missingDep = []
        self.missingArr = []
        self.missingDepTime = []
        self.missingArrTime = []
        self.missingDelDepTime = []
        self.missingDate = []
        self.missingInter = []
        self.missingExpArr = []
        self.missingInterArr = []
        self.exit = []
        self.badDate = []
        self.badTime = []
        self.singleReturn = []
        self.returnDate = []
        self.returnTime = []
        self.phrase_loader("ai_chatbot/nlg/phrases.dsv")

    def hello_user(self):
        return random.choice(self.helloPhrase)

    def ticket_display(self, departing, arrival, date, time, price, url):
        return_string = []
        return_string.append("The current cheapest ticket from")
        return_string.append(departing)
        return_string.append("to")
        return_string.append(arrival)
        return_string.append("on the date")
        return_string.append(date)
        return_string.append("departing at")
        return_string.append(time)
        return_string.append("is:")
        return_string.append(price + ".")
        return_string.append("Click here to book:")
        return_string.append(url)
        return ' '.join(return_string)

    def missing_departure(self):
        return random.choice(self.missingDep)

    def missing_arrival(self):
        return random.choice(self.missingArr)

    def missing_date(self):
        return random.choice(self.missingDate)

    def missing_dep_time(self):
        return random.choice(self.missingDepTime)

    def missing_arr_time(self):
        return random.choice(self.missingArrTime)

    def missing_del_dep_time(self):
        return random.choice(self.missingDelDepTime)

    def which_station(self, location):
        return_string = []
        return_string.append("Which station in")
        return_string.append(location)
        return_string.append("did you want?")
        return ' '.join(return_string)

    def confirm_book_selection(self, depart, arrival, date, time, ticket, delay, retdate, rettime):
        return_string = []
        return_string.append("you said:")
        return_string.append("a")
        return_string.append(ticket)
        return_string.append("ticket from")
        return_string.append(depart)
        return_string.append("to")
        return_string.append(arrival)
        return_string.append("on the")
        return_string.append(date)
        return_string.append("at")
        return_string.append(time)
        if delay is True:
            return_string.append(", returning on the")
            return_string.append(retdate)
            return_string.append("at")
            return_string.append(rettime)
        return_string.append("- Is that correct?")
        return ' '.join(return_string)

    def no_process(self):
        return random.choice(self.errorPhrase)

    def delay_display(self, delay_data):
        return_string = []
        return_string.append("Apologies, your train will arrive instead: ")
        return_string.append(delay_data)
        return_string.append(" minutes later.")
        return ' '.join(return_string)

    def missing_intermediate_station(self):
        return random.choice(self.missingInter)

    def missing_expected_arrival_time(self):
        return random.choice(self.missingExpArr)

    def missing_intermediate_station_arrival(self):
        return random.choice(self.missingInterArr)

    def exit_conversation(self):
        return random.choice(self.exit)

    def bad_date(self):
        return random.choice(self.badDate)

    def bad_time(self):
        return random.choice(self.badTime)

    def missing_single_or_return(self):
        return random.choice(self.singleReturn)

    def missing_return_date(self):
        return random.choice(self.returnDate)

    def missing_return_time(self):
        return random.choice(self.returnTime)

    def phrase_loader(self, doc_loc):
        with open(doc_loc) as csvfile:
            reader = csv.reader(csvfile, delimiter='$')
            for row in reader:
                if len(row) == 2:
                    type = row[0].lower()
                    if type == "hello":
                        self.helloPhrase.append(row[1])
                    elif type == "error":
                        self.errorPhrase.append(row[1])
                    elif type == "dep":
                        self.missingDep.append(row[1])
                    elif type == "arr":
                        self.missingArr.append(row[1])
                    elif type == "deptime":
                        self.missingDepTime.append(row[1])
                    elif type == "arrtime":
                        self.missingArrTime.append(row[1])
                    elif type == "deldeptime":
                        self.missingDelDepTime.append(row[1])
                    elif type == "date":
                        self.missingDate.append(row[1])
                    elif type == "inter":
                        self.missingInter.append(row[1])
                    elif type == "exparr":
                        self.missingExpArr.append(row[1])
                    elif type == "interarr":
                        self.missingInterArr.append(row[1])
                    elif type == "exit":
                        self.exit.append(row[1])
                    elif type == "baddate":
                        self.badDate.append(row[1])
                    elif type == "badtime":
                        self.badTime.append(row[1])
                    elif type == "singlereturn":
                        self.singleReturn.append(row[1])
                    elif type == "returndate":
                        self.returnDate.append(row[1])
                    elif type == "returntime":
                        self.returnTime.append(row[1])
                else:
                    print("that phrase is invalid!")
