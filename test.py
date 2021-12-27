from flask import Flask, render_template, request, url_for, flash
from flask_login.utils import logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import pyshorteners
import sqlite3
import pyperclip
from globaluser import Login

import localbase

localbase.checkBase()

app = Flask(__name__)
app.config['SECRET_KEY'] = '2dac65609ffed636456505864'

login_manager = LoginManager(app)


def logincheck(login):
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    user = cursor.execute("""SELECT login FROM "users" WHERE login = ?""",(login,)).fetchone()
    if not user:
        return 0
    else:
        return 1

def regUser(login, password):
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    cursor.execute("""INSERT INTO "users" (login, password) VALUES(?, ?)""",(login, password,))
    con.commit()

def getUserLogin(login):
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    res = cursor.execute("""SELECT * FROM "users" WHERE login = ? LIMIT 1""",(login,)).fetchone()
    if not res:
        return False   
    return res

def getUser(user_id):    
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    res = cursor.execute("""SELECT * FROM users WHERE id = ? LIMIT 1""",(user_id)).fetchone()
    if not res:
        return False   
    return res

def shortener(user_id, name, link, status):
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    cursor.execute("""INSERT INTO links (user_id, name, link, status) VALUES(?, ?, ?, ?)""",(user_id, name, link, status,))
    con.commit()   
    con.close()

def LinkPrivate(user_id):
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    links = cursor.execute("""SELECT * FROM "links" WHERE user_id = ?""",(user_id)).fetchall()
    con.commit()
    return links


def LinkForUsers():
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    links = cursor.execute("""SELECT * FROM links WHERE status = 'для пользователей'""").fetchall()
    con.commit()
    print(links)
    return links

@login_manager.user_loader
def load_user(user_id):
    print('load_user')
    return Login().logOnDatabase(user_id, localbase)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли')
    return redirect(url_for('/'))

@app.route('/', methods=['POST', 'GET'])
def index():
    print("Ссылки пользователей")
    con = sqlite3.connect('database.db')
    cursor = con.cursor()
    links = cursor.execute("""SELECT * FROM "links" WHERE status = 'public'""").fetchall()
    con.commit()
    print(links)
    con.close()
    if request.method == 'POST':
        url = request.form.get('link')
        link = pyshorteners.Shortener().tinyurl.short(url)
        pyperclip.copy(link)
        flash(f'новая ссылка: {link}')
    return render_template('index.html', links = links, title="Сокращатель")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        login = request.form['login'] 
        password = request.form['password'] 
        hash = generate_password_hash(password)
        reg = logincheck(login)
        if reg == 1:
            flash("Такой логин уже есть!")
        elif reg == 0:
            regUser(login, hash)
            flash("регистрация пройдена")
            return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация') 

@app.route('/login', methods=['POST', 'GET'])
def login(): 
    if current_user.is_authenticated:
        return redirect(url_for('userLog'))

    if request.method == 'POST': 
        user = getUserLogin(request.form['login']) 
        if user and check_password_hash(user[2], request.form['password']):
            userLog = Login().create(user)
            rm = True if request.form.get('remainme') else False
            login_user(userLog, remember=rm)
            return redirect(request.args.get('next') or url_for('userLog'))
        else:
            flash('Неверные данные!')
     
    return render_template('login.html', title='Авторизация') 


@app.route('/userLog', methods=['POST', 'GET'])
@login_required
def userLog(): 
    user = getUser(current_user.get_id())
    login = user[1]
    status = request.form.get('status')
    name = request.form.get('name')
    url = request.form.get('link')
    link = pyshorteners.Shortener().tinyurl.short(url)
    pyperclip.copy(link)
    shortener(user[0], name, link, status)
    flash(f'сокращенная ссылка: <a href="{link}">{link}</a>')

    links = LinkPrivate(user[0])
    return render_template('userLog.html', title='Личный кабинет', login = login, links = links) 


@app.route('/linksForUsers')
@login_required
def linksForUser(): 
    linksForUser = LinkForUsers()
    return render_template('linksForUsers.html', title='Ссылки для пользователей', links = linksForUser)


if __name__ == "__main__": 
    app.run()
    
