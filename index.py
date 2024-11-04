from datetime import datetime, timedelta
import json
from flask import Flask, make_response, redirect, render_template, request, url_for
from flask_mysqldb import MySQL
import subprocess
import random
import string

SITE = {
    'name': 'Cadastro de coisas',
    'criador': 'Vitor Irapuã',
    'logo': '/static/img/logo.png',
    'favicon': '/static/img/logo.png'
}

app = Flask(__name__)

# Configurações de acesso ao MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'crudvtdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_USE_UNICODE'] = True
app.config['MYSQL_CHARSET'] = 'utf8mb4'

mysql = MySQL(app)

def send_email(email_to, subject, content):
    url = "https://api.sendgrid.com/v3/mail/send"
    api_key = ""
    email_from = "andre@luferat.net"

    payload = {
        "personalizations": [{
            "to": [{
                "email": email_to
            }]
        }],
        "from": {
            "email": email_from
        },
        "subject": subject,
        "content": [{
            "type": "text/plain",
            "value": content
        }]
    }

    result = subprocess.run([
        "curl",
        "--request", "POST",
        "--url", url,
        "--header", f"Authorization: Bearer {api_key}",
        "--header", "Content-Type: application/json",
        "--data", json.dumps(payload)
    ], capture_output=True, text=True)

    return result.stdout, result.stderr


def get_new_password(tamanho=8):
    caracteres = string.ascii_letters + string.digits + "_-$&"
    return ''.join(random.choice(caracteres) for _ in range(tamanho))



@app.before_request
def before_request():
    cur = mysql.connection.cursor()
    cur.execute("SET NAMES utf8mb4")
    cur.execute("SET character_set_connection=utf8mb4")
    cur.execute("SET character_set_client=utf8mb4")
    cur.execute("SET character_set_results=utf8mb4")
    cur.execute("SET lc_time_names = 'pt_BR'")
    cur.close()


@app.route('/')
def home():
   
    edit = request.args.get('edit')
    delete = request.args.get('delete')

    cookie = request.cookies.get('user_data')

    if cookie == None:
        return redirect(f"{url_for('login')}")

    user = json.loads(cookie)
    user['fname'] = user['name'].split()[0]

    sql = '''
        SELECT t_id, t_photo, t_name, t_status
        FROM thing
        WHERE
            t_owner = %s
            AND t_status != 'del'
        ORDER BY t_date DESC;
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql, (user['id'], ))
    things = cur.fetchall()
    cur.close()

    toPage = {
        'site': SITE,
        'title': 'Página Inicial',
        'css': 'home.css',
        'things': things,
        'user': user,
        'edit': edit,
        'delete': delete

    }
    return render_template('home.html',  page=toPage)

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    toPage = {
        'site': SITE,
        'title': 'Página Inicial',
        'css': 'login.css'
    }

    error = ''

    if request.method == 'POST':

        form = dict(request.form)

        print('\n\n\n', form, '\n\n\n')

        sql = '''
            SELECT o_id, o_name
            FROM owner
            WHERE o_email = %s
                AND o_pass = SHA1(%s)
                AND o_status = 'on';
        '''
        cur = mysql.connection.cursor()
        cur.execute(sql, (form['email'], form['password'], ))
        user = cur.fetchone()
        cur.close()

        # print('\n\n\n', user, '\n\n\n')

        if user != None:

            resp = make_response(redirect(url_for('home')))

            cookie_data = {
                'id': user['o_id'],
                'name': user['o_name']
            }

            print('\n\n\nCookie:', cookie_data, '\n\n\n')
            # Data em que o cookie expira
            expires = datetime.now() + timedelta(days=365)
            # Adicona o cookie à página
            resp.set_cookie('user_data', json.dumps(
                cookie_data), expires=expires)

            return resp

        else:
            error = 'Login e/ou senha errados!'

    return render_template('login.html', error=error, page=toPage)



@app.route('/new', methods=['GET', 'POST'])
def new():

    sucess = False

    toPage = {
        'site': SITE,
        'title': 'Novo treco',
        'css': 'new.css'
    }


    cookie = request.cookies.get('user_data')

    if cookie == None:
        return redirect(f"{url_for('login')}")

    user = json.loads(cookie)
    user['fname'] = user['name'].split()[0]

    if request.method == 'POST':
        form = dict(request.form)

        sql = '''
            INSERT INTO thing (
                t_owner, t_photo, t_name, t_description, t_location
            ) VALUES (
                %s, %s, %s, %s, %s
            )
        '''
        cur = mysql.connection.cursor()
        cur.execute(sql, (user['id'], form['photo'],
                    form['name'], form['description'], form['location']))
        mysql.connection.commit()
        cur.close()

        success = True

    return render_template('new.html', user=user, page=toPage)

@app.route('/view/<id>')
def view(id):
    toPage = {
        'site': SITE,
        'title': 'Novo treco',
        'css': 'view.css'
    }

    cookie = request.cookies.get('user_data')

    if cookie == None:
        return redirect(f"{url_for('login')}")

    user = json.loads(cookie)
    user['fname'] = user['name'].split()[0]

    sql = '''
        SELECT t_id, t_date, t_photo, t_name, t_description, t_location
        FROM thing
        WHERE t_status = 'on' AND t_owner = %s AND t_id = %s
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql, (user['id'], id,))
    thing = cur.fetchone()
    cur.close()

    print('\n\n\n', thing, '\n\n\n')

    return render_template('view.html', user=user, thing=thing, page=toPage)


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    toPage = {
        'site': SITE,
        'title': 'Novo treco',
        'css': 'view.css'
    }

    cookie = request.cookies.get('user_data')

    if cookie == None:
        return redirect(url_for('login'))

    user = json.loads(cookie)
    user['fname'] = user['name'].split()[0]

    if request.method == 'POST':

        form = dict(request.form)

        sql = '''
            UPDATE thing SET 
                t_photo = %s,
                t_name = %s,
                t_description = %s,
                t_location = %s
            WHERE t_status = 'on'
                AND t_owner = %s
                AND t_id = %s
        '''
        cur = mysql.connection.cursor()
        cur.execute(sql, (form['photo'], form['name'], form['description'], form['location'], user['id'], id,))
        mysql.connection.commit()
        cur.close()

        return redirect(url_for('home', edit=True))

    sql = '''
        SELECT t_id, t_date, t_photo, t_name, t_description, t_location
        FROM thing
        WHERE t_status = 'on' AND t_owner = %s AND t_id = %s
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql, (user['id'], id,))
    thing = cur.fetchone()
    cur.close()

    return render_template('edit.html', user=user, page=toPage, thing=thing)


@app.route('/delete/<id>')
def delete(id):
    cookie = request.cookies.get('user_data')
    if cookie == None:
        return redirect(url_for('login'))
    user = json.loads(cookie)
    user['fname'] = user['name'].split()[0]

    sql = '''
        UPDATE thing SET
            t_status = 'del'
        WHERE t_owner = %s
            AND t_id = %s
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql, (user['id'], id,))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('home', delete=True))

@app.route('/logout')
def logout():

    resp = make_response(redirect(url_for('login')))

    resp.set_cookie('user_data', '', expires=0)

    return resp


@app.route('/newuser', methods=['GET', 'POST'])
def newuser():

    cookie = request.cookies.get('user_data')
    if cookie != None:
        return redirect(url_for('home'))    

    feedback = ''
    form = {}

    toPage = {
        'site': SITE,
        'title': 'cadastre-se',
        'css': 'newuser.css'
        
    }



    if request.method == 'POST':

        form = dict(request.form)

        sql = '''
            SELECT count(o_id) AS total
            FROM owner
            WHERE o_email = %s
                AND o_status != 'del'
        '''
        cur = mysql.connection.cursor()
        cur.execute(sql, (form['email'], ))
        total = int(cur.fetchone()['total'])
        cur.close()

        if total == 0:
            sql = '''
                INSERT INTO owner (o_birth, o_name, o_email, o_pass)
                VALUES (%s, %s, %s, SHA1(%s))
            '''
            cur = mysql.connection.cursor()
            cur.execute(sql, (form['birth'], form['name'],
                        form['email'], form['password'],))
            mysql.connection.commit()
            cur.close()

            feedback = 'success'

        else:
            form['email'] = ''
            feedback = 'error'

    return render_template('newuser.html', page=toPage, feedback=feedback, form=form)

@app.route('/profile')
def profile():
    toPage = {
        'site': SITE,
        'title': 'Perfil',
        'css': 'profile.css'
        
    }

    cookie = request.cookies.get('user_data')
    if cookie == None:
        return redirect(url_for('login'))
    user = json.loads(cookie)
    user['fname'] = user['name'].split()[0]

    sql = '''
        SELECT *
        FROM owner
        WHERE o_id = %s
            AND o_status = 'on'
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql, (user['id'], ))
    userdata = cur.fetchone()
    cur.close()

    del userdata['o_pass']

    print('\n\n\n', userdata, '\n\n\n')

    return render_template('/profile.html', user=user, userdata=userdata, page=toPage)

@app.route('/sendpass', methods=['GET', 'POST'])
def sendpass():
    toPage = {
        'site': SITE,
        'title': 'Perfil',
        'css': 'profile.css'
        
    }

    feedback = ''

    if request.method == 'POST':
        form = dict(request.form)
        sql = '''
            SELECT o_id, o_email, o_name
            FROM owner
            WHERE o_email = %s
                AND o_status = 'on'
        '''
        cur = mysql.connection.cursor()
        cur.execute(sql, (form['email'], ))
        userdata = cur.fetchone()
        cur.close()

        print('\n\n\n', userdata, '\n\n\n')

        if userdata != None:

            new_password = get_new_password()

            sql = '''
                UPDATE owner
                SET o_pass = SHA1(%s)
                WHERE o_id = %s
                    AND o_status = 'on'
            '''
            cur = mysql.connection.cursor()
            cur.execute(sql, (new_password, userdata['o_id'],))
            mysql.connection.commit()
            cur.close()

            mail_message = f'''
Olá {userdata['o_name']}!

Você pediu uma nova senha de acesso ao "Cadastro de Trecos".

Use esta senha para fazer login: {new_password}

Obrigado...
            '''
            send_email(
                userdata['o_email'],
                'Cadastro de Trecos - nova senha',
                mail_message
            )

            feedback = 'success'

        else:
            feedback = 'error'

    return render_template('sendpass.html', page=toPage, feedback=feedback)

if __name__ == '__main__':
    app.run(debug=True)