from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogzpassword@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "y337kGcys&zP3B"

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(225), unique=True)
    password = db.Column(db.String(225))
    blogs = db.relationship('Blog', backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(225))
    body = db.Column(db.String(100000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

@app.before_request
def require_login():
    allowed_routes = ['login', 'index', 'signup', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['GET'])
def index():
    
    if request.method == "GET":
        users = User.query.all()
        owner = request.args.get("owner_id")
        if owner:
            owner_posts = User.query.get(owner)
            return render_template('index.html', owner_posts=owner_posts)


@app.route("/newpost", methods=["POST", "GET"])
def newpost():
    if request.method == "GET":
        return render_template('addnewpost.html')

    blog_titles = request.form['blogtitle']
    blog_posts = request.form['blogbody']

    blog_title_error = ""
    blog_post_error = ""

    is_error = False

    if blog_titles == "":
        blog_title_error = "Please enter a Blog Title"
        is_error = True
    
    if blog_posts == "":
        blog_post_error = "Please enter a Blog Post"
        is_error = True 
    
    if is_error:
        return render_template('addnewpost.html', blog_title_error=blog_title_error, blog_post_error=blog_post_error )

    blog_title = request.form['blogtitle']
    blog_body = request.form["blogbody"]
    blog_owner = User.query.filter_by(username=session['username']).first()
    new_blog = Blog(blog_title, blog_body, blog_owner)
    db.session.add(new_blog)
    db.session.commit()
    return render_template("individualblogs.html", blog_title=blog_title, blog_body=blog_body)

@app.route("/blog/", methods=["GET", "POST"])
def blog():

    if request.method == "GET":
        blogs = Blog.query.all()
        users = User.query.all()
        id_request = request.args.get("id")
        owner = request.args.get("owner_id")
        if id_request:
            blog_post = Blog.query.get(id_request)
            return render_template('individualblog.html', blog_post=blog_post)
        elif owner:
            owner_posts = Blog.query.get(owner)
            return render_template('singleuser.html', owner_posts=owner_posts, blogs=blogs)
        return render_template('bloglistings.html', title="All the Blogz!", blogs=blogs, users=users)



    if request.method == "POST":
        blog_name = request.form['blog']
        new_task = Blog(blog_name, owner)
        db.session.add(new_task)
        db.session.commit()

    blogs = Blog.query.filter_by(owner=owner).all()
    return render_template('bloglistings.html', blogs=blogs)    

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template('login.html')

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect ('/newpost')
        else:
            flash("User password incorrect, or user does not exist", 'error')
    return redirect ("/login")

@app.route("/signup", methods=["POST", "GET"])
def signup():

    if request.method == "GET":
        return render_template("signup.html")

    username = request.form['username']
    password = request.form['password']
    verify = request.form['verify']

    username_error = ""
    password_error = ""
    verify_error = ""

    is_error = False

    if username == "" or len(username) < 3:
        username_error = "Username invalid"
        is_error = True
    
    if password == "" or len(password) < 3:
        password_error = "Invalid password"
        is_error = True 
    
    if verify == "" or verify != password:
        verify_error = "Invalid attempt at password retype"
        is_error = True 
    
    if is_error:
        return render_template('signup.html', username_error=username_error, password_error=password_error, verify_error=verify_error )

    existing_user = User.query.filter_by(username=username).first()
    if not existing_user:
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        return redirect('/newpost')
    else:
        flash("Duplicate user")
        return render_template("signup.html")

    return render_template('bloglistings.html')


@app.route('/logout')
def logout():
    del session ['username']
    return redirect ('/login')

if __name__ == '__main__':
    app.run()