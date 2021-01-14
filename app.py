
from flask import Flask, render_template, request, redirect, session
import mysql.connector
import gunicorn

app = Flask(__name__)

app.secret_key = "Super Secret"

my_db = mysql.connector.connect(
  host="us-cdbr-east-03.cleardb.com",
  user="b41e5d7a9fe22b",
  password="8f65782e",
  database="heroku_a0217320959ca67",
  use_pure=True
)

mycursor = my_db.cursor()
mycursor.execute("CREATE TABLE IF NOT EXISTS events (id INT AUTO_INCREMENT PRIMARY KEY,host VARCHAR(255),description VARCHAR(255),day VARCHAR(255), time VARCHAR(255),status VARCHAR(255) )")
mycursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY,username VARCHAR(255),password VARCHAR(255))")

@app.route('/')
def home():
    if "username" in session:
        sql = "SELECT id,host,description,day,time,status FROM events"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()

        if len(myresult) == 0:
            list =""
        else:
            list=myresult

        return render_template('home.html', user = session['username'], list=list)
    else:
        return render_template('index.html')

@app.route('/myevents')
def myevents():
    host = session['username'];
    sql = "SELECT id,host,description,day,time,status FROM events WHERE host= %s"
    value = (host,)
    mycursor.execute(sql, value)
    myresult = mycursor.fetchall()

    if len(myresult) == 0:
        list =""
    else:
        list=myresult

    return render_template("myEvents.html", user = session['username'], list=list)

@app.route("/add", methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        host = session['username']
        description = request.form.get('description')
        day = request.form.get('day')
        time = request.form.get('time')
        status = "still on"

        sql = "INSERT INTO events(host,description,day,time,status) VALUES (%s, %s, %s, %s, %s)"
        values =[host,description,day,time,status]
        mycursor.execute(sql, values)

        my_db.commit()

        return redirect("/myevents")
    else:
        return render_template("add.html", user = session['username'])
    

@app.route('/cancel/<int:id>')
def delete(id):
    status = "canceled"

    sql = "UPDATE events SET status= %s WHERE id= %s"
    values = (status, id)

    mycursor.execute(sql, values)
    my_db.commit()

    return redirect('/')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
  
  if request.method == 'POST':
    host = session['username']
    description = request.form.get('description')
    day = request.form.get('day')
    time = request.form.get('time')
    status = request.form.get('status')
    
    sql = "UPDATE events SET host= %s, description = %s, day= %s, time=%s, status= %s WHERE id= %s"
    values = (host, description, day, time, status, id)
    mycursor.execute(sql, values)

    my_db.commit()

    return redirect("/")
  else:
    sql = "SELECT id,host,description,day,time,status FROM events WHERE id= %s"
    value = (id,)
    mycursor.execute(sql, value)
    myresult = mycursor.fetchone()

    return render_template('edit.html', event=myresult)

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        sql = "SELECT username FROM users WHERE username =%s  AND password = %s";
        values =[username,password]
        mycursor.execute(sql, values)

        myresult = mycursor.fetchall()

        if len(myresult) > 0:
            session['username'] = username
            return redirect('/')
        else:
            return render_template("index.html", message = "Wrong username or password!")
    else:
        return render_template("index.html")

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')

        if (password != confirm_password):
            return render_template("signup.html", message= "Passwords don't match")
   
        sql = "SELECT username FROM users WHERE username = %s";
        value = (username, )
        mycursor.execute(sql, value)

        myresult = mycursor.fetchall()

        if len(myresult) > 0:
            return render_template("signup.html", message= "Username already taken!")
        else:
            sql = "INSERT INTO users(username, password) VALUES (%s, %s)"
            values =[username,password]
            mycursor.execute(sql, values)
            my_db.commit()

            session['username'] = username
            return redirect("/")
    else:
        return render_template("signup.html")

@app.route('/logout')
def logout():
    # remove the username from the session 
    session.pop('username', None)
    return render_template("index.html")

if __name__ == '__main__':
    app.run()
