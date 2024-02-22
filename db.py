import datetime
import sqlite3

db_file = "zalohaDB/zkusebni.db"

def create_connection(db_file=db_file):
    conn = sqlite3.connect(db_file)
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    reservedSlots_sql = '''
                          CREATE TABLE IF NOT EXISTS ReservedSlots (
                            id text PRIMARY KEY,
                            slot_date text NOT NULL,
                            slot_time text NOT NULL,
                            customer_cap text NOT NULL,
                            quantity integer NOT NULL,
                            product_id integer NOT NULL);
                          '''
    availableSlots_sql = '''
                          CREATE TABLE IF NOT EXISTS AvailableSlots (
                            date text PRIMARY KEY,
                            count_dopol integer NOT NULL,
                            count_odpol integer NOT NULL);
                          '''
    cursor.execute(reservedSlots_sql)
    cursor.execute(availableSlots_sql)
    conn.commit()
    conn.close()


    conn = create_connection()
    cur = conn.cursor()
    cur.execute(f'''
                SELECT json_object('date', date,'count_odpol',count_odpol,'dopol', count_dopol)
                FROM AvailableSlots av2
                WHERE  av2.slot_date BETWEEN "{datumOd}" AND "{datumDo}"
                ORDER BY av2.date
                ''')
    rows = cur.fetchall()
    for row in rows:
        print(row)
 

 # Function to insert data into the database

def number_of_rows(datum:str)->int:
    conn = create_connection()
    cursor = conn.cursor()
    data = cursor.execute(f'SELECT COUNT(slot_date) FROM ReservedSlots WHERE slot_date="{datum}"')
    return data.fetchall()[0][0]

   
def insert_pocty(datumOd, datumDo, pocet_dopol, pocet_odpol):
    svatky = ['2023-07-05', '2023-07-06', '2023-09-28', '2023-10-28',
              '2023-11-17', '2023-12-24', '2023-12-25', '2023-12-26',
              '2023-12-31', "2024-01-01", "2024-03-29", "2024-04-01",
              "2024-05-01", "2024-05-08", "2024-07-05", "2024-07-06",
              "2024-09-28", "2024-10-28", "2024-11-17", "2024-12-24",
              "2024-12-25","2024-12-26"]
    start_date = datetime.date(int(datumOd.split("-")[0]), int(datumOd.split("-")[1]), int(datumOd.split("-")[2]))
    end_date = datetime.date(int(datumDo.split("-")[0]), int(datumDo.split("-")[1]), int(datumDo.split("-")[2]))
    conn = create_connection()
    cursor = conn.cursor()
    while start_date<=end_date:
        #print(start_date)
        if datetime.datetime.weekday(start_date) == 5: # type: ignore
            cursor.execute(f'INSERT OR REPLACE INTO AvailableSlots (date, count_dopol, count_odpol) VALUES("{start_date}",0,0)')
        elif datetime.datetime.weekday(start_date) == 6: # type: ignore
           cursor.execute(f'INSERT OR REPLACE INTO AvailableSlots (date, count_dopol, count_odpol) VALUES("{start_date}",0,0)')
        elif start_date.strftime("%Y-%m-%d") in svatky:
           cursor.execute(f'INSERT OR REPLACE INTO AvailableSlots (date, count_dopol, count_odpol) VALUES("{start_date}",0,0)')
        else:
            cursor.execute(f'INSERT OR REPLACE INTO AvailableSlots (date, count_dopol, count_odpol) VALUES("{start_date}",{pocet_dopol},{pocet_odpol})')
        start_date = start_date+datetime.timedelta(days=1)
    conn.commit()
    conn.close()
    
conn = create_connection()
create_tables()
insert_pocty("2023-12-01", "2024-12-31", 20, 30)
#print(av_slots("2024-01-02"))
#select_all_reserved_slots("2023-12-10","2023-12-20")
