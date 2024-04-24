from flask import Flask, render_template, redirect, abort, request
from data import db_session
from data.messages import Message
from data.users import User
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from forms.message import MessageForm
from data.categories import category
import validators

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret_key123'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route("/")
@app.route("/forum")
def index():
    return render_template("main.html")


@app.route("/forum/<name>")
def forum(name):
    if name in category:
        db_sess = db_session.create_session()
        mes = db_sess.query(Message).filter(Message.category == name)[::-1]
        return render_template("index.html", category=name, desc=category[name], mes=mes)
    else:
        return render_template("404.html")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
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
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


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


@app.route('/mes/<category>/<reply>', methods=['GET', 'POST'])
@login_required
def add_mes(category, reply):
    form = MessageForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        mes = Message()
        mes.content = form.content.data
        if not validators.url(form.url.data):
            mes.url = ""
        else:
            mes.url = form.url.data
        mes.category = category
        mes.reply = reply
        current_user.news.append(mes)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(f'/forum/{category}')
    return render_template('mes.html', title='Добавление сообщения',
                           form=form)


@app.route('/mes/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_mes(id):
    form = MessageForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        mes = db_sess.query(Message).filter(Message.id == id,
                                            Message.user == current_user
                                            ).first()
        if mes:
            form.content.data = mes.content
            form.url.data = mes.url
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        mes = db_sess.query(Message).filter(Message.id == id,
                                            Message.user == current_user
                                            ).first()
        if mes:
            mes.content = form.content.data
            mes.url = form.url.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('mes.html',
                           title='Редактирование сообщения',
                           form=form
                           )


@app.route('/mes_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def mes_delete(id):
    db_sess = db_session.create_session()
    mes = db_sess.query(Message).filter(Message.id == id,
                                        Message.user == current_user
                                        ).first()
    if mes:
        db_sess.delete(mes)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
