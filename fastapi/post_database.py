## switch to orm it will reduce the manual writing and it is real application 
import psycopg
from nested_model import patient1_json


"""psycopy connect to db"""
conn_info = (
    "dbname=patient_db user=postgres password='216125642781' host=localhost port=5432"
)

# """creating the automate of create table in db"""
# type_list = {
#     int: "INTEGER",
#     str: "VARCHAR(255)",
#     datetime: "TIMESTAMPZ",
#     float: "DOUBLE PRECISION",
#     bool: "BOOLEAN",
#     bytes: "BYTEA",
# }

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS patient (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    gender VARCHAR(10) NOT NULL
        CHECK (gender IN ('male', 'female', 'other')),
    city VARCHAR(255) NOT NULL,
    state VARCHAR(255) NOT NULL,
    pincode VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    verified_at TIMESTAMPTZ,
    token_hash CHAR(64) NOT NULL UNIQUE
);
"""


def add_db(patient1_json):
    try:
        with psycopg.connect(conn_info) as conn:  ##conn= psycopg.connect(conn_info)
            print("successfully connected")
            with conn.cursor() as cur:  # cur= conn.cursor()
                # column_table = []
                # for field_name, field_type in Patient.model_fields.items():
                #     field_type = type_list.get(
                #         field_type.annotation, "TEXT"
                #     )  # text is giving default value if type not found
                #     column_table.append(f"{field_name} {field_type}")
                # column_table = ",".join(column_table)
                # cur.execute(f" CREATE TABLE IF NOT EXITS patient( {column_table});")
                cur.execute(CREATE_TABLE)

                columns = ", ".join(patient1_json.keys())
                """PostgreSQL syntax uses %(key)s for named parameters"""
                values = ", ".join(f"%({key})s" for key in patient1_json.keys())
                insert_query = f"INSERT INTO users ({columns}) VALUES ({values});"
                cur.execute(insert_query, patient1_json)

    except Exception as error:
        print(f"Error while connecting to the db {error}")
