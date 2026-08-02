from PySide6.QtCore import QLocale, QDateTime


def updateDayWeekHour():
    now = QDateTime.currentDateTime()
    localeBR = QLocale(QLocale.Language.Portuguese, QLocale.Country.Brazil)
    text = localeBR.toString(now, "dddd - HH:mm")
    return text[0].upper() + text[1:]