# encoding: utf-8
from agate import Table, Computation, Text
import requests
from bs4 import BeautifulSoup
from questions import QUESTIONS
from utils import rename_column

class VoteWatcher(object):
    """
    Example usage:
    # Init vote watcher
    x = VoteWatch(128,"https://www.eduskunta.fi/FI/vaski/Sivut/Aanestys.aspx?aanestysnro=19&istuntonro=82&vuosi=2015")
    
    # Print a table with all MP's
    x.table_all.to_csv("table.csv")

    # Print a table with only people that changed opinions
    x.table_diff.to_csv("table_change.csv")    
    """

    def __init__(self, question_id, vote_url, reverse=False):
        """ 
        - question_id : an id of a question as defined in questions.py 
        - vote_url    : a url the the voting record of on eduskunta.fi
            ie. https://www.eduskunta.fi/FI/vaski/Sivut/Aanestys.aspx?aanestysnro=19&istuntonro=82&vuosi=2015
        - reverse    : Set to true if "agree" in election mahcine equals
            "no" in parliament vote.
        """
        self.vote_url = vote_url
        self.reverse = reverse
        try:
            self.question = QUESTIONS[question_id]
        except KeyError:
            raise ValueError("No such question id")

        self._get_promise_table()
        self._get_vote_table()
        self._compare_answers()

    def _get_promise_table(self):
        """ Get the answers from the voting advice application
        """
        print "Get election machine data (YLE)"
        table = Table.from_csv("yle-vaalikone-2015.csv")\
            .where(lambda row: row["valittu"] == 1)\
            .select(["nimi", "puolue", self.question])
        self.promise_table = rename_column(table, self.question, "promise")

    def _get_vote_table(self):
        """ Get the votes of every mp
        """
        print "Get votes from eduskunta.fi"
        resp = requests.get(self.vote_url)
        soup = BeautifulSoup(resp.text, "html.parser")

        """ TODO: Make a better selector
        """
        _rows = [] 
        trs = soup.find_all("li", {"class": "expand"})[1].find("table").find_all("tr")
        for row in trs:
            cells = row.find_all("td")
            name_cell = cells[0].text.split("/")
            name = name_cell[0].strip()
            party = name_cell[1].strip()
            vote = cells[1].text
            _rows.append([name, party, vote])

        self.vote_table = Table(_rows, column_names=["name", "party", "vote"])


    def _compare_answers(self):
        """ Check if the answers in the voting mahcine correspond with the
            vote.
        """
        print "Compare promises and votes"
        table = self.vote_table.join(self.promise_table,"name", right_key="nimi")
        self.table_all = table.compute([
            ("comparison", AnswerComparison())
        ])
        self.table_diff = self.table_all\
            .where(lambda row: row['comparison'] == "different opinion")
        
        print "Found %s MP's that didn't vote according to their promises." % len(self.table_diff.rows)


class AnswerComparison(Computation):
    """ Check if answer in election machine and vote correspond.
    """
    def _translate_promise(self, value):
        if not value:
            return None

        if "eri" in value:
            return "disagree"
        elif "samaa" in value:
            return "agree"
        else:
            return None

    def _translate_vote(self, value):
        if not value:
            return None

        if value == "Ei":
            return "disagree"
        elif value == "Jaa":
            return "agree"
        else:
            return None

    def __init__(self, reverse=False):
        self.reverse = reverse

    def get_computed_data_type(self, table):
        return Text()

    def run(self, row):
        promise = self._translate_promise(row["promise"])
        vote = self._translate_vote(row["vote"])

        if promise and vote:
            if promise == vote and not self.reverse:
                return "same opinion"
            else:
                return "different opinion"
        else:
            return None