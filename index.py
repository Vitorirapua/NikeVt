from datetime import datetime, timedelta
from flask import Flask, json, make_response, redirect, render_template, request, url_for
from flask_mysqldb import MySQL


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

    cookie = request.cookies.get('user_data')

    if cookie == None:
        return redirect(f"{url_for('login')}")

    print('\n\n\n', cookie, '\n\n\n')

    user_id = '1'

    sql = '''
        SELECT *
        FROM thing
        WHERE
            t_owner = %s
            AND t_status != 'del'
        ORDER BY t_date DESC;
    '''
    cur = mysql.connection.cursor()
    cur.execute(sql, (user_id, ))
    things = cur.fetchall()
    cur.close()

    toPage = {
        'site': SITE,
        'title': 'Página Inicial',
        'css': 'home.css',
        'things': things # Passa os itens para o template
    }

    return render_template('home.html', things=things, page=toPage)


@app.route('/login', methods=['GET', 'POST'])
def login():

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

        print('\n\n\n', user, '\n\n\n')

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

    toPage = {
        'site': SITE,
        'title': 'Página Inicial',
        'css': 'login.css'
    }

    return render_template('login.html', error=error, page=toPage)


if __name__ == '__main__':
    app.run(debug=True)

    

    