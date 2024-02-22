import sqlite3

db_file = "zalohaDB/zkusebni.db"

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
                            id text PRIMARY KEY,
                            count_odpol integer NOT NULL,
                            count_dopol integer NOT NULL);
                          ''')
    
    return conn

def select_all_reserved_slots():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ReservedSlots")
    rows = cur.fetchall()
    for row in rows:
        print(row)
 
 # Function to insert data into the database
def insert_data(values):
    # Establish a connection to the database
    conn = create_connection()
    cursor = conn.cursor()
    if values !=None:
        cursor.execute('INSERT INTO ReservedSlots (id, slot_date, slot_time, customer_cap, quantity, product_id) VALUES(?,?,?,?,?,?)', values)
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def number_of_rows(datum:str)->int:
    cursor = create_connection().cursor()
    data = cursor.execute(f'SELECT COUNT(slot_date) FROM ReservedSlots WHERE slot_date="{datum}"')
    return data.fetchall()[0][0]
 
def delete_by_id(id:str):
    cursor=create_connection()
    data = cursor.execute(f'DELETE FROM ReservedSlots WHERE id="{id}"')
    cursor.commit()
    cursor.close()
           
def id_exist(id:str)->bool:
    cursor=create_connection()
    data = cursor.execute(f'SELECT id FROM ReservedSlots WHERE id="{id}"')
    if data.fetchall() != []:
        return True
    else:
        return False
    
def insert_avl_dates(values):
    # Establish a connection to the database
    conn = create_connection()
    cursor = conn.cursor()
    if values !=None:
        cursor.execute('INSERT INTO AvailableSlots (id, count_dopol, count_odpol) VALUES(?,?,?)', values)
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

insert_avl_dates(("2023-12-15",30,30))

