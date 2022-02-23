import requests
from bs4 import BeautifulSoup, SoupStrainer
import re
from datetime import date, timedelta, datetime
import matplotlib.pyplot as plt
import pylab


ListDureesFilms = []
ListAllWednesday = []
ListOfMeanByYear = []
CurrentYear = date.today().year
requests_session = requests.Session()


def DateOfAllWednesday(year):
    ResultList = []
    d = date(year, 1, 1)
    d += timedelta(days = (2 - d.weekday() + 7) % 7)
    while d.year == year:
        ResultList.append(d)
        d += timedelta(days = 7)
    return ResultList

def AskDate():
    StartDate = int(input("Date de début de l'analyse ?\n"))
    if (DateIsCorrect(StartDate)):
        return StartDate

def DateIsCorrect(startDate):
    if (1970 <= startDate < CurrentYear):
        return True
    else:
        return False

def GetListOfYear(StartDate):
    return list(range(StartDate, CurrentYear))

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

def TraceFigure(ListOfMeanByYear, StartDate):
    fig = plt.figure()
    x = GetListOfYear(StartDate)
    height = ListOfMeanByYear
    width = 0.05
    plt.bar(x, height, width, color='k')
    plt.savefig('Output.png')

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


# Main starts here :

StartDate = AskDate()
ListOfYear = GetListOfYear(StartDate)

for i in range(len(ListOfYear)):
    ListOfMeanDurationOfFilmsByYear = []
    ListAllWednesday = DateOfAllWednesday(ListOfYear[i])
    for j in range(len(ListAllWednesday)):
        ListOfDurationByWeek = GetListOfDurationByWeek(str(ListAllWednesday[j]))
        if(len(ListOfDurationByWeek) == 0):
            ListOfMeanDurationOfFilmsByYear.append(0)
        else:
            ListOfMeanDurationOfFilmsByYear.append((sum(ListOfDurationByWeek) / len(ListOfDurationByWeek)))
    ListOfMeanByYear.append(round((sum(ListOfMeanDurationOfFilmsByYear) / len(ListOfMeanDurationOfFilmsByYear)), 1))

TraceFigure(ListOfMeanByYear, StartDate)
