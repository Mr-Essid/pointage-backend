import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from services.services_history import add_history, get_history, get_history_of_date, get_history_of_employer_c, \
    howManyInMonth, get_history_by_uid, add_history_by_uid
from auth_indicator import oauth2_scheme
from BaseModels import HistoryResponse, HistoryResponseWithName, Details
from fastapi_mqtt import MQTTConfig, FastMQTT
from env_data import BROKER, PASSWORD_BROKER, USERNAME_BROKER

history_route = APIRouter(prefix="/history")

config = MQTTConfig(
    username=USERNAME_BROKER,
    password=PASSWORD_BROKER,
    host=BROKER,
    port=8883,
    ssl=True
)

mqttApp = FastMQTT(config)


@mqttApp.on_connect()
def connect(client, p, rc, pr):
    print("Connected")


@mqttApp.subscribe("/employer/uuid")
async def message_to_topic(client, topic, payload, qos, properties):
    uuid = payload.decode('utf-8')
    history_of_the_employer = get_history_by_uid(uuid)
    if history_of_the_employer is None:
        print("no employers here")
        return

    if len(history_of_the_employer) > 0:
        if history_of_the_employer[0].date == datetime.date.today():
            mqttApp.publish("/history/uuid", "pointed employer")
            print("user already pointed today")
            return
    add_history_by_uid(uuid)


@history_route.post("/", response_model=Details)
def add_history_c(id_: int, current_admin=Depends(oauth2_scheme)):
    history_of_the_employer = get_history_of_employer_c(id_)

    if len(history_of_the_employer) > 0:
        if history_of_the_employer[0].date == datetime.date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The Employer Is Already Pointed")

    return add_history(id_)


@history_route.post("/uuid/{uuid}", response_model=Details | None)
def add_history_by_uid_c(uuid: str, current_admin=Depends(oauth2_scheme)):
    history_of_the_employer = get_history_by_uid(uuid)
    print(f"history by uid len of root is {history_of_the_employer}")

    if len(history_of_the_employer) > 0:
        if history_of_the_employer[0].date == datetime.date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The Employer Is Already Pointed")

    return add_history_by_uid(uuid)


@history_route.get("/uuid/{uuid}", response_model=list[HistoryResponse])
def get_history_by_uid_c(uuid: str, current_admin=Depends(oauth2_scheme)):
    return get_history_by_uid(uuid)


@history_route.get("/", response_model=list[HistoryResponseWithName])
def get_all_history_c(current_admin=Depends(oauth2_scheme)):
    return get_history()


@history_route.get("/employer/{id_}", response_model=list[HistoryResponse])
def get_history_employer_c(id_: int, current_admin=Depends(oauth2_scheme)):
    return get_history_of_employer_c(id_)


@history_route.get("/date/{date_}", response_model=list[HistoryResponseWithName])
def get_history_date_c(date_: datetime.date, current_admin=Depends(oauth2_scheme)):
    return get_history_of_date(date_)


@history_route.get('/per-month/{id_}')
def get_how_many_in_month(id_: int, current_admin=Depends(oauth2_scheme)):
    return howManyInMonth(id_)
