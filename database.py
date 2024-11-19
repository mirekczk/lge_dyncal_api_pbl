import datetime
import re
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator, model_validator, Field

svatky = ["2024-04-01", "2024-05-01", "2024-05-08", "2024-07-05",
          "2024-07-06", "2024-09-28", "2024-10-28", "2024-11-17", 
          "2024-12-24", "2024-12-25", "2024-12-26", "2025-01-01",
          "2025-04-18", "2025-04-21", "2025-05-01", "2025-05-08", 
          "2025-07-05", "2025-07-06", "2025-09-28", "2025-10-28", 
          "2025-11-17", "2025-12-24", "2025-12-25", "2025-12-26"]


class AvailableSlot(BaseModel):
    date_start: str = Field(
        pattern=r"^(202)\d{1}(\-)(0[1-9]|1[0,1,2])(\-)(0[1-9]|[12][0-9]|3[01])$", description="Date format YYYY-MM-DD")
    date_stop: str = Field(
        pattern=r"^(202)\d{1}(\-)(0[1-9]|1[0,1,2])(\-)(0[1-9]|[12][0-9]|3[01])$", description="Date format YYYY-MM-DD")
    time_slots: str = Field(pattern=r"^(08-12)|(12-16)|(08-16)$",
                            description="Timeslot format HH-HH. Only 08-12 and 12-16 and 08-16 are allowed.")
    customer_zipcode: str

    @field_validator('customer_zipcode')
    def validate_zipcode(cls, customer_zipcode: str):
        if re.match("^[1-7]\\d{4}$|^([1-7]\\d{2} \\d{2})$", customer_zipcode):
            pass
        else:
            raise HTTPException(
                422, "ZIP code format has to be five digits. For example: 60200 or 602 00")
        return customer_zipcode

    @model_validator(mode="after")  # type: ignore
    def validate_date(cls, values: "AvailableSlot"):
        try:
            start_date = datetime.date(int(values.date_start.split("-")[0]), int(
                values.date_start.split("-")[1]), int(values.date_start.split("-")[2]))
            end_date = datetime.date(int(values.date_stop.split("-")[0]), int(
                values.date_stop.split("-")[1]), int(values.date_stop.split("-")[2]))
            if end_date < start_date or start_date < datetime.date.today():
                raise HTTPException(422, "Bad date. Use actual and in format YYYY-MM-DD.")
        except ValueError:
            raise HTTPException(422, "Bad date. Use actual and in format YYYY-MM-DD.")
        except KeyError:
            raise HTTPException(422, "Bad date. Use actual and in format YYYY-MM-DD.")
        return values

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "date_start": "2024-05-15",
                    "date_stop": "2024-05-19",
                    "time_slots": "08-16",
                    "customer_zipcode": "602 00"
                }
            ]
        }
    }


class DeliverySlot(BaseModel):
    slot_date: str = Field(
        pattern=r"^(202)\d{1}(\-)(0[1-9]|1[0,1,2])(\-)(0[1-9]|[12][0-9]|3[01])$", description="Date format YYYY-MM-DD")
    slot_time: str = Field(
        description="Timeslot in format HH-HH. For Delivery and instalation => 08-12 or 12-16. For only delivery => 08-16.")
    customer_zipcode: str = Field(description="ZIP code. For example: 60200 or 602 00. CZ ZIPcodes 100 00 - 800 00")
    document_no: str = Field(default="LGEPL_Number1_Number2_Number3",
                             description="Interface Key Value. (Subsidiary_Number1_Number2_Number3)")
    quantity: str | None = "1"
    partner: str | None = "LGE_automatic"

    @field_validator('customer_zipcode')
    def validate_zipcode(cls, customer_zipcode: str):
        if re.match("^\\d{5}$|^(\\d{3} \\d{2})$", customer_zipcode):
            pass
        else:
            raise HTTPException(
                422, "ZIP code format has to be five digits. For example: 60200 or 602 00")
        return customer_zipcode

    @field_validator('quantity')
    def validate_quantity(cls, quantity: str):
        if re.match("^[1-9][0-9]*$", quantity):
            pass
        else:
            raise HTTPException(
                422, "Quantity has to be positive number.")
        return quantity

    @field_validator('slot_time')
    def validate_time_slot(cls, time_slot: str):
        if re.match("^(08-12)|(12-16)|(08-16)$", time_slot):
            pass
        else:
            raise HTTPException(
                422, "Bad timeslot. Timeslot in format HH-HH. For Delivery and instalation => 08-12 or 12-16. For only delivery => 08-16.")
        return time_slot

    @model_validator(mode="after")  # type: ignore
    def validate_date(cls, values: "DeliverySlot"):
        try:
            slot_date = datetime.date(int(values.slot_date.split("-")[0]), int(
                values.slot_date.split("-")[1]), int(values.slot_date.split("-")[2]))
            if slot_date < datetime.date.today():
                raise HTTPException(
                    422, "Bad date. Use actual and in format YYYY-MM-DD.")
        except ValueError:
            raise HTTPException(
                422, "Bad date. Use actual and in format YYYY-MM-DD.")
        except KeyError:
            raise HTTPException(
                422, "Bad date. Use actual and in format YYYY-MM-DD.")
        return values

    def get_branch_id(self):
        if self.customer_zipcode != None:
            zipcode = self.customer_zipcode.replace(' ', '')
            zipcode = int(zipcode)
            if (10000 <= zipcode <= 29999) or (37000 <= zipcode <= 49999) or (58000 <= zipcode <= 58999):
                result = "PRA"
            elif (56800 <= zipcode <= 57999) or (59000 <= zipcode <= 69999) or (75000 <= zipcode <= 75130) or (75136 <= zipcode <= 75299) or (76000 <= zipcode <= 79099) or (79600 <= zipcode <= 79999):
                result = "BRN"
            elif (70000 <= zipcode <= 74999) or (75131 <= zipcode <= 75135) or (75300 <= zipcode <= 75999) or (79100 <= zipcode <= 79599):
                result = "OST"
            elif (30000 <= zipcode <= 36999):
                result = "PLZ"
            elif (50000 <= zipcode <= 56799):
                result = "HKR"
            else:
                result = "XXX"
        else:
            result = "XXX"
        return result

  
    model_config = {
        "json_schema_extra": {
            "examples": [
                {   "slot_date": "2024-12-18",
                    "slot_time": "12-16",
                    "document_no": "LGEXX_Number1_Number2_Number3",
                    "customer_zipcode": "691 21",
                    "quantity": "1"
                 }
            ]
        }
    }


class Login(BaseModel):
    username: str
    password: str

    @model_validator(mode="after")  # type: ignore
    def is_auth(cls, login: "Login"):
        if (login.username == os.getenv('login_test') and login.password == os.getenv('password_test')) or (login.username == os.getenv('login_prod') and login.password == os.getenv('password_prod')):
            return login
        else:
            raise HTTPException(
                401, "Unauthorized. Wrong password or username.")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "lg.wsd",
                    "password": "******************"
                }
            ]
        }
    }


class GetAvailableSlots(BaseModel):
    login: Login
    get_available_slots: AvailableSlot

    def get_branch_id(self):
        if self.get_available_slots.customer_zipcode != None:
            zipcode = self.get_available_slots.customer_zipcode.replace(
                ' ', '')
            zipcode = int(zipcode)
            if (10000 <= zipcode <= 29999) or (37000 <= zipcode <= 49999) or (58000 <= zipcode <= 58999):
                result = "PRA"
            elif (56800 <= zipcode <= 57999) or (59000 <= zipcode <= 69999) or (75000 <= zipcode <= 75130) or (75136 <= zipcode <= 75299) or (76000 <= zipcode <= 79099) or (79600 <= zipcode <= 79999):
                result = "BRN"
            elif (70000 <= zipcode <= 74999) or (75131 <= zipcode <= 75135) or (75300 <= zipcode <= 75999) or (79100 <= zipcode <= 79599):
                result = "OST"
            elif (30000 <= zipcode <= 36999):
                result = "PLZ"
            elif (50000 <= zipcode <= 56799):
                result = "HKR"
            else:
                result = "XXX"
        else:
            result = "XXX"
        return result


class ReserveDeliverySlot(BaseModel):
    login: Login
    reserve_slot: DeliverySlot

class UpdateDocumentNumber(BaseModel):
    update_document_no: str = Field(description="Interface Key Value. (Subsidiary_Number1_Number2_Number3)")
