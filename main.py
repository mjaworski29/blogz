from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(225))
    body = db.Column(db.String(100000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/', methods=['POST', 'GET'])
def index():
    
    if request.method=="GET":
        return redirect("/blog")

    if request.method == 'POST':
        return redirect("/newpost")

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
    new_blog = Blog(blog_title, blog_body)
    db.session.add(new_blog)
    db.session.commit()
    return redirect("/")

@app.route("/blog/", methods=["GET"])
def blog():
    
    if request.method=="GET":
        blogs = Blog.query.all()
        id_request = request.args.get("id")
        if id_request != None:
            blog_post = Blog.query.get(id_request)
            return render_template('individualblog.html', blog_post=blog_post)
        return render_template('bloglistings.html',title="Build a Blog!", 
        blogs=blogs)


if __name__ == '__main__':
    app.run()