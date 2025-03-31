import os.path

from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


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
    return render_template('index.html')


@app.route('/post/<id>')
def hello(id):
    post2 = Post.query.get_or_404(id)
    print(post2)
    return render_template('post.html', post=post2)

@app.route('/add_post', methods=["POST", "GET"])
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

if __name__ == '__main__':
    app.run(debug=True)