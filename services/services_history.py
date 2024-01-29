import datetime

from database.main_shcema import History
from BaseModels import HistoryResponseWithName, HistoryResponse, Details, CountMonth


def add_history(id_: int) -> Details | None:
    return History.addHistory(id_)


def add_history_by_uid(uid: str) -> Details | None:
    return History.pointByUID(uid)


def get_history() -> list[HistoryResponseWithName]:
    return History.getHistory()


def get_history_of_employer_c(id_employer: int) -> list[HistoryResponse]:
    return History.getHistoryOfEmployer(id_employer)


def get_history_of_date(date_: datetime.date) -> list[HistoryResponseWithName]:
    return History.getHistoryOfDate(date_)


def get_history_by_uid(uid: str):
    return History.getHistoryByUID(uid)


def howManyInMonth(id_: int) -> CountMonth | None:
    return History.getCountByMonthEmployer(id_)
