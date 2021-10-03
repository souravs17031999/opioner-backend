import time
from flask import Flask, jsonify
import psycopg2
import os

app = Flask(__name__)

# mysql = MySQL()
# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'DHANPURA8'
# app.config['MYSQL_DATABASE_DB'] = 'dev'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# app.config['SECRET_KEY'] = "adminTokenAuthForViewResponse"

# mysql.init_app(app)
DATABASE_URL = f"postgres://{os.getenv('PGUSER')}:{os.getenv('PGPASSWORD')}@{os.getenv('PGHOST')}/{os.getenv('PGDATABASE')}"

conn = psycopg2.connect(DATABASE_URL)


@app.route('/')
def hello():

    # conn = mysql.connect()
    cursor = conn.cursor()
    print("------------------- conn : ", conn)
    print("--------------cursor: ", cursor)
    affected_count = 0

    query = ("SELECT * FROM task_list")
    try:
        cursor.execute(query)
        affected_count = cursor.rowcount
        db_data = cursor.fetchall()
        print(db_data)
    except Exception as e:
        print(e)
    finally:
        cursor.close()

    print("----------------------------------------------------")
    print(cursor.query.decode())
    print(f"{affected_count} rows affected")
    print("----------------------------------------------------")

    return jsonify({"status": "success", "message": "you made it using docker !"})
