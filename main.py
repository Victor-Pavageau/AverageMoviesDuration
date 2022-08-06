# All the data come from www.allocine.fr

import requests
from bs4 import BeautifulSoup, SoupStrainer
import re
from datetime import date, timedelta
import matplotlib.pyplot as plt
import statistics
import threading


ListDureesFilms = []
ListAllWednesday = []
ListOfMeanByYear = []
StartDate = 0


def DateOfAllWednesday(year):
    WednesdayList = []
    d = date(year, 1, 1)
    d += timedelta(days = (2 - d.weekday() + 7) % 7)
    while d.year == year:
        WednesdayList.append(d)
        d += timedelta(days = 7)
    return WednesdayList

def AskDate():
    global StartDate
    try:
        startDate = int(input())
        if (1970 <= startDate < date.today().year):
            StartDate = startDate
        else:
            print("An error as occured, please enter a valid date\nThe year must be between 1970 and the last completed year.\n")
            AskDate()
    except:
        print("An error as occured, please enter a valid date\nThe year must be between 1970 and the last completed year.\n")
        AskDate()

def GetListOfYear(StartDate):
    return list(range(StartDate, date.today().year))

def GetListFilms(weekDate):
    url = "https://www.allocine.fr/film/agenda/sem-" + weekDate + "/"
    strainer = SoupStrainer('a', attrs={'class': 'meta-title-link'})
    soup = BeautifulSoup(requests_session.get(url).text, 'html.parser')
    return soup.find_all("a", class_="meta-title-link")

def GetURLOfFilm(film):
    return "https://www.allocine.fr" + re.search('<a class="meta-title-link" href="(.*)">', film).group(1)

def GetInfoOfFilm(film):
    strainer = SoupStrainer('div', attrs={'class': 'meta-body-item meta-body-info'})
    return BeautifulSoup(requests_session.get(film).content, 'lxml', parse_only=strainer)

def GetFilmDurationString(filmInfos):
    return str(filmInfos).split('<span class="spacer">/</span>')[1]

def GetFilmDurationInt(filmDuration):
    FilmHour = int(filmDuration.split('h')[0])
    FilmMinutes = int(filmDuration.split('h')[1].split('min')[0])
    return (FilmHour * 60 + FilmMinutes)

def SaveScatterPlot(ListOfMeanByYear):
    fig = plt.figure(figsize=(10, 10))
    axisYear = GetListOfYear(StartDate)
    axisMinutes = ListOfMeanByYear
    plt.plot(axisYear, axisMinutes, "-bo")
    plt.ylabel('Duration (in minute)', fontsize=16)
    plt.xlabel('Year', fontsize=16)
    plt.title('Scatter plot of the average duration of movies over time', fontsize=18)
    plt.savefig('OutputScatterPlot.png')

def GetListOfDurationByWeek(weekDate):
    ListOfDurationByWeek = []
    ListFilms = GetListFilms(weekDate)
    for i in range(len(ListFilms)):
        InfosFilms = GetInfoOfFilm(GetURLOfFilm(str(ListFilms[i])))
        if(InfosFilms and (len(InfosFilms) > 1)):
            FilmDurationString = str(GetFilmDurationString(InfosFilms))
            if('<' not in FilmDurationString):
                FilmDuration = GetFilmDurationInt(FilmDurationString)
                ListOfDurationByWeek.append(FilmDuration)
    return ListOfDurationByWeek

def AppendMeanByYear(ListAllWednesday):
    ListOfMeanDurationOfFilmsByYear = []
    for j in range(len(ListAllWednesday)):
        ListOfDurationByWeek = GetListOfDurationByWeek(str(ListAllWednesday[j]))
        if(len(ListOfDurationByWeek) != 0):
            ListOfMeanDurationOfFilmsByYear.append(statistics.mean(ListOfDurationByWeek))
    ListOfMeanByYear.append(round(statistics.mean(ListOfMeanDurationOfFilmsByYear), 1))

print("This program will calculate the average duration of movies per year. The data come from allocine.fr")
print("Years before 1970 are not available.\n")


requests_session = requests.Session()

print("From which year do you want to conduct the study?\n")
AskDate()
ListOfYear = GetListOfYear(StartDate)
ThreadList = []

print("The program is running, please wait.\nThe program may take several minutes to run.")

for i in range(len(ListOfYear)):
    ListAllWednesday = DateOfAllWednesday(ListOfYear[i])
    thread = threading.Thread(name="thread " + str(ListOfYear[i]), target=AppendMeanByYear, args=(ListAllWednesday,))
    ThreadList.append(thread)
    thread.start()

for thread in ThreadList:
    thread.join()

SaveScatterPlot(ListOfMeanByYear)

input("The study is finished, the scatter plot has been saved.\nPress any key to exit...")
