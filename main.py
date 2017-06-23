from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'maggieisababe'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog_list', 'index']

    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    authors = User.query.all()
    return render_template('index.html', authors=authors)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged in', 'success')
            return redirect('/newpost')
        if not user or user == '':
            flash('User don\'t exist, duder.', 'error')
            return render_template('login.html')
        if user.password != password or password == '':
            flash('Wrong password', 'error')
            return render_template('login.html')

    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if len(username) < 3 or username == '':
            flash('Invalid username')
            return render_template('signup.html')
        if verify != password:
            flash('Passwords don\'t fucking match, dude.')
            return render_template('signup.html')
        if password == '':
            flash('Please enter a fuggin\' password, guy.')
            return render_template('signup.html')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('User already exists')
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            flash('Logged in')
            return redirect('/newpost')

    return render_template('signup.html')
# main blog page url
@app.route('/blog')
def blog_list():

    if request.args.get('id'):
        id = request.args.get('id')
        one_blog = Blog.query.filter_by(id=id).first()
        blog_body = one_blog.body
        blog_title = one_blog.title
        return render_template('blogview.html', one_blog=one_blog)

    if request.args.get('user'):
        user = request.args.get('user')
        blog_posts = Blog.query.filter_by(owner_id=user).all()
        return render_template('blog.html', blog_posts=blog_posts)
    else:

    # return render_template('singleUser.html', usernames=usernames)

        blog_posts = Blog.query.all()
        return render_template('blog.html', blog_posts=blog_posts)


@app.route('/newpost', methods=['GET', 'POST'])
def new_post():
    # TODO adjust something in this function to accomodate for the addition of relationship
    # between user class and blog class. use session to check user perhaps?
    # POST requests

    # owner = User.query.filter_by(owner_id = blogs)?
    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':

        # get user input

        new_blog_title = request.form['new_blog_title']
        new_blog_body = request.form['new_blog_body']
        new_post = Blog(new_blog_title, new_blog_body, owner)

        title_error = ''
        body_error = ''

        if new_blog_title == '':
            title_error = 'Danggg, man. Give us a title. C\'mon now.'

        if new_blog_body == '':
            body_error = 'Dude, no. You need some texty stuff.'

        #if not error submit to database
        if not title_error and not body_error:
            db.session.add(new_post)
            db.session.commit()
            id = str(new_post.id)
            return redirect('/blog?id={}'.format(id))
        else:
            return render_template('newpost.html', body_error=body_error, title_error=title_error,
                new_blog_title=new_blog_title, new_blog_body=new_blog_body)


    # retrieve all entries from database
    # blog_posts = db.session.query(Blog)
    # retrieve OWNED entries from database
    # maybe try owner_id = blog
    blogs = Blog.query.filter_by(owner=owner).first()

    return render_template('newpost.html', owner=owner)

@app.route('/logout')
def logout():

        del session['username']
        return redirect('/blog')



if __name__ == '__main__':
    app.run()
