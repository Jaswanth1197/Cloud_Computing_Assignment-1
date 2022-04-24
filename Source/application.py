import os
import uuid
from flask import Flask, session,render_template,request, Response, redirect, send_from_directory
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from db import db_init, db
from models import  User, Product
from datetime import datetime
from flask_session import Session
from helpers import login_required
import urllib.request


applicaton = app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Admin123@database-online-store.cadudrikeyav.us-east-1.rds.amazonaws.com/onlinestoredb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_init(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = os.urandom(16) 

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/Books')
def books():
    return render_template('Books.html')

@app.route('/Clothing')
def clothing():
    return render_template('Clothing.html')

@app.route('/Electronics')
def electronics():
    return render_template('Electronics.html')

@app.route('/Accessories')
def accessories():
    return render_template('Accessories.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/welcome')
def welcome():
    #return render_template('welcome.html')
    urllib.request.urlretrieve('https://u9fwaz18pl.execute-api.us-east-1.amazonaws.com/default/welcome-page', './templates/welcome-page.html')
    return render_template('welcome-page.html')

@app.route('/<folder>/<filename>')
def article(folder, filename):
    return render_template('/' + folder + '/' + filename + '.html')

@app.route("/signup", methods=["GET","POST"])
def signup():
	if request.method=="POST":
		session.clear()
		password = request.form.get("password")
		repassword = request.form.get("repassword")
		if(password!=repassword):
			return render_template("error.html", message="Passwords do not match!")

		#hash password
		pw_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
		
		fullname = request.form.get("fullname")
		username = request.form.get("username")
		#store in database
		new_user =User(fullname=fullname,username=username,password=pw_hash)
		try:
			db.session.add(new_user)
			db.session.commit()
		except:
			return render_template("error.html", message="Username already exists!")
		return render_template("login.html", msg="Account created!")
	return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
	if request.method=="POST":
		session.clear()
		username = request.form.get("username")
		password = request.form.get("password")
		result = User.query.filter_by(username=username).first()
		print(result)
		# Ensure username exists and password is correct
		if result == None or not check_password_hash(result.password, password):
			return render_template("error.html", message="Invalid username and/or password")
		# Remember which user has logged in
		session["username"] = result.username
		return welcome()
	return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop('username', None)

    return redirect('/')

@app.route('/search', methods = ['POST'])
def search():

    if request.method == 'POST':
    
        if request.form['search'] == 'Search':
            
            search_string = request.form["searchword"]

            article_search = []
            dir_path = 'templates'
            for folder in os.listdir(dir_path):
                if os.path.isdir(os.path.join(dir_path, folder)):
                    for filename in sorted(os.listdir(os.path.join(dir_path, folder))):
                        if filename.endswith('html'):
                            with open(os.path.join(dir_path, folder, filename), encoding="utf8") as file:
                                file_content = file.read()

                                if search_string in file_content:
                                    article_search.append([folder, filename.replace('.html', '')])
                                else:
                                    render_template('home.html')
    
    else:
        return render_template('home.html')

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = False)

application = app
