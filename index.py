from flask import Flask, render_template

SITE = {
    'name': 'Nike',
    'owner': 'Vitor Irapuã',
    'logo': '/static/img/logo.png',
    'favicon': '/static/img/logo.png'
}


app = Flask(__name__)

@app.route('/')
def home():
    
    toPage = {
        # Título da página → <title></title>
        'site': SITE,
        'title': '',
        'css': 'home.css'
    }
    
    return render_template('home.html', page=toPage)


@app.route('/contacts')
def contacts():
    
    toPage = {
        # Título da página → <title></title>
        'site': SITE,
        'title': 'Faça contato',
        'css': 'contacts.css'
    }
    
    return render_template('contacts.html', page=toPage)

@app.route('/about')
def about():
    
    toPage = {
        # Título da página → <title></title>
        'site': SITE,
        'title': 'Sobre nós',
        'css': 'about.css'
    }
    
    return render_template('about.html', page=toPage)    


@app.route('/policies')
def policies():
    
    toPage = {
        # Título da página → <title></title>
        'site': SITE,
        'title': 'Politícas de Privacidade',
        'css': 'policies.css'
    }
    
    return render_template('policies.html', page=toPage)            

if __name__ == '__main__':
    app.run(debug=True)