from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'isatudata'
app.secret_key = 'isatu'

mysql = MySQL(app)


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register')
def register():
    pass

@app.route('/login', methods=['POST'])
def login():
    if request.method == "POST":
        user = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM studentdatas WHERE student_email = %s AND student_pass = %s", (user, password))
        users = cursor.fetchone()

        cursor.close()
        if users:
            ids = users[0]
            name = users[1]
            session['ids'] = ids
            session['name'] = name

            return redirect(url_for('firstpage'))
        else:
            flash('Wrong account number or password')
            return redirect(url_for('index'))

@app.route('/firstpage')
def firstpage():
    ids = session.get('ids')
    name = session.get('name')
    session['ids'] = ids
    return render_template('firstpage.html',name=name,ids=ids)

@app.route('/message')
def message():
    ids = session.get('ids')
    cur = mysql.connection.cursor()
    print(ids)
    cur.execute(f"SELECT * FROM request_form WHERE student_id = {ids} ")
    data = cur.fetchall()
    transaction_list = []
    for row in data:
        transaction = {
            'sname': str(row[1]),
            'sid': str(row[0]),
            'request': row[5],
            'option': row[4],
            # Add other fields as needed
        }
        transaction_list.append(transaction)
    return render_template('message.html',transaction=transaction_list)

@app.route('/submit', methods=['POST','GET'])
def submit():
    request_form = []
    if request.method == 'POST':
        user = session.get('ids')
        name = session.get('name')
        option = request.form.getlist('option')
        cur = mysql.connection.cursor()
        options = ', '.join(option)
        cur.execute(f"INSERT INTO request_form (student_id,student_name,requested_form) VALUES (%s,%s,%s)", (user,name,options,))
        print(user)
        mysql.connection.commit()
        print(options)


        return redirect(url_for('payment'))

@app.route("/payment")
def payment():
    ids = session.get('ids')
    print(ids)

    session['ids'] = ids
    return render_template('payment.html')

@app.route('/registrar_dashboard')
def registrar_dashboard():
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT * FROM request_form WHERE opttion = 'pending' ORDER BY date_requested DESC")
    data = cur.fetchall()
    transaction_list = []
    for row in data:
        transaction = {
            'sname': str(row[1]),
            'sid': str(row[0]),
            'request': row[2],
            'rdate': row[3],
            'id': row[6],
            # Add other fields as needed
        }
        transaction_list.append(transaction)
    return render_template('registrar_dashboard.html',transaction=transaction_list)

@app.route('/message_from_registrar/<string:id>',methods=['GET'])
def message_from_registrar(id):
    cur = mysql.connection.cursor()
    cur.execute(f"UPDATE request_form SET opttion = 'Accepted' WHERE id= {id}" )
    mysql.connection.commit()
    session['id'] = id
    return redirect(url_for('mess'))

@app.route('/messages_from_registrar/<string:id>',methods=['GET'])
def messages_from_registrar(id):
    cur = mysql.connection.cursor()
    cur.execute(f"UPDATE request_form SET opttion = 'Decline' WHERE id= {id}" )
    mysql.connection.commit()
    session['id'] = id
    return redirect(url_for('mess'))

@app.route('/mess',methods=["POST","GET"])
def mess():
    if request.method == "POST":
        id = session.get('id')
        print(id)
        mess = request.form['mess']
        cur = mysql.connection.cursor()
        cur.execute(f"UPDATE request_form SET registrarm = '{mess}' WHERE id= {id}")
        mysql.connection.commit()
        return redirect(url_for('registrar_dashboard'))

    return render_template('mregistrar.html')

@app.route('/about')
def about():
    return render_template("Aboutpage.html")

@app.route('/contact')
def contact():
    return render_template("Contactpage.html")

@app.route('/features')
def features():
    return render_template("Featurespage.html")

@app.route('/mregistrar',methods=["POST"])
def mregistrar():
    if request.method == "POST":
        id = session.get('id')
        mess = request.form['mess']
        cur = mysql.connection.cursor()
        cur.execute(f"UPDATE request_form SET registrarm = {mess} WHERE student_id= {id}")
        mysql.connection.commit()
        return render_template('registrar_dashboard.html')

    return render_template('mregistrar.html')

@app.route('/logout')
def logout():
    session['ids'] = None
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)

