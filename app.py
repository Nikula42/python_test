import os
import os.path

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from flask_login import UserMixin
from flask_login import LoginManager, login_user, login_required, logout_user, current_user


class User(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.username = username
        self.password = password


load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATA_URL')
app.config['UPLOAD_FOLDER'] = os.getenv('STATIC')
db = SQLAlchemy(app)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

users = {}


@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    photo_path = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)


@app.route('/post/<int:id>')
def hello(id):
    post2 = Post.query.get_or_404(id)
    return render_template('post.html', post=post2)


@app.route('/add_post', methods=["POST", "GET"])
@login_required
def add_page():
    if request.method == 'POST':
        title = request.form['text_web']
        text = request.form['story']
        category = request.form['user-sity']
        photo = request.files.get('photo')
        print(photo)
        photo_path = None
        if photo and allowed_file(photo.filename):
            filename = secure_filename(photo.filename)
            photo_path = filename
            print(photo_path)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        elif photo:
            flash('Не подходящий формат файла')
        try:
            new_post = Post(title=title, text=text, photo_path=photo_path, category=category)
            db.session.add(new_post)
            db.session.commit()
        except:
            flash('Ошибка при добавлении статьи в БД')

        return redirect('/')
    else:
        return render_template("add post.html")


@app.route('/information')
def info():
    return render_template('info.html')


@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    global next_user_id
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            print("Пользователь с таким именем уже существует.")
            return redirect(url_for('register'))

        user = User(username, password)
        users[username] = user

        print("Вы успешно зарегистрированы!")
        print(users)
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/auth/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('index'))
        return 'Неверные учетные данные'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)