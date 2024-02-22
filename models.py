import datetime
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator, model_validator, Field, root_validator, validator

svatky = ["2024-03-29", "2024-04-01", "2024-05-01", "2024-05-08",
          "2024-07-05", "2024-07-06", "2024-09-28", "2024-10-28",
          "2024-11-17", "2024-12-24", "2024-12-25", "2024-12-26",
          "2025-01-01", "2025-04-18", "2025-04-21", "2025-05-01",
          "2025-05-08", "2025-07-05", "2025-07-06", "2025-09-28",
          "2025-10-28", "2025-11-17", "2025-12-24", "2025-12-25", "2025-12-26"]

class AvailableSlots(BaseModel):
    date_start: str = Field(
        pattern=r"^(202)\d{1}(\-)(0[1-9]|1[0,1,2])(\-)(0[1-9]|[12][0-9]|3[01])$", description="Date format YYYY-MM-DD")
    date_stop: str = Field(
        pattern=r"^(202)\d{1}(\-)(0[1-9]|1[0,1,2])(\-)(0[1-9]|[12][0-9]|3[01])$", description="Date format YYYY-MM-DD")
    time_slots: str = Field(pattern=r"^(08-12)|(12-16)|(08-16)$", description="Timeslot format HH-HH. Only 08-12 and 12-16 is allowed.")

    @model_validator(mode="after")  # type: ignore
    def validate_date(cls, values: "AvailableSlots"):
        try:
            start_date = datetime.date(int(values.date_start.split("-")[0]), int(
                values.date_start.split("-")[1]), int(values.date_start.split("-")[2]))
            end_date = datetime.date(int(values.date_stop.split("-")[0]), int(
                values.date_stop.split("-")[1]), int(values.date_stop.split("-")[2]))
            if end_date < start_date or start_date < datetime.date.today():
                raise HTTPException(
                    422, "Bad date. Use actual and in format YYYY-MM-DD.")
        except ValueError:
            raise HTTPException(
                422, "Bad date. Use actual and in format YYYY-MM-DD.")
        except KeyError:
            raise HTTPException(
                422, "Bad date. Use actual and in format YYYY-MM-DD.")
        return values

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "date_start": "2024-03-05",
                    "date_stop": "2024-03-19",
                    "time_slots": "08-16"
                }
            ]
        }
    }


class DeliverySlot(BaseModel):
    slot_date: str = Field(
        pattern=r"^(202)\d{1}(\-)(0[1-9]|1[0,1,2])(\-)(0[1-9]|[12][0-9]|3[01])$", description="Date format YYYY-MM-DD")
    slot_time: str = Field(
        description="Timeslot format HH-HH. Only 08-12 and 12-16 is allowed.")
    customer_cap: str = Field(
        pattern=r"^(\d{5})|(\d{3}\s\d{2})$", description="Customer zip code.")
    quantity: int
    product_id: int
    product_place_id: int

    @model_validator(mode="after")  # type: ignore
    def validate_date(cls, values: "DeliverySlot"):
        try:
            slot_date = datetime.date(int(values.slot_date.split("-")[0]), int(
                values.slot_date.split("-")[1]), int(values.slot_date.split("-")[2]))
            if slot_date < datetime.date.today():
                raise HTTPException(
                    422, "Bad date. Use actual and in format YYYY-MM-DD.")
        except ValueError:
            raise HTTPException(422, "Bad date. Use actual and in format YYYY-MM-DD.")
        except KeyError:
            raise HTTPException(
                422, "Bad date. Use actual and in format YYYY-MM-DD.")
        return values
    
    @field_validator('slot_time')
    def validate_time_slot(cls, time_slot: str):
        if re.match("^(08-12)|(12-16)$", time_slot):
            pass
        else:
            raise HTTPException(
                422, "Bad timeslot. Timeslot in format HH-HH. Only 08-12 or 12-16 is allowed.")
        return time_slot

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "slot_date": "2024-03-05",
                    "slot_time": "12-16",
                    "customer_cap": "69121",
                    "quantity": 1,
                    "product_id": 12,
                    "product_place_id": 11
                }
            ]
        }
    }


class Login(BaseModel):
    username: str
    password: str

    @model_validator(mode="after")  # type: ignore
    def is_auth(cls, login: "Login"):
        if login.username == "login" and login.password == "password":
            return login
        else:
            raise HTTPException(401, "Unauthorized. Wrong password or username.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "lg.wsd",
                    "password": "ec**************"
                }
            ]
        }
    }


class GetAvailableSlots(BaseModel):
    login: Login
    get_available_slots: AvailableSlots

    @classmethod
    def is_available_timeslot(cls, time: str) -> int:
        timeFrom = int(time.split("-")[0])
        timeTo = int(time.split("-")[1])
        if timeTo >= timeFrom:
            if timeFrom >= 7 and timeFrom < 12:
                return 1
            elif timeFrom >= 12 and timeFrom < 16:
                return 2
            else:
                return 0
        else:
            return 0

    @classmethod
    def is_bday(cls, datum, holidays=svatky) -> bool:
        res = True
        if datetime.datetime.weekday(datum) == 5:
            # sobota, D+2 a pote zavolam rekurzivne, kdyby i den potom byl svatek/vikend
            res = False
        elif datetime.datetime.weekday(datum) == 6:
            # nedele, D+1
            res = False
        elif datum.strftime("%Y-%m-%d") in holidays:
            # svatek, D+1
            res = False
        return res


class ReserveDeliverySlot(BaseModel):
    login: Login
    reserve_slot: DeliverySlot
