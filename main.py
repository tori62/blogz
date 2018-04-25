from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] ='mysql+pymysql://blogz:assign4@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'secretpassword'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    body = db.Column(db.String(1000))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,title,body,author):
        self.title = title
        self.body = body
        self.author_id = author


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blog = db.relationship('Blog', backref='author')

    def __init__(self,username,password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['blog','signup','login','index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

# This route allows a writer to signup for access to post a blog.  

@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if not_valid(username):
            error = "Please enter a valid username (between 3-20 characters and no spaces.)"
            username = ''
            password = ''
            return render_template('signup.html',username = username, password = password, name_error=error)
        else:
            pass

        if password == '':
            error = "Please enter a valid password (between 3-20 characters and no spaces.)"
            return render_template('signup.html', username=username, password = password, word_error=error)

        if not_valid(password):
            error = "Please enter a valid password (between 3-20 characters and no spaces.)"
            password = ''
            return render_template('signup.html', username=username, password = password, word_error=error)
        else:
            pass

        if verify != password:
            error = "Password did not match. Please re-enter password and verify."
            password = ''
            return render_template('signup.html',username=username,verify_error = error )
        else:
            pass

        existing_author = User.query.filter_by(username=username).first()
        if not existing_author:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/blog')
        else:
            error = "That username already exists.  Please enter another username."
            password = ''
            return render_template('signup.html',username = username, password = password, name_error=error)
    else:
        return render_template('signup.html')



@app.route('/login', methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify_password']
        user = User.query.filter_by(username=username).first()

        if password == '':
            error = "Please enter password."
            return render_template('login.html', username=username, password = password, word_error=error)

        if verify != password:
            error = "Password did not match. Please re-enter password and verify."
            password = ''
            return render_template('login.html',username=username,verify_error = error )
        elif not user:
            username = ''
            error = "Username does not exist."
            return render_template('login.html', username=username, name_error = error)
        else:
            if user and user.password == password:
                session['username'] = username
                flash('Logged In')
                return redirect('/newpost')  
            else:
                flash('User password is incorrect or user does not exist','error') 

    return render_template('login.html')


@app.route('/newpost', methods=['POST','GET'])
def newpost():
    if request.method == 'POST':
        new_title = request.form['blog-title']
        if not new_title:
            return render_template('newpost.html')
        else:
            new_post = request.form['body']
            username = session['username']
            users = User.query.filter_by(username=username).first()
            author_id = users.id

            if new_title == "" or new_post == "":
                error = "Please enter additional information."
                return render_template('newpost.html',blog_title=new_title,body=new_post,error=error)

            else:
                new_entry = Blog(new_title,new_post,author_id)
                db.session.add(new_entry)
                db.session.commit()
                return redirect('/blog?id=' + str(new_entry.id))

    else:
        return render_template('newpost.html')

@app.route('/')
def index():
    user = User.query.all()
    return render_template('index.html', user = user)

@app.route('/blog', methods=['POST','GET'])
def blog():
    blog_id = request.args.get('id')
    if not blog_id:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs = blogs)
    else:
        blogs = Blog.query.get(blog_id)
        title = blogs.title
        post = blogs.body
        author_id = blogs.author_id
        author = User.query.get(author_id)
        name = author.username
        return render_template('single.html',blog_title=title,body=post, username = name)


@app.route('/logout', methods=['POST','GET'])
def logout():
    if session['username'] == '':
        flash ('You are not logged in')
    else:
        del session['username']
        return redirect('/blog')

def not_valid(info):
    for i in info:
        if i == " ":
            return True
        elif len(info) < 3 or len(info) > 20:
            return True
        else:
            return False


   

if __name__ == '__main__':
    app.run()   