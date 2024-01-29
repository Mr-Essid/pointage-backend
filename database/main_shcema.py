import datetime
import time
from typing import Type

from sqlalchemy import Column, String, Boolean, Integer, DATE, CHAR, Cast, Date, cast, case, true, select, Row, \
    Sequence, Text, func
from sqlalchemy.orm import relationship, Session
from sqlalchemy.exc import IntegrityError

from BaseModels import EmployerBaseModel, HistoryBM, EmployerUpdate, Details, EmployerResponse, HistoryResponse, \
    HistoryResponseWithName, CountMonth
from database.main_database import base, engine
from sqlalchemy import ForeignKey


def getAllEmployers_():
    with Session(engine) as session:
        return session.query(User).all()


class User(base):
    __tablename__ = 'users'
    name = Column(String(30), nullable=False)
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(20), nullable=False, unique=True)
    gender = Column(CHAR)
    email = Column(String(100), nullable=False, unique=True)
    isadmin = Column(Boolean)
    password = Column(Text, nullable=True)
    mobile = Column(String(8))
    history = relationship("History", back_populates="user")

    @classmethod
    def convertFromUserToBaseModel(cls, user):
        return EmployerResponse(
            name=user.name,
            gender=user.gender,
            email=user.email,
            mobile=user.mobile,
            uid=user.uid,
            id_emp=user.id,
            isadmin=user.isadmin,
            password=user.password
        )

    def __init__(self, mainStructure: EmployerBaseModel):
        self.name = mainStructure.name
        self.email = mainStructure.email
        self.isadmin = mainStructure.isadmin
        self.uid = mainStructure.uid
        self.mobile = mainStructure.mobile
        self.gender = mainStructure.gender
        self.password = mainStructure.password

    def __str__(self):
        return f"Name {self.name}, UID {self.uid}"

    def __repr__(self):
        return f"Name {self.name}, UID {self.uid}"

    @classmethod
    def addEmployer(cls, new_employer):
        newUser = User(new_employer)

        isError = False
        with Session(engine) as session:
            session.add(newUser)
            try:
                session.commit()
            except IntegrityError as e:
                session.rollback()
                isError = True

        if isError:
            return None

        return cls.convertFromUserToBaseModel(cls._getUserByUID(new_employer.uid))

    @classmethod
    def _getUserByUID(cls, uid: str):

        with Session(engine) as session:
            return session.query(cls).filter(cls.uid == uid).first()

    @classmethod
    def getEmployerByUID(cls, uid: str):
        emp = cls._getUserByUID(uid)
        if emp is None:
            return
        return cls.convertFromUserToBaseModel(emp)

    @classmethod
    def getById(cls, id_: int):
        with Session(engine) as session:
            employer = session.query(cls).filter(cls.id == id_).first()
            if employer is None:
                return None
            return cls.convertFromUserToBaseModel(employer)

    @classmethod
    def _getById(cls, id_: int):
        with Session(engine) as session:
            return session.query(cls).filter(cls.id == id_).first()

    @classmethod
    def getByEmail(cls, email: str):
        with Session(engine) as session:
            user = session.query(cls).filter(cls.email == email).first()

            if user is None:
                return None
            return cls.convertFromUserToBaseModel(user)

    # email, uid, tel

    @classmethod
    def getAllEmployers(cls):

        with Session(engine) as session:
            list_ = session.query(cls).all()

            new_list = list(map(cls.convertFromUserToBaseModel, list_))

            return new_list

    @classmethod
    def updateEmp(cls, emp: EmployerUpdate):
        if emp.email is None and emp.mobile is None and emp.uid is None:
            return -1

        isError = False
        with Session(engine) as session:
            emp_ = session.query(cls).filter(cls.id == emp.id_).first()
            if emp_ is None:
                return -2

            if emp.email:
                emp_.email = emp.email
            if emp.mobile:
                emp_.mobile = emp.mobile

            if emp.uid:
                emp_.uid = emp.uid

            try:
                session.commit()

            except IntegrityError as e:
                session.rollback()
                isError = True

            if isError:
                return -3

            return cls.convertFromUserToBaseModel(cls._getById(emp.id_))

    @classmethod
    def deleteUser(cls, id_: int):
        with Session(engine) as session:
            emp = session.query(cls).filter(cls.id == id_).first()
            if emp is None:
                return None

            session.delete(emp)
            session.commit()

        return Details(message="Employer Deleted")


class History(base):
    __tablename__ = 'history'
    statut = Column(String(10), nullable=False)
    date = Column(DATE, nullable=False)
    id_history = Column(Integer, primary_key=True, autoincrement=True)
    id_employer = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="history")

    def __init__(self, hisbm: HistoryBM):
        self.date = hisbm.date
        self.statut = hisbm.statut
        self.id_employer = hisbm.id_emp_hist

    @staticmethod
    def convertFromHistory(history):
        history_res = HistoryResponse(
            id_hist=history.id_history,
            id_emp_hist=history.id_employer,
            statut=history.statut,
            date=history.date
        )

        return history_res

    @staticmethod
    def convertFromHistoryWithName(history: Row[tuple[Type]]):
        history_res = HistoryResponseWithName(
            id_history=history[1],
            statut=history[3],
            date_=history[2],
            name_employer=history[0]
        )

        return history_res

    @classmethod
    def addHistory(cls, id_emp):
        statet = "retard" if time.localtime().tm_hour > 9 else "present"
        isError = False
        with Session(engine) as session:
            session.add(cls(HistoryBM(date=datetime.date.today(), statut=statet, id_emp_hist=id_emp)))
            try:
                session.commit()
            except IntegrityError as e:
                print(e)
                isError = True

            if isError:
                return None

        return Details(message="history added successfully")

    @classmethod
    def getHistory(cls):
        history_res: Row[tuple[str, int, datetime.date, str]] | None = None

        statement = (select(User.name, cls.id_history, cls.date, cls.statut).select_from(cls).
                     join(User,
                          User.id == cls.id_employer).order_by(cls.date.desc()))

        with Session(engine) as session:
            history_res = session.execute(statement).all()

        data = list(map(cls.convertFromHistoryWithName, history_res))

        return data

    @classmethod
    def getHistoryOfEmployer(cls, id_emp):
        history_res: list[Type[cls]] | None = None
        with Session(engine) as session:
            history_res = session.query(History).filter(cls.id_employer == id_emp).order_by(
                cls.date.desc()).all()

        response_history_list = list(map(cls.convertFromHistory, history_res))

        return response_history_list

    @classmethod
    def getHistoryOfDate(cls, date_: datetime.date):

        if type(date_) is not datetime.date:
            return

        history_res: Row[tuple[str, int, datetime.date, str]] | None = None

        statement = (select(User.name, cls.id_history, cls.date, cls.statut).select_from(cls).
                     join(User,
                          User.id == cls.id_employer).where(cls.date == date_).order_by(cls.date.desc()))

        with Session(engine) as session:
            history_res = session.execute(statement).all()

        data = list(map(cls.convertFromHistoryWithName, history_res))

        return data

    @classmethod
    def pointByUID(cls, uid: str):
        statet = "retard" if time.localtime().tm_hour > 9 else "present"
        isError = False
        print("This Function Called")
        with Session(engine) as session:
            user_id = session.query(User.id).filter(User.uid == uid).first()
            if user_id is None:
                return None
            session.add(cls(HistoryBM(date=datetime.date.today(), statut=statet, id_emp_hist=user_id[0])))
            try:
                session.commit()
            except IntegrityError as e:
                print(e)
                isError = True

            if isError:
                return None

        return Details(message="history added successfully")

    @classmethod
    def getCountByMonthEmployer(cls, id_employer: int):
        with (Session(engine) as session):
            res = session.query(func.extract("month", cls.date), func.count("*")) \
                .filter(cls.id_employer == id_employer).group_by(
                func.extract("month", cls.date)).order_by(
                func.extract("month", func.max(cls.date))).first()
            print(f"This is Result {res}")
            if res is None:
                res = (0, 0)

            return CountMonth(month=res[0], howManyPointed=res[1])

    @classmethod
    def getHistoryByUID(cls, uid: str):

        history_res: list[Type[cls]] | None = None

        with Session(engine) as session:
            id_emp = session.query(User.id).filter(User.uid == uid).first()
            if id_emp is None:
                return
            history_res = session.query(History).filter(cls.id_employer == id_emp[0]).order_by(
                cls.date.desc()).all()

        response_history_list = list(map(cls.convertFromHistory, history_res))

        return response_history_list


if __name__ == '__main__':
    base.metadata.create_all(engine)
    newE = EmployerBaseModel(
        name="Cyrine",
        gender='m',
        email="helflo@go.com",
        isadmin=False,
        uid="201010",
        mobile="975815"
    )
    # User.addEmployer(newE)
    print(History.getCountByMonthEmployer(17))
