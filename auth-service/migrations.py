import os
import psycopg2

print(
    "------------------------------INITIALIZING DATABASE ------------------------------"
)
DATABASE_URL = f"postgres://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}/{os.getenv('PGDATABASE')}"
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True
cursor = conn.cursor()

print("------------------------------MIGRATING DATABASE ------------------------------")

with cursor as cursor:
    cursor.execute(open("dbinit/dev_26092021_schema.sql", "r").read())


cursor = conn.cursor()
if os.getenv("REQUIRE_DB_INSERT") == "True":
    print("-------------------------- DATABASE INSERTION IN PROGRESS ---------------")
    with cursor as cursor:
        cursor.execute(open("dbinit/dev_26092021_inserts.sql", "r").read())
else:
    print(" ------------------SKIPPING INSERTION OF DB RECORDS -----------------")

print(
    "--------------------------- DATABASE MIGRATIONS DONE ------------------------------"
)
