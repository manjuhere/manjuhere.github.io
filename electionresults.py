import requests
import urllib.request
import time
from bs4 import BeautifulSoup
import csv
from pytablewriter import MarkdownTableWriter
from pytablewriter.style import Style
import git, os
import time

from datetime import datetime
import pytz
tz = pytz.timezone('Asia/Kolkata')

repo_dir = "/home/ashwin/Desktop/UPP-Election-Result-2019"
file_name = os.path.join(repo_dir, 'index.md')

# print(writer.dumps())
def readStateInfo(filepath):
    _info = []
    with open(filepath, 'r') as csvFile:
        reader = csv.DictReader(csvFile)
        for row in reader:
            # print(dict(row))
            _info.append(row)
    csvFile.close()
    return _info


def getResultConstituency(constituency, party, state="S10", candidate=None):
    # http://eciresults.nic.in/ConstituencywiseS1610.htm?ac=10
    # NEW - https://results.eci.gov.in/ConstituencywiseS1610.htm?ac=10
    # https://results.eci.gov.in/pc/en/constituencywise/Constituencywise{0}{1}.htm?ac={1}
    # resultUrl = "https://results.eci.gov.in/Constituencywise{0}{1}.htm?ac={1}"
    resultUrl = "https://results.eci.gov.in/pc/en/constituencywise/Constituencywise{0}{1}.htm?ac={1}"
    # print(resultUrl.format(state, constituency))
    response = requests.get(resultUrl.format(state, constituency))


    # print(response)
    soup = BeautifulSoup(response.text, "html.parser")
    # votes_table = soup.find('table', {"style": "margin: auto; width: 100%; font-family: Verdana; border: solid 1px black;font-weight:lighter"})
    votes_table = soup.find('table', {"class":"table-party"})
    votes_table_tr = votes_table.find_all('tr')

    _resultDict = None

    for tr in votes_table_tr:
        print(tr)
        if tr != "":
            try:
                _votes = None
                tds = tr.find_all('td')
                if candidate is None:
                    if tds[2].text == party:
                        # print("Candidate: {0} Party: {1}  Votes: {2}".format(tds[0].text, tds[1].text, tds[2].text))
                        _resultDict = {"candidate": tds[1].text, "party": tds[2].text, "votes": int(tds[5].text)}
                        break
                else:
                    if tds[1].text == candidate:
                        # print("Candidate: {0} Party: {1}  Votes: {2}".format(tds[0].text, tds[1].text, tds[2].text))
                        _resultDict = {"candidate": tds[1].text, "party": tds[2].text, "votes": int(tds[5].text)}
                        break
            except Exception as ae:
                _resultDict = None
                pass

    if _resultDict is None:
        return False
    else:
        return _resultDict


while True:

    STATE = "karnataka"
    PARTY = "UPJP"

    _constituencies = readStateInfo("states/{0}.csv".format(STATE))

    _totalVotes = 0
    _totalConstituencyCollected = 0
    _resultList = []

    for _constituency in _constituencies:
        _result = getResultConstituency(constituency=_constituency["constituencyNumber"], party=PARTY)
        if _result:
            _totalConstituencyCollected += 1
            _totalVotes =  _totalVotes + _result["votes"]
            _resultList.append([_constituency["constituencyName"], _result["candidate"], _result["votes"]])
            print("Constituency: {0} \t\t\t Candidate: {1} \t\t\t Votes: {2} \n".format(_constituency["constituencyName"], _result["candidate"], _result["votes"]))
            

    print("\n\n TOTAL VOTES - {0:,} \n Collected from {1}/{2} Constituencies".format(_totalVotes, _totalConstituencyCollected, len(_constituencies)))

    _resultList.sort(key = lambda x: x[2], reverse=True) 

    writer = MarkdownTableWriter()
    writer.headers = ["Constituency", "Candidate", "Votes"]
    writer.value_matrix = _resultList

    writer.styles = [
        Style(align="center"),
        Style(align="center"),
        Style(font_weight="bold", align="right", thousand_separator=","),
    ]

    writer.write_table()

    try:
        india_now = datetime.now(tz)
        file = open("index.md","w") 
        
        file.write("# Election Result UPP 2019\n") 
        file.write("\n---\n")         
        file.write("# TOTAL VOTES - {0:,} \n## (Collected from {1}/{2} Constituencies) \n\n".format(_totalVotes, _totalConstituencyCollected, len(_constituencies))) 
        file.write("\n---\n")         
        file.write("# Results by Constituency \n\n")                 
        file.write("### Last Updated - {0} \n\n\n".format(india_now.strftime("%H:%M | %d-%m-%Y"))) 

        file.write(writer.dumps()) 

        file.write("\n\n")         

        file.write("""
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script async src='https://www.googletagmanager.com/gtag/js?id=UA-138371535-2'></script>
        <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());

        gtag('config', 'UA-138371535-2');
        </script>
        """) 

        file.close() 

        r = git.Repo(repo_dir)
        r.index.add([file_name])
        r.index.commit("Last Updated - {0}".format(india_now))
        r.remotes.origin.push()
        print("Last Updated - {0}".format(india_now.strftime("%H:%M | %d-%m-%Y")))
        time.sleep(120)
    except Exception as e:
        print(e)
        time.sleep(5)
    


