import sqlite3
import json

db_file = "zalohaDB/LGE_2024.db"


def create_connection(db_file=db_file):
    conn = sqlite3.connect(db_file)
    conn.cursor().execute('''
                          CREATE TABLE IF NOT EXISTS ReservedSlots (
                            id text PRIMARY KEY,
                            slot_date text NOT NULL,
                            slot_time text NOT NULL,
                            customer_cap text NOT NULL,
                            quantity integer NOT NULL,
                            product_id integer NOT NULL);
                          ''')

    conn.cursor().execute('''
                          CREATE TABLE IF NOT EXISTS AvailableSlots (
                            date text PRIMARY KEY,
                            count_odpol integer NOT NULL,
                            count_dopol integer NOT NULL);
                          ''')

    return conn


def select_as(datumOd, datumDo):
    conn = create_connection()
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    cursor.execute(f'''
                SELECT json_object(
                    'date', date,
                    'count_dopol', count_dopol,
                    'count_odpol', count_odpol)
                FROM AvailableSlots as2
                WHERE  as2.date BETWEEN '{datumOd}' AND '{datumDo}'
                ''')
    rows = cursor.fetchall()
    return [json.loads(x) for x in rows]

    
def select_availeble_slots_dopol(datumOd, datumDo):
    conn = create_connection()
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    cursor.execute(f'''
                SELECT json_object(
                    'date', date,
                    'time_slot', '08-12',
                    'slot_number', count_dopol,
                    'delivery_appointment_date',IIF(as2.count_dopol > 0, date||" 8:01", NULL))
                FROM AvailableSlots as2
                WHERE  as2.date BETWEEN '{datumOd}' AND '{datumDo}'
                ''')
    rows = cursor.fetchall()
    return [json.loads(x) for x in rows]

def select_availeble_slots_odpol(datumOd, datumDo):
    conn = create_connection()
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    cursor.execute(f'''
                SELECT json_object(
                    'date', date,
                    'time_slot', '12-16',
                    'slot_number', count_odpol,
                    'delivery_appointment_date',IIF(as2.count_odpol > 0, date||" 12:01", NULL))
                FROM AvailableSlots as2
                WHERE  as2.date BETWEEN '{datumOd}' AND '{datumDo}'
                ''')
    rows = cursor.fetchall()
    return [json.loads(x) for x in rows]

def select_availeble_slots_vse(datumOd, datumDo):
    conn = create_connection()
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    cursor.execute(f'''
                SELECT json_object(
                    'date', date,
                    'time_slot', '08-12',
                    'slot_number', count_dopol,
                    'delivery_appointment_date',IIF(as2.count_dopol > 0, date||" 8:01", NULL))
                FROM AvailableSlots as2
                WHERE  as2.date BETWEEN '{datumOd}' AND '{datumDo}'
                UNION
                SELECT json_object(
                    'date', date,
                    'time_slot', '12-16',
                    'slot_number', count_odpol,
                    'delivery_appointment_date',IIF(as2.count_odpol > 0, date||" 12:01", NULL))
                FROM AvailableSlots as2 
                WHERE  as2.date BETWEEN '{datumOd}' AND '{datumDo}'
                ''')
    rows = cursor.fetchall()
    return [json.loads(x) for x in rows]

def insert_slot(values):
    # Establish a connection to the database
    conn = create_connection()
    cursor = conn.cursor()
    if values != None:
        cursor.execute(
            'INSERT INTO ReservedSlots (id, slot_date, slot_time, customer_cap, quantity, product_id) VALUES(?,?,?,?,?,?)', values)
        if values[2]=="08-12":
            cursor.execute(f"UPDATE AvailableSlots SET count_dopol = count_dopol - 1 WHERE count_dopol > 0 AND AvailableSlots.date = '{values[1]}'")
        elif values[2]=="12-16":
            cursor.execute(f"UPDATE AvailableSlots SET count_odpol = count_odpol - 1 WHERE count_odpol > 0 AND AvailableSlots.date = '{values[1]}'")
            
    # Commit the changes and close the connection
    conn.commit()
    conn.close()


def edit_slots(values):
    # Establish a connection to the database
    conn = create_connection()
    cursor = conn.cursor()
    if values != None:
        for value in values:
            #print(value)
            cursor.execute(f'INSERT OR REPLACE INTO AvailableSlots (date,count_dopol,count_odpol) VALUES(?,?,?)', value)
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
def edit_slots2(value):
    # Establish a connection to the database
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f'INSERT OR REPLACE INTO AvailableSlots (date,count_dopol,count_odpol) VALUES(?,?,?)', value)
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def delete_slot(id: str) -> str:
    cursor = create_connection()
    data = cursor.execute(f'SELECT slot_date, slot_time FROM ReservedSlots WHERE id="{id}"')
    rows = data.fetchall()
    print(rows[0][1])
    if rows != []:
        if rows[0][1] == "08-12":
            cursor.execute(f"UPDATE AvailableSlots SET count_dopol = count_dopol + 1 WHERE AvailableSlots.date = '{rows[0][0]}'")
        elif rows[0][1]=="12-16":
            cursor.execute(f"UPDATE AvailableSlots SET count_odpol = count_odpol + 1 WHERE AvailableSlots.date = '{rows[0][0]}'")
        cursor.execute(f'DELETE FROM ReservedSlots WHERE id="{id}"')
    cursor.commit()
    cursor.close()
    return id

def number_of_rows(datum: str) -> int:
    cursor = create_connection().cursor()
    data = cursor.execute(
        f'SELECT COUNT(slot_date) FROM ReservedSlots WHERE slot_date="{datum}"')
    return data.fetchall()[0][0]


def get_avlslot_counts(datum: str) -> dict:
    conn = create_connection()
    conn.row_factory = lambda cursor, row: row[0]
    cursor = conn.cursor()
    data = cursor.execute(
        f'''
        SELECT
        json_object(
            'date', date, 
            'count_dopol', count_dopol,
            'count_odpol', count_odpol)
        FROM AvailableSlots as2
        WHERE date="{datum}"
        ''')
    rows = data.fetchall()
    return json.loads(rows[0])

def slot_exist(id: str) -> bool:
    cursor = create_connection()
    data = cursor.execute(
        f'SELECT slot_date FROM ReservedSlots WHERE id="{id}"')
    rows = data.fetchall()
    if rows != []:
        # print(rows[0][0])
        return True
    else:
        return False
