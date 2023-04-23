from flask import Flask, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import render_template, redirect, abort, request
from data import db_session
from forms.user import LoginForm, RegisterForm
from forms.addreview import AddReviewForm
from forms.addcomment import AddCommentForm
from data.users import User
from data.comments import Comment
from data.reviews import Review
from flask import make_response
from flask_restful import reqparse, abort, Api, Resource
import os
import codecs

SIZE = 40

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


def avatar_setup(current_user):
    """Функция подготовки аватарки"""
    try:
        path = f"./static/imgs/{current_user.nickname}.png"
        with open(path, "wb") as file:
            file.write(current_user.get_avatar(SIZE))
    except Exception as e:
        print(e)
        path = ""
    return path


@login_manager.user_loader
def load_user(user_id: int):
    """Функция погрузки пользователя"""
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/", defaults={'search_id': 0})
@app.route("/index", defaults={'search_id': 0})
@app.route("/index/<int:search_id>")
def index(search_id=0):
    db_sess = db_session.create_session()
    if search_id == 0:
        reviews = db_sess.query(Review).all()
    else:
        reviews = db_sess.query(Review).filter(Review.language == search_id).all()
    path = avatar_setup(current_user)
    return render_template("index.html", reviews=reviews, current_user=current_user, avatar=path.replace(".", ""),
                           size=SIZE)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            email=form.email.data,
            nickname=form.nickname.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/addreview', methods=['GET', 'POST'])
@login_required
def add_review():
    form = AddReviewForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        review = Review()
        review.author = current_user.id

        file = form.code.data
        filename = file.filename
        file.save(os.path.join('uploads', f"{filename.split('.')[0]}.txt"))
        with codecs.open(f'./uploads/{filename.split(".")[0]}.txt', 'r', "utf_8_sig") as f:
            code = f.read()
        review.code = code

        print(form.language.data)
        review.language = form.language.data
        current_user.reviews.append(review)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    path = avatar_setup(current_user)
    return render_template('addreview.html', title='Adding a Review',
                           form=form, avatar=path.replace(".", ""),
                           size=SIZE)


@app.route('/review/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_review(id):
    form = AddReviewForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        review = db_sess.query(Review).filter(Review.id == id).first()
        if review and (review.author_user == current_user or current_user.id == 1):
            form.language.data = review.language
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        review = db_sess.query(Review).filter(Review.id == id).first()
        if review and (review.author_user == current_user or current_user.id == 1):
            file = form.code.data
            filename = file.filename
            file.save(os.path.join('uploads', f"{filename.split('.')[0]}.txt"))
            with codecs.open(f'./uploads/{filename.split(".")[0]}.txt', 'r', "utf_8_sig") as f:
                code = f.read()
            review.code = code
            review.language = form.language.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    path = avatar_setup(current_user)
    return render_template('addreview.html',
                           title='Редактирование записи',
                           form=form, avatar=path.replace(".", ""),
                           size=SIZE)


@app.route('/review_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def review_delete(id):
    db_sess = db_session.create_session()
    review = db_sess.query(Review).filter(Review.id == id).first()
    if review and (review.author_user == current_user or current_user.id == 1):
        db_sess.delete(review)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/comment_review/<int:id>', methods=['GET', 'POST'])
@login_required
def comment_review(id):
    if request.method == "GET":
        db_sess = db_session.create_session()
        review = db_sess.query(Review).filter(Review.id == id).first()
        path = avatar_setup(current_user)
        return render_template('commentreview.html',
                               title='Суд вершиться!',
                               review=review, avatar=path.replace(".", ""),
                               size=SIZE)


@app.route('/add_comment_review/<int:id>', methods=['GET', 'POST'])
@login_required
def add_comment_review(id):
    form = AddCommentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        review = db_sess.query(Review).filter(Review.id == id).first()
        comment = Comment()
        comment.author = current_user.id
        comment.review_id = id
        comment.comment_text = form.comment_text.data
        review.comments.append(comment)
        db_sess.merge(review)
        db_sess.commit()
        return redirect(f'/comment_review/{comment.review_id}')
    path = avatar_setup(current_user)
    return render_template('addcomment.html', title='Adding a Comment',
                           form=form, avatar=path.replace(".", ""),
                           size=SIZE)


@app.route('/comment/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_comment(id):
    form = AddCommentForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        comment = db_sess.query(Comment).filter(Comment.id == id).first()
        if comment and (comment.author_user == current_user or current_user.id == 1):
            form.comment_text.data = comment.comment_text
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        comment = db_sess.query(Comment).filter(Comment.id == id).first()
        if comment and (comment.author_user == current_user or current_user.id == 1):
            comment.comment_text = form.comment_text.data
            db_sess.commit()
            return redirect(f'/comment_review/{comment.review_id}')
        else:
            abort(404)
    path = avatar_setup(current_user)
    return render_template('addcomment.html',
                           title='Редактирование записи',
                           form=form, avatar=path.replace(".", ""),
                           size=SIZE)


@app.route('/comment_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def comment_delete(id):
    db_sess = db_session.create_session()
    comment = db_sess.query(Comment).filter(Comment.id == id).first()
    if comment and (comment.author_user == current_user or current_user.id == 1):
        db_sess.delete(comment)
        db_sess.commit()
    else:
        abort(404)
    return redirect(f'/comment_review/{comment.review_id}')


def main():
    db_name = "court.db"
    db_session.global_init(f"db/{db_name}")
    db_sess = db_session.create_session()

    app.run(port=8080, host='0.0.0.0', debug=False)


if __name__ == '__main__':
    main()
