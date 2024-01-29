from fastapi import APIRouter, Depends, HTTPException, status
from auth_indicator import oauth2_scheme
from services.services_employer import (add_employer, get_all_employers, update_employer, getEmployerByEmail,
                                        get_employer_by_id, get_employer_by_UID, delete_employer)
from BaseModels import EmployerBaseModel, EmployerResponse, EmployerUpdate, Details

employer_route = APIRouter(prefix="/employers")


@employer_route.post("/employer", response_model=EmployerResponse)
def add_employer_c(new_employer: EmployerBaseModel, current_admin=Depends(oauth2_scheme)):
    new_employer.isadmin = False
    new_employer.password = None
    employer_added = add_employer(new_employer)

    if employer_added is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Identifier Exists")

    return employer_added


@employer_route.get("/", response_model=list[EmployerResponse])
def get_employers_c(current_admin=Depends(oauth2_scheme)):
    employers = get_all_employers()
    filtered_data = list(filter(lambda employer: not employer.isadmin, employers))
    return filtered_data


@employer_route.get("/employer", response_model=EmployerResponse)
def get_employer_by_c(email: str | None = None, id_: int | None = None, uid: str | None = None,
                      current_admin=Depends(oauth2_scheme)):
    if email:
        employer = getEmployerByEmail(email)
        if employer is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"There is No Employer With Email {email}")
        if employer.isadmin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action Not Permitted")

        return employer

    if id_:

        employer = get_employer_by_id(id_)
        if employer is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"There is No Employer With id {id_}")
        if employer.isadmin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action Not Permitted")

        return employer

    if uid:
        employer = get_employer_by_UID(uid)

        if employer is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"There is No Employer With UID {uid}")

        if employer.isadmin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action Not Permitted")

        return employer

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No Filed Specified")


@employer_route.put("/employer", response_model=EmployerResponse)
def update_admin_c(employer_to_update: EmployerUpdate, current_admin=Depends(oauth2_scheme)):
    updated_employer = update_employer(employer_to_update)
    if updated_employer == -3:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Identifier Exists There is No Way To Update Right Now")

    if updated_employer == -2:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"There is No Employer With id {employer_to_update.id_}")

    if updated_employer == -1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="There is No Filed Specified")

    return updated_employer


@employer_route.delete("/employer", response_model=Details)
def delete_employer_c(id_: int, current_admin=Depends(oauth2_scheme)):
    details = delete_employer(id_)

    if details is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Employer With id {id_} is Not Exists")

    return details
