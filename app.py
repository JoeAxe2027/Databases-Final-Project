from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import errorcode
import pygal

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = 'your_secret_key'


def get_db_connection():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root"
            port="6603"
            database="classicmodels"
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Invalid credidnetion")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database not found")
        else:
            print(err)
        exit()
    return mydb

#Home dashboard page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        report_type = request.form['report_type']
        if report_type == 'products':
            return redirect(url_for('products'))
        elif report_type == 'customers':
            return redirect(url_for('customers'))
        elif report_type == 'employees':
            return redirect(url_for('employees'))
    return render_template('index.html')