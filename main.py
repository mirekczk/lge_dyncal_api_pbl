import datetime
from fastapi import FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uuid
from fastapi_utilities import repeat_every, repeat_at
import uvicorn
from uvicorn.config import LOGGING_CONFIG
from models import GetAvailableSlots, ReserveDeliverySlot
import database

app = FastAPI(debug=False, title="API for LGE Dynamic Calendar",
              description="API for LGE Dynamic Calendar, handling timeslots API",
              version="1.0.1")

templates = Jinja2Templates(directory="templates")


@app.get("/", include_in_schema=False)
async def index():
    response = {
        "detail": "alive",
        "documentation": "localhost/docs"
    }
    return response

#311111
#51111
#4111


@app.get("/show_available_slots", include_in_schema=False)
def show_slots(request: Request):
    dnesni = datetime.date.today().strftime("%Y-%m-%d")
    future_date =  datetime.date.today() + datetime.timedelta(days = 30)
    dates=database.select_as(str(dnesni), future_date)
    return templates.TemplateResponse("edit_table.html", {
        "request": request,
        "dates": dates
    })


@app.post("/save_values", include_in_schema=False, response_class=RedirectResponse)
def edit_slots(request: Request, date: list = Form(...), dopol:list=Form(...), odpol: list=Form(...)):
    dnesni = datetime.date.today().strftime("%Y-%m-%d")
    future_date =  datetime.date.today() + datetime.timedelta(days = 30)
    dates = database.select_as(str(dnesni), future_date)
    values = zip(date, dopol, odpol)
    #print(values)
    database.edit_slots(values)
    return RedirectResponse(url="localhost:5052/show_available_slots",status_code=status.HTTP_303_SEE_OTHER)

@app.post("/delivery_timeslots")
async def get_timeslots(data: GetAvailableSlots):
    start_date = datetime.date(int(data.get_available_slots.date_start.split("-")[0]), int(
        data.get_available_slots.date_start.split("-")[1]), int(data.get_available_slots.date_start.split("-")[2]))
    end_date = datetime.date(int(data.get_available_slots.date_stop.split("-")[0]), int(
        data.get_available_slots.date_stop.split("-")[1]), int(data.get_available_slots.date_stop.split("-")[2]))
    time_slot = data.get_available_slots.time_slots
    if time_slot == '08-12':
        result = database.select_availeble_slots_dopol(start_date,end_date)
    elif time_slot == '12-16':
        result = database.select_availeble_slots_odpol(start_date,end_date)
    elif time_slot == '08-16':
        result= database.select_availeble_slots_vse(start_date,end_date)
    else:
        result=[]
    return result
    
    
@app.post("/reserve_timeslot", include_in_schema=True)
async def reserve_timeslot(data: ReserveDeliverySlot):
    slot = data.reserve_slot
    slot_id = uuid.uuid4().hex
    values =(slot_id, slot.slot_date, slot.slot_time,slot.customer_cap,slot.quantity,slot.product_id)
    counts = database.get_avlslot_counts(values[1])
    if ((values[2]=="08-12") and (counts["count_dopol"]>0)) or ((values[2]=="12-16") and (counts["count_odpol"]>0)):
      database.insert_slot(values)
      status_type = {"ok": 1,
                     "error_code": 0,
                     "error_desc": ""}
      status = {
          "status_return": status_type,
          "slot_id": slot_id}
    else:
        status_type = {"ok": 0,
                    "error_code": 1,
                       "error_desc": "Insufficient number of slots"}
        status = {
            "status_return": status_type,
            "slot_id": None}
    return status


@app.delete("/delivery_timeslots/{slot_id}", include_in_schema=True)
async def delete_timeslot(slot_id: str):
    if database.slot_exist(slot_id):
        database.delete_slot(slot_id)
        status_type = {"ok": 1,
                   "error_code": 0,
                   "error_desc": ""}
    else:
        status_type = {"ok": 0,
                "error_code": 1,
                "error_desc": "slot_id doesnt exist"}
    status = {
        "status_return": status_type,
        "slot_id": slot_id}
    return status

@app.on_event("startup")
#@repeat_every(seconds=5, raise_exceptions=True)
@repeat_at(cron="2 0 * * *", raise_exceptions=True) #every dat at 00:02
async def set_to_zero():
    svatky = ["2024-03-29", "2024-04-01", "2024-05-01", "2024-05-08",
          "2024-07-05", "2024-07-06", "2024-09-28", "2024-10-28",
          "2024-11-17", "2024-12-24", "2024-12-25", "2024-12-26",
          "2025-01-01", "2025-04-18", "2025-04-21", "2025-05-01",
          "2025-05-08", "2025-07-05", "2025-07-06", "2025-09-28",
          "2025-10-28", "2025-11-17", "2025-12-24", "2025-12-25", "2025-12-26"]
    
    def next_bday(day: datetime.date):
        day = day + datetime.timedelta(days=1)
        while day.strftime("%Y-%m-%d") in svatky or day.weekday() == 5 or day.weekday() == 6:
            day = day + datetime.timedelta(days=1)
        return day 
    
    datum_D0 = datetime.date.today() #dnes
    datum_D1 = next_bday(datum_D0) #dalsi pracovni den
    datum_D2 = next_bday(datum_D1)
    database.edit_slots2((datum_D0.strftime("%Y-%m-%d"), '0', '0'))
    database.edit_slots2((datum_D1.strftime("%Y-%m-%d"), '0', '0')) 
    database.edit_slots2((datum_D2.strftime("%Y-%m-%d"), '0', '0'))
    print(f'Vynulovany prepravy pro dnes a dalsi 2 pracovni dny: {datum_D0.strftime("%Y-%m-%d")}; {datum_D1.strftime("%Y-%m-%d")}; {datum_D2.strftime("%Y-%m-%d")}')

if __name__ == "__main__":
    # LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s [%(name)s] %(levelprefix)s %(message)s"
    LOGGING_CONFIG["formatters"]["access"][
        "fmt"] = '%(asctime)s [%(name)s] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'

    uvicorn.run("main:app", host="0.0.0.0", port=5052,
                log_level="info", reload=True)
