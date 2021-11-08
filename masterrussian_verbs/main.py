import requests
import json
import random
import codecs

from bs4 import BeautifulSoup
from os.path import exists

class BulkCardBuilder:
    def __init__(self):
        with open("open.json") as f:
            self.open = json.load(f)

        with open("done.json") as f:
            self.done = json.load(f)

        len_open = len(self.open)
        len_done = len(self.done)
        print("Stats: " + str(len_open) + " verbs to go. " + str(len_done) + " verbs done. " + str(len_done / len_open * 100) + "% done!")

        if not exists("cardsoftoday.txt"):
            self.file = codecs.open("cardsoftoday.txt", "w+", "utf-8")
        else:
            self.file = codecs.open("cardsoftoday.txt", "a", "utf-8")

        # Pick random URL from the list.
        self.url = random.choice(range(len(self.open)))

        # Download URL.
        html = self.download_url(self.open[self.url])

        # Go through HTML to gather conjugations.
        table = self.get_conjugation_table(html)

        # self.print_table(table)
        
        # Add cards dialog.
        self.add_cards(table)

    def download_url(self, url):
        r = requests.get(url)
        # UTF-8 to support Cyrillic. 
        r.encoding = 'utf-8'
        return r.text

    class ConjugationTable(object):
        definition = ""
        ipa = ""

        imp_infinitive = ""
        imp_present_conjugations = []
        imp_past_conjugations = []

        per_infinitive = ""
        per_past_conjugations = []
        per_future_conjugations = []

    def get_conjugation_table(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        
        conjugation_table = self.ConjugationTable()  

        # General info
        general_info = soup.find("div", {"class": "col1"}).find("p").find_all("span")
        conjugation_table.ipa = general_info[1].contents[0]
        conjugation_table.definition = general_info[2].contents[0]

        tables = soup.find_all("table", {"class": "verbs"})

        # Table 0 - Infinitives
        conjugation_table.imp_infinitive = tables[0].find("td", {"class": "second"}).contents[0]
        conjugation_table.per_infinitive = tables[0].find("td", {"class": "third"}).contents[0]

        # Table 1 - Imperfective Present Tense
        conjugation_table.imp_present_conjugations = []
        td = tables[1].find_all("td", {"class": "second"})
        for i in range(0,6):
            conjugation_table.imp_present_conjugations.insert(i, td[i].contents[0])

        # Table 2 - Imperfective Past Tense 
        conjugation_table.imp_past_conjugations = []
        td = tables[2].find_all("td", {"class": "second"})
        for i in range(0,4):
            conjugation_table.imp_past_conjugations.insert(i, td[i].contents[0])

        # Table 2 - Perfective Past Tense 
        conjugation_table.per_past_conjugations = []
        td = tables[2].find_all("td", {"class": "third"})
        for i in range(0,4):
            conjugation_table.per_past_conjugations.insert(i, td[i].contents[0])

        # Table 3 - Future Tense
        conjugation_table.per_future_conjugations = []
        td = tables[3].find_all("td", {"class": "third"})
        for i in range(0,6):
            conjugation_table.per_future_conjugations.insert(i, td[i].contents[0])

        return conjugation_table

    def add_cards(self, table):
        print("Making card for " + table.imp_infinitive + " / " + table.per_infinitive)

        image = input("Paste image URL:")
        sentence_with_delimiters = input("Insert sentence (\P for pronoun, \C for conjugation):")

        all_cards = []
        count = [0]

        def get_cards_from_conjugations(conjugation_list, time):
            for idx, val in enumerate(conjugation_list):
                card = "<img src='" + image + "?random=" + str(count[0]) + "'/>;"
                card += self.get_pronoun(idx) + " - " + time + ";"
                # Gap sentence for questioning.
                card += sentence_with_delimiters.replace("\P", self.get_pronoun(idx)).replace("\C", "(" + table.imp_infinitive + ")") + ";"
                # Single word answer for input validation.
                card += val + ";"
                # Full sentence answer
                card += sentence_with_delimiters.replace("\P", self.get_pronoun(idx)).replace("\C", "<b>" + val + "</b>")

                all_cards.insert(len(all_cards), card)
                count[0] += 1

        get_cards_from_conjugations(table.imp_present_conjugations, "Present Tense")
        get_cards_from_conjugations(table.imp_past_conjugations, "Imperfective Paste Tense")
        get_cards_from_conjugations(table.per_past_conjugations, "Perfective Paste Tense")
        get_cards_from_conjugations(table.per_future_conjugations, "Perfective Future Tense")

        pick_n_random = input("How many cards need to be generated? (Max 20, default 10):")

        if pick_n_random == "":
            pick_n_random = 10
        elif int(pick_n_random) > 20:
            pick_n_random = 20

        print("Adding " + str(pick_n_random) + " random cards to file.")

        for i in range(0,int(pick_n_random)):
            chosen_card = random.choice(all_cards)
            
            # Write card to file.
            self.file.write(chosen_card + "\n")

            # Remove to prevent duplicates.
            all_cards.remove(chosen_card)

        # Insert this verb to the done list.
        self.done.insert(len(self.done), self.open[self.url])

        # Remove this verb from the open list.
        self.open.pop(self.url)

        with open('open.json', 'w') as data_file:
            self.open = json.dump(self.open, data_file)

        with open('done.json', 'w') as data_file:
            self.done = json.dump(self.done, data_file)

        print("DONE!")

    def get_pronoun(self, index):
        match index:
            case 0:
                return "я"
            case 1:
                return "ты"
            case 2:
                return "он/она/оно"
            case 3:
                return "мы"
            case 4:
                return "вы"
            case 5:
                return "они"
    
    def get_pronoun_past(self, index):
        match index:
            case 0:
                return "я/он"
            case 1:
                return "я/она"
            case 2:
                return "оно"
            case 3:
                return "мы"

    def print_table(self, table):
        print("Definition: " + table.definition)
        print("Verb: " + table.imp_infinitive + " / " + table.per_infinitive) 
        print("IPA: " + table.ipa) 
        print("Imperfective Present: " + ' - '.join(table.imp_present_conjugations))
        print("Imperfective Past: " + ' - '.join(table.imp_past_conjugations))
        print("Perfective Past: " + ' - '.join(table.per_past_conjugations))
        print("Perfective Future: " + ' - '.join(table.per_future_conjugations))

if __name__ == '__main__':
    BulkCardBuilder()