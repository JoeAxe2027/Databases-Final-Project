from flask import Flask, render_template, request, flash, url_for, redirect
import mysql.connector
from mysql.connector import errorcode
import pygal
import calendar


app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = 'your secret key'
app.secret_key = 'your secret key'

def get_db_connection():
    try:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            port="6603",
            database="classicmodels"
        )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Invalid username or password.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist.")
        else:
            print(err)
        exit()
    return mydb

#Chart visualization
def generate_bar_chart(title, x_labels, values, label='Sales'):
    chart = pygal.Bar(show_legend=False)
    chart.title = title
    chart.x_labels = x_labels
    chart.add(label, values)
    chart.value_formatter = lambda x: f"${x:,.2f}" if isinstance(x, float) else str(x)
    return chart.render_data_uri()


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def home_navigation_post():
    option = request.form.get('report_type')
    if option == "products":
        return redirect(url_for('product_reports'))
    elif option == "customers":
        return redirect(url_for('customer_reports'))
    elif option == "employees":
        return redirect(url_for('employee_reports'))



@app.route('/product-reports', methods=['GET', 'POST'])
def product_reports():
    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT YEAR(orderDate) as year FROM orders ORDER BY year")
    years = [row['year'] for row in cursor.fetchall()]
    data, graph = [], None

    if request.method == 'POST':
        option = request.form.get('report')
        year = request.form.get('year')

        if option == "monthlyOrderTotals":
            cursor.execute("""
                CREATE OR REPLACE VIEW monthlyOrderTotals AS
                SELECT YEAR(o.orderDate) AS year, MONTH(o.orderDate) AS month,
                       SUM(od.quantityOrdered * od.priceEach) AS totalSales
                FROM orders o
                JOIN orderdetails od ON o.orderNumber = od.orderNumber
                GROUP BY year, month
            """)
            cursor.execute("SELECT * FROM monthlyOrderTotals WHERE year = %s", (year,))
            result = cursor.fetchall()
            data = [{**r, 'monthName': calendar.month_name[r['month']], 'totalSales': f"${r['totalSales']:,.2f}"} for r in result]
            graph = generate_bar_chart(
                f"Monthly Order Totals - {year}",
                [row['monthName'] for row in data],
                [float(row['totalSales'].replace('$','').replace(',','')) for row in data]
            )

        elif option == "orderLineTotals":
            cursor.execute("""
                CREATE OR REPLACE VIEW orderLineTotals AS
                SELECT YEAR(o.orderDate) AS year, p.productLine,
                       SUM(od.quantityOrdered * od.priceEach) AS totalSales
                FROM orders o
                JOIN orderdetails od ON o.orderNumber = od.orderNumber
                JOIN products p ON od.productCode = p.productCode
                GROUP BY year, p.productLine
            """)
            cursor.execute("SELECT * FROM orderLineTotals WHERE year = %s", (year,))
            result = cursor.fetchall()
            data = [{**r, 'totalSales': f"${r['totalSales']:,.2f}"} for r in result]
            graph = generate_bar_chart(
                f"Order Line Totals - {year}",
                [row['productLine'] for row in data],
                [float(row['totalSales'].replace('$','').replace(',','')) for row in data]
            )

        elif option == "productOrderTotals":
            cursor.execute("""
                CREATE OR REPLACE VIEW productOrderTotals AS
                SELECT YEAR(o.orderDate) AS year, p.productName,
                       SUM(od.quantityOrdered * od.priceEach) AS totalSales
                FROM orders o
                JOIN orderdetails od ON o.orderNumber = od.orderNumber
                JOIN products p ON od.productCode = p.productCode
                GROUP BY year, p.productName
            """)
            cursor.execute("SELECT * FROM productOrderTotals WHERE year = %s ORDER BY totalSales DESC", (year,))
            result = cursor.fetchall()
            data = [{**r, 'totalSales': f"${r['totalSales']:,.2f}"} for r in result]
            graph = generate_bar_chart(
                f"Top 10 Product Sales - {year}",
                [row['productName'] for row in data[:10]],
                [float(row['totalSales'].replace('$','').replace(',','')) for row in data[:10]]
            )

    return render_template('products.html', years=years, data=data, graph=graph)

@app.route('/customer-reports', methods=['GET', 'POST'])
def customer_reports():
    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT YEAR(orderDate) as year FROM orders ORDER BY year")
    years = [row['year'] for row in cursor.fetchall()]
    data, graph = [], None

    if request.method == 'POST':
        option = request.form.get('report')
        year = request.form.get('year')

        if option == "customerOrderTotals":
            cursor.execute("""
                CREATE OR REPLACE VIEW customerOrderTotals AS
                SELECT YEAR(o.orderDate) AS year, c.customerName,
                       SUM(od.quantityOrdered * od.priceEach) AS totalOrders
                FROM customers c
                LEFT JOIN orders o ON c.customerNumber = o.customerNumber
                LEFT JOIN orderdetails od ON o.orderNumber = od.orderNumber
                GROUP BY year, c.customerName
            """)
            cursor.execute("SELECT * FROM customerOrderTotals WHERE year = %s ORDER BY totalOrders DESC", (year,))
            result = cursor.fetchall()
            data = [{**r, 'totalOrders': f"${r['totalOrders']:,.2f}"} for r in result]
            graph = generate_bar_chart(
                f"Top 10 Customer Order Totals - {year}",
                [row['customerName'] for row in data[:10]],
                [float(row['totalOrders'].replace('$','').replace(',','')) for row in data[:10]],
                label='Total'
            )

        elif option == "customerPaymentTotals":
            cursor.execute("""
                CREATE OR REPLACE VIEW customerPaymentTotals AS
                SELECT YEAR(p.paymentDate) AS year, c.customerName,
                       SUM(p.amount) AS totalPayments
                FROM customers c
                LEFT JOIN payments p ON c.customerNumber = p.customerNumber
                GROUP BY year, c.customerName
            """)
            cursor.execute("SELECT * FROM customerPaymentTotals WHERE year = %s ORDER BY totalPayments DESC", (year,))
            result = cursor.fetchall()
            data = [{**r, 'totalPayments': f"${r['totalPayments']:,.2f}"} for r in result]
            graph = generate_bar_chart(
                f"Top 10 Customer Payment Totals - {year}",
                [row['customerName'] for row in data[:10]],
                [float(row['totalPayments'].replace('$','').replace(',','')) for row in data[:10]],
                label='Total'
            )

    return render_template('customers.html', years=years, data=data, graph=graph)

@app.route('/employee-reports', methods=['GET', 'POST'])
def employee_reports():
    mydb = get_db_connection()
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT DISTINCT YEAR(orderDate) as year FROM orders ORDER BY year")
    years = [row['year'] for row in cursor.fetchall()]
    data, graph = [], None

    if request.method == 'POST':
        option = request.form.get('report')
        year = request.form.get('year')

        if option == "employeeOrderTotals":
            cursor.execute("""
                CREATE OR REPLACE VIEW employeeOrderTotals AS
                SELECT YEAR(o.orderDate) AS year, CONCAT(e.firstName, ' ', e.lastName) AS fullName,
                       SUM(od.quantityOrdered * od.priceEach) AS totalOrders
                FROM employees e
                LEFT JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
                LEFT JOIN orders o ON c.customerNumber = o.customerNumber
                LEFT JOIN orderdetails od ON o.orderNumber = od.orderNumber
                GROUP BY year, fullName
            """)
            cursor.execute("SELECT * FROM employeeOrderTotals WHERE year = %s ORDER BY totalOrders DESC", (year,))
            result = cursor.fetchall()
            data = [{**r, 'totalOrders': f"${r['totalOrders']:,.2f}"} for r in result]
            graph = generate_bar_chart(
                f"Employee Order Totals - {year}",
                [row['fullName'] for row in data],
                [float(row['totalOrders'].replace('$','').replace(',','')) for row in data],
                label='Total'
            )

        elif option == "employeeOrderNumbers":
            cursor.execute("""
                CREATE OR REPLACE VIEW employeeOrderNumbers AS
                SELECT YEAR(o.orderDate) AS year, CONCAT(e.firstName, ' ', e.lastName) AS fullName,
                       COUNT(DISTINCT o.orderNumber) AS numOrders
                FROM employees e
                LEFT JOIN customers c ON e.employeeNumber = c.salesRepEmployeeNumber
                LEFT JOIN orders o ON c.customerNumber = o.customerNumber
                GROUP BY year, fullName
            """)
            cursor.execute("SELECT * FROM employeeOrderNumbers WHERE year = %s ORDER BY numOrders DESC", (year,))
            result = cursor.fetchall()
            data = result
            graph = generate_bar_chart(
                f"Employee Order Count - {year}",
                [row['fullName'] for row in data],
                [row['numOrders'] for row in data],
                label='Orders'
            )

    return render_template('employees.html', years=years, data=data, graph=graph)

if __name__ == '__main__':
    app.run(port=5008, debug=True)
