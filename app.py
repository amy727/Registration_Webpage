
##Import
from flask import Flask, redirect, render_template, request
import sqlite3
from sqlite3 import Error
import logging

# Configure app
app = Flask(__name__)

#configure log file
logging.basicConfig(filename='logfile.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

# Variables
person = []

#create db connection
def create_db_connection():
    try:
        conn = sqlite3.connect("registration_database.sqlite")
        return conn
    except Error as e:
        logging.error(e)
        print(e)

#create cursor
def create_cursor(c):
    try:
        cursor = c.cursor()
        return cursor
    except Error as e:
        logging.error(e)
        print(e)

def create_table(cursor):
    #Command to create table
    create_registrants_table = """ CREATE TABLE IF NOT EXISTS REGISTRANTS(
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    first_name text NOT NULL,
                                    last_name text NOT NULL,
                                    gender text NOT NULL,
                                    address text NOT NULL

                                ); """ 
    try:
        cursor.execute(create_registrants_table) #creates table
    except Error as e: #error exception
        logging.error(e)
        print(e)

def insert_entry(conn, cursor, entry):
    insert_command = """ INSERT INTO REGISTRANTS(first_name, last_name, gender, address) 
                        VALUES(?,?,?,?) """ #db command to insert
    try:
        cursor.execute(insert_command, entry) #insert entry to database
        conn.commit()
    except Error as e: #error exception
        logging.error(e)
        print(e)

def update_entry(conn, cursor, entry):
    update_command = """ UPDATE REGISTRANTS
                        SET first_name = ?, last_name = ?, gender = ?, address = ? 
                        WHERE id = ? """ #db command to update
    try:
        cursor.execute(update_command, entry) #update entry in database
        conn.commit()
    except Error as e: #error exception
        logging.error(e)
        print(e)

def get_id(cursor, entry):
    #get id
    get_id_command = """ SELECT id FROM REGISTRANTS WHERE
                    (first_name=?) AND (last_name=?) AND 
                    (gender=?) AND (address=?)""" ##db command
    try:
        cursor.execute(get_id_command, entry)
        r_id = cursor.fetchone() #get registrant's id
        if r_id == None:
            return r_id #returns None if there is no id
        else:
            return r_id[0] #otherwise returns the first id
    except Error as e:
        logging.error(e)
        print(e) #error exception

def get_registrants(cursor):
    get_data_command = """ SELECT * FROM REGISTRANTS """ #db command
    registrant_info = []

    try:
        cursor.execute(get_data_command)
        data = cursor.fetchall()
        if data == None:
            return registrant_info #return empty list if None is returned
        else:
            for entry in data: #otherwise parse data into a dictionary and append to list
                registrant_info.append({"id":entry[0], "firstname":entry[1], "lastname":entry[2],
                                "gender":entry[3], "address":entry[4]})
            return registrant_info #return list
    except Error as e: #error exception
        logging.error(e)
        print(e)

#INDEX PAGE - Form
@app.route("/")
def index():
    return render_template("index.html")

#SUCCESS PAGE - indicates success and outputs index id of registrant
@app.route("/success")
def success():

    #get id
    conn = create_db_connection()
    cursor = create_cursor(conn)
    registrant_id = get_id(cursor, (person[0],person[1],person[2],person[3]))
    conn.close()

    #render page
    return render_template("success.html", id=registrant_id)

#REGISTRANTS PAGE - displays the registrants from the database
@app.route("/registrants")
def registrants():
    conn = create_db_connection()
    cursor = create_cursor(conn)
    people = get_registrants(cursor)
    conn.close()
    return render_template("registered.html", people=people)


#REGISTRATION - checks form and registers person
@app.route("/register", methods=["POST"])
def register():
    #get form results
    firstname = request.form.get("firstname")
    lastname = request.form.get("lastname")
    gender = request.form.get("gender")
    address = request.form.get("address")

    #check if everything is filled out
    if not firstname or not lastname or not gender or not address:
        return render_template("failure.html")

    #update person information
    person.clear()
    person.extend([firstname,lastname,gender,address])

    #Create database connection
    conn = create_db_connection()
    cursor = create_cursor(conn)
    create_table(cursor)

    #check if entry already exists
    entry = (firstname,lastname,gender,address)
    personID = get_id(cursor, entry)
    if personID == None:
        insert_entry(conn, cursor, entry)
    else:
        update_entry(conn, cursor, entry + (personID,))
    conn.close()
    

    return redirect("/success")

## MAIN
if __name__ == '__main__':

    app.debug = True
    app.run(host = 'localhost', port = 5000)

    
   
