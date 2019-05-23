import requests
import time
from bs4 import BeautifulSoup
import csv
from pytablewriter import HtmlTableWriter
from pytablewriter.style import Style
import git, os
import time

from datetime import datetime
import pytz
tz = pytz.timezone('Asia/Kolkata')

repo_dir = "/Users/manjunath/Developer/Web Dev/githubpages"
file_name = os.path.join(repo_dir, 'index.html')

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

    _resultDict = []

    for tr in votes_table_tr:
        if tr != "":
            try:
                _votes = None
                tds = tr.find_all('td')
                if candidate is None:
                    if tds[2].text in party:
                        # print("Candidate: {0} Party: {1}  Votes: {2}".format(tds[0].text, tds[1].text, tds[2].text))
                        row = {"candidate": tds[1].text, "party": tds[2].text, "votes": int(tds[5].text)}
                        print(row)
                        _resultDict.append(row)

                else:
                    if tds[1].text == candidate:
                        # print("Candidate: {0} Party: {1}  Votes: {2}".format(tds[0].text, tds[1].text, tds[2].text))
                        row = {"candidate": tds[1].text, "party": tds[2].text, "votes": int(tds[5].text)}
                        _resultDict.append(row)

            except Exception as ae:
                _resultDict = []
                pass

    if len(_resultDict) == 0:
        return False
    else:
        return _resultDict


while True:

    STATE = "karnataka"
    PARTY = ["BJP", "UPJP", "INC", "JD(S)"]

    _constituencies = readStateInfo("states/{0}.csv".format(STATE))

    _totalVotes = 0
    _totalConstituencyCollected = 0
    _resultList = []

    for _constituency in _constituencies:
        _results = getResultConstituency(constituency=_constituency["constituencyNumber"], party=PARTY)
        _totalConstituencyCollected += 1
        if _results:
            for result in _results:
                _totalVotes =  _totalVotes + result["votes"]
                _resultList.append([_constituency["constituencyName"], result["party"], result["candidate"], result["votes"]])
                print("Constituency: {0} \t\t\t Candidate: {1} \t\t\t Votes: {2} \n".format(_constituency["constituencyName"], result["candidate"], result["votes"]))
        else:
            print("No results")
            
    print("\n\n TOTAL VOTES - {0:,} \n Collected from {1}/{2} Constituencies".format(_totalVotes, _totalConstituencyCollected, len(_constituencies)))

    _resultList.sort(key = lambda x: x[2], reverse=True) 
    writer = HtmlTableWriter()
    writer.headers = ["Constituency", "Party", "Candidate", "Votes"]
    writer.value_matrix = _resultList
    writer.table_name = "results_table"
    writer.styles = [
        Style(align="center"),
        Style(align="center"),
        Style(font_weight="bold", align="right", thousand_separator=","),
    ]

    writer.write_table()

    try:
        india_now = datetime.now(tz)
        file = open("index.html","w") 
        file.write("---\nlayout: default\n---\n")
        file.write("<body>")
        file.write("<h1> 2019 Loksabha Election Result for {0} </h1><br>".format(STATE))
        file.write("<hr>")
        file.write("""
        <h2> TOTAL VOTES - {0:,} </h2><br>
        <h3> (Collected from {1}/{2} Constituencies) </h2><br><br>
        """.format(_totalVotes, _totalConstituencyCollected, len(_constituencies))) 
        file.write("<hr>")
        file.write("""
        <label for="party"> Select Party</label>
        <select id="party" onChange="filterForParty(this.value);">
            <option value="UPJP">UPJP</option>
            <option value="BJP">BJP</option>
            <option value="INC">INC</option>
            <option value="JD(S)">JD(S)</option>
        </select>
        """)
        
        file.write("""<h2>Results for</h2><label id="partyName"><h2>Party</h2></label><br><br>""")

        file.write(writer.dumps()) 

        file.write("<hr>")
        file.write("### Last Updated - {0} \n\n\n".format(india_now.strftime("%H:%M | %d-%m-%Y"))) 
        file.write("</body>")
        file.write("""
        <script>
            function filterForParty(party) {
                document.getElementById("partyName").innerText = party;
                var found;
                table = document.getElementById("results_table");
                let tr = table.getElementsByTagName("tr");
                for (let i = 0; i < tr.length; i++) {
                    let td = tr[i].getElementsByTagName("td");
                    if ((td[1] != undefined) &&  (td[1].innerHTML.toUpperCase().indexOf(party) > -1)) {
                        found = true;
                    }

                    if (found) {
                        tr[i].style.display = "";
                        found = false;
                    } else {
                        tr[i].style.display = "none";
                    }
                }
            }
            filterForParty(document.getElementById("party").value)
        </script>
        """)
        
        # file.write("""
        # <!-- Global site tag (gtag.js) - Google Analytics -->
        # <script async src='https://www.googletagmanager.com/gtag/js?id=UA-138371535-2'></script>
        # <script>
        # window.dataLayer = window.dataLayer || [];
        # function gtag(){dataLayer.push(arguments);}
        # gtag('js', new Date());

        # gtag('config', 'UA-138371535-2');
        # </script>
        # """) 

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
    


