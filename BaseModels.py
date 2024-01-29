import datetime

from pydantic import BaseModel


class EmployerUpdate(BaseModel):
    id_: int
    email: str | None = None
    mobile: str | None = None
    uid: str | None = None


class EmployerBaseModel(BaseModel):
    """
    :arg name; gender;email;isadmin
    """
    name: str
    gender: str
    email: str
    mobile: str
    isadmin: bool | None = False
    uid: str
    password: str | None = None


class EmployerResponse(EmployerBaseModel):
    id_emp: int


class HistoryBM(BaseModel):
    date: datetime.date
    statut: str
    id_emp_hist: int


class HistoryResponse(HistoryBM):
    """
        id_hist = ,
        id_emp_hist = ,
        statut = ,
        date =
    """
    id_hist: int


class HistoryResponseWithName(BaseModel):
    """
    id_history,
    statut,
    name_employer,
    date_
    """

    id_history: int
    statut: str
    name_employer: str
    date_: datetime.date


class Details(BaseModel):
    message: str


class Token(BaseModel):
    access_token: str
    exp: datetime.datetime
    token_type: str


class CountMonth(BaseModel):
    month: int
    howManyPointed: int
