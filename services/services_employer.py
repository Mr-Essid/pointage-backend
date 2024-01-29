from database.main_shcema import User
from BaseModels import EmployerBaseModel, EmployerResponse, EmployerUpdate, Details


def add_employer(new_employer: EmployerBaseModel) -> EmployerResponse | None:
    return User.addEmployer(new_employer)


def get_all_employers() -> list[EmployerResponse]:
    return User.getAllEmployers()


def get_employer_by_id(id_: int) -> EmployerResponse | None:
    return User.getById(id_)


def get_employer_by_UID(uid: str) -> EmployerResponse | None:
    return User.getEmployerByUID(uid)


def getEmployerByEmail(email: str) -> EmployerResponse | None:
    return User.getByEmail(email)


def update_employer(employer_to_update: EmployerUpdate) -> EmployerResponse | int:
    return User.updateEmp(employer_to_update)


def delete_employer(id_: int) -> Details | None:
    return User.deleteUser(id_)
