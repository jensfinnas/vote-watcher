# Vote watcher

Vote watcher is a Python module for comparing promises made by MP's in the election machine of YLE to their votes in the parliament.

### Install

`pip install -r requirements.txt`

### Example usage

First find a parliament vote that corresponds to a question in the election machine (see `questions.py` for a list of available questions). For example question number 128 that roughly equals this [vote in parliament](https://www.eduskunta.fi/FI/vaski/Sivut/Aanestys.aspx?aanestysnro=19&istuntonro=82&vuosi=2015).

Then init VoteWatcher.

```
from votewatcher import VoteWatcher
vw = VoteWatcher(128, "https://www.eduskunta.fi/FI/vaski/Sivut/Aanestys.aspx?aanestysnro=19&istuntonro=82&vuosi=2015")
```

Results will be saved in two [Agate](http://agate.readthedocs.org/en/1.1.0/api/table.html) tables. One with all data. One with just the MP's that didn't vote according to their promises.

```
vw.table_all.to_csv("all.csv")
vw.table_diff.to_csv("promise-breakers.csv")
```