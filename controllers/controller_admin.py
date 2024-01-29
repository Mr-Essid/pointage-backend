import datetime
from datetime import timedelta
from typing import Annotated

from auth_indicator import oauth2_scheme
from services.services_hash import sha256_hash
from services.services_jwt import create_access_token, decodeAccessToken
from services.services_employer import (get_employer_by_id, get_employer_by_UID, get_all_employers,
                                        getEmployerByEmail,
                                        add_employer, update_employer, delete_employer)
from BaseModels import EmployerBaseModel, EmployerUpdate, EmployerResponse, Token, Details
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

admin_router = APIRouter(prefix="/admins")


@admin_router.post("/login", response_model=Token)
def login_c(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="request not permitted"
    )
    admin_ = getEmployerByEmail(form_data.username)

    print(admin_)
    if not admin_.isadmin:
        raise unauthorized_exception

    if admin_ is None:
        raise unauthorized_exception

    if sha256_hash(form_data.password) != admin_.password:
        raise unauthorized_exception

    time_refresh_token = timedelta(days=1)

    token_ = create_access_token({"username": form_data.username})
    type_ = "bearer"
    exp_ = datetime.datetime.utcnow() + time_refresh_token
    return Token(access_token=token_, token_type=type_, exp=exp_)


@admin_router.post("/signup", response_model=EmployerResponse)
def signup_c(new_admin: EmployerBaseModel):
    if new_admin.isadmin:
        new_admin.password = sha256_hash(new_admin.password)

    response = add_employer(new_admin)
    if response is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="identifier already exists")

    return response


@admin_router.get("/current", response_model=EmployerResponse)
def get_current_admin_c(token_: Annotated[str, Depends(oauth2_scheme)]):
    username = decodeAccessToken(token_).get('username')
    admin = None
    admin = getEmployerByEmail(username)
    if admin is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="action not permitted")

    return admin


@admin_router.put("/", response_model=EmployerResponse)
def update_admin_c(admin_model_update_c: EmployerUpdate,
                   current_admin_c: Annotated[EmployerResponse, Depends(get_current_admin_c)]):
    admin_model_update_c.id_ = current_admin_c.id_emp

    admin_that_updated = update_employer(admin_model_update_c)

    if admin_that_updated is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Some Things Went Wrong or Identifier Exists")

    return admin_that_updated


@admin_router.delete("/", response_model=Details)
def delete_admin_c(password: Annotated[str, Form()],
                   current_admin: Annotated[EmployerResponse, Depends(get_current_admin_c)]):
    if sha256_hash(password) != current_admin.password:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action Not Permitted")

    delete_employer(current_admin.id_emp)

    return Details(message="Admin Deleted Successfully")
