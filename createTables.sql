-- projects table
CREATE TABLE IF NOT EXISTS ReservedSlots (
	id text PRIMARY KEY,
	slot_date text NOT NULL,
    slot_time text NOT NULL,
    customer_cap text NOT NULL,
    quantity integer NOT NULL,
    product_id integer NOT NULL
);

-- tasks table
CREATE TABLE IF NOT EXISTS AvailableSlots (
	id text PRIMARY KEY,
	count_odpol integer NOT NULL,
	count_dopol integer NOT NULL);

INSERT INTO AvailableSlots VALUES("2023-12-01", 50, 50)
INSERT INTO AvailableSlots VALUES("2023-12-02", 0, 0)
INSERT INTO AvailableSlots VALUES("2023-12-03", 0, 0)
INSERT INTO AvailableSlots VALUES("2023-12-04", 50, 50)

INSERT INTO ReservedSlots VALUES("132132","2023-12-04","08-12","69121",1,12)