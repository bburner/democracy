import requests
from bs4 import BeautifulSoup
import re
import csv
import os

print("This scraper extracts and parses data from a range of bills.")
startnumb = int(input("Enter a US House of Representatives bill you would like to start with: "))
stopnumb = int(input("Enter the bill number you would like to end on: "))

with open('HouseData.csv', 'a', newline='') as csvfile:
    fieldnames = ['Title of Bill', 'Bill Number', 'Bill Sponsor','Party','State','District','Date Introduced','Status','Status Date','Topic','Actions']
    writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
    writer.writeheader()

    for i in range(startnumb,stopnumb):
        billurl = "https://www.congress.gov/bill/114th-congress/house-bill/" + str(i)
        billtxt = billurl + '/text?format=txt'

        page = requests.get(billurl)
        pagetxt = requests.get(billtxt)
        if page.status_code == 200: #Checks to make sure the page (i.e. bill) exists
            soup = BeautifulSoup(page.content, 'html.parser')

    #Parses the Title
            try:
                titlehtml = soup.find_all('h1')[0].get_text()
            except IndexError:
                billnumb = i
                billname = 'none'
                print("\nTitle of Bill: " + str(billname))
                print("Bill number: " + str(i))
            else:
                title = re.search(r'\-\s(.*?)[1][1][4]', titlehtml)
                billname = str(title.group(1))
                billnumber = str(i)
                print("\nTitle of Bill: " + billname)
                print("Bill number: " + billnumber)

    #Parses information on the sponsor of the bill
            try:
                rep = soup.find_all('td')[0].get_text() #Extracts the representative text from a table on congress.gov
            except IndexError:
                repname = 'none'
                party = 'none'
                state = 'none'
                district = 'none'
                date = 'none'
                print("Bill number is reserved")
            else:
                name = re.search(r'[\s](.*)\s\[(.*)\](.*)\)', rep) #Regex to parse the text into name party and date
                repname = str(name.group(1))
                print("Bill Sponsor: " + repname)
                psd = name.group(2)
                if psd[0] == 'D':
                    party = 'Democrat'
                elif psd[0] == 'R':
                    party = 'Republican'
                else:
                    party = str(psd[0]) #Exception for 3rd party Representatives
                state = str(psd[2:4])
                district = str(psd[5:])
                print("Party: " + party) 
                print("State: " + state)
                print("District: " + district)

                dater = re.search(r'(\d\d\/.*)\)', rep)
                datep = str(dater.group(1))
                print("Date Introduced: " + datep)

    #Parsing Info for the bill status
            try:
                statusr = soup.find_all('td')[2].get_text()
            except IndexError:
                statusp = 'none'
            else:
                statusp = re.search(r'\d\d\s(.*?)\s\(', statusr)
                try:
                    statusfinal = str(statusp.group(1))
                    statusdate = re.search(r'(\d\d\/\d\d/\d\d\d\d)', statusr)
                    datefinal = str(statusdate.group(1))
                except AttributeError:
                    statusfinal = 'none'
                    statusdate = 'none'
                    datefinal = 'none'
                else:
                    print("Status: " + statusfinal)
                    print("Status Date: " + datefinal)

    #Parsing info for the topic (derived from the originating committee)
            try:
                committee = soup.find_all('td')[1].get_text()
            except IndexError:
                committee = 'none'
            else:
                #Python dictonary allows the custom assignment of topics based on committee information
                committeedic = {'griculture':'Economy', 'ppropriations':'Economy','rmed':'National Security','udget':'Economy','ducation':'Social Issues','nergy':'Economy','thics':'Government Reform','inancial':'Economy','oreign':'Foreign Relations','omeland':'National Security','dministration':'Government Reform','udiciary':'Law and the Judicial System','esources':'Economy','versight':'Government Reform','ules':'Government Reform','cience':'Science and Technology','usiness':'Economy','ransportation':'Economy','eterans':'Social Issues','eans':'Economy','ntelligence':'National Security','conomic':'Economy','axation':'Economy'}
                topiclist = []
                for key, value in committeedic.items():
                    restr = r'.*' + re.escape(key) + '.*'
                    if re.match(restr, committee) != None:
                        topiclist.append(value)
                        print("Topic: " + value)
                    else:
                        continue

    #Parsing info for the votes / action record
            try:
                votes = soup.find_all('td')[3].get_text()
            except IndexError:
                votes = 'none'
            else:
                print("Actions: " + str(votes) + "\n")

    #Parsing info for the bill text
            if pagetxt.status_code == 200: 
                souptxt = BeautifulSoup(pagetxt.content, 'html.parser')
                try:
                    text = souptxt.find(id='billTextContainer').get_text()
                except AttributeError:
                    text = 'none'
                    print("Text: none")
                else: #Saves the bill text as a .txt file
                    filename = str(i) + '.txt'
                    filepath = os.path.join('./billtext/', filename)
                    if not os.path.exists('./billtext/'):
                        os.makedirs('./billtext/')
                    billtxt = open(filepath, 'w')
                    billtxt.write(text)
                    billtxt.close()

            else:
                text = 'none'

    # Exception printed if the page is not found
        else:
            print("error on " + billurl + "House bill was not found")

#Writing data to csv file

        
        writer.writerow({'Title of Bill':billname,'Bill Number':billnumber, 'Bill Sponsor':repname, 'Party':party, 'State':state,'District':district,'Date Introduced':datep, 'Status':statusfinal, 'Status Date':datefinal,'Topic':topiclist, 'Actions':votes})
csvfile.close()

input("Press any key to exit")
