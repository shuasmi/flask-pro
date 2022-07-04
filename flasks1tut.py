from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import json
import os
import math
from flask_mail import Mail

with open('config.json', 'r') as c:
    params = json.load(c)["params"]
local_server = True
app = Flask(__name__)  # creating the Flask class object
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_location']
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
)
mail = Mail(app)
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)

class srlogin(db.Model):
    '''
    sno, name phone_num, msg, date, email
    '''
    srno = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String(80), nullable=False)
    password= db.Column(db.String(20), nullable=False)

class Post(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    img_url = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String, nullable=False)
    slug = db.Column(db.String(120), nullable=False)


@app.route("/")
def web():
    posts = Post.query.filter_by().all()
    last = math.ceil(len(posts) / int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page - 1) * int(params['no_of_posts']):(page - 1) * int(params['no_of_posts']) + int(params['no_of_posts'])]
    if page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"

    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)


    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)


@app.route("/home")
def home():
    posts = Post.query.filter_by().all()
    last = math.ceil(len(posts) / int(params['no_of_posts']))
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page = 1
    page = int(page)
    posts = posts[(page - 1) * int(params['no_of_posts']):(page - 1) * int(params['no_of_posts']) + int(
        params['no_of_posts'])]
    if page == 1:
        prev = "#"
        next = "/?page=" + str(page + 1)
    elif page == last:
        prev = "/?page=" + str(page - 1)
        next = "#"

    else:
        prev = "/?page=" + str(page - 1)
        next = "/?page=" + str(page + 1)


    return render_template('index.html', params=params, posts=posts, prev=prev, next=next)



@app.route('/about')
def about():
    posts=Post.query.all()
    post=Post.query.all()
    return render_template('about.html',params=params,posts=posts,post=post)

@app.route('/login',methods = ['GET', 'POST'])
def login():
    if (request.method == 'POST'):
        '''Add entry to the database'''
        email = request.form.get('email')
        password = request.form.get('password')
        entry = srlogin(email_address=email,password=password)
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ',
                          sender=email,
                          recipients=[params['gmail-user']],
                          body=password
                          )
    return render_template('login.html',params=params)

@app.route('/post/<string:post_slug>',methods=['GET'])
def post_route(post_slug):
    post = Post.query.filter_by(slug=post_slug).first()

    return render_template('post.html', params=params,post=post)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if "user" in session and session['user'] == params['admin_user']:
        posts =Post.query.all()
        return render_template("about.html", params=params,posts=posts)

    if request.method == 'POST':
        username = request.form.get("uname")
        userpass = request.form.get("password")
        if username == params['admin_user'] and userpass == params['admin_password']:
            # set the session variable
            session['user'] = username
            posts=Post.query.all()
            return render_template("about.html", params=params,posts=posts)

    return render_template("dashboard.html", params=params)

@app.route("/uploader" , methods=['GET', 'POST'])
def uploader():
    if (request.method == 'POST'):
        f = request.files['file1']
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        return "Uploaded successfully!"





@app.route("/edit/<string:srno>", methods=['GET', 'POST'])
def edit(srno):
    post = Post.query.get(srno)
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.slug = request.form.get('slug')
        db.session.commit()
        return redirect('/about')
    return render_template('edit.html',post=post,params=params)

@app.route("/delete/<string:srno>" , methods=['GET', 'POST'])
def delete(srno):
    post = Post.query.filter_by(srno=srno).first()
    db.session.delete(post)
    db.session.commit()


    return redirect("/about")







if __name__ == '__main__':
    app.run(debug=True)