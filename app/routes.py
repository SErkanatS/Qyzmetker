from flask import flash, redirect, render_template, session, url_for, request
import jwt
from app.forms import LoginForm, ResetForm, SetPasswordForm, UserRegistrationForm, UserUpdateForm
from app.models import User
from app import app, db, bcrypt, s, SignatureExpired, Message, mail
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import and_, func


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login',  methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.email_confirm:
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Неверный логин или пароль! Попробуйте еще раз', 'danger')
        else:
            flash("Подтвердите почту!", 'warning')
    return render_template('login.html', title='Login', form=form)

@app.route('/sign-up', methods=['POST', 'GET']) 
def sign_up(): 
    if current_user.is_authenticated: 
        return redirect(url_for('home')) 
    form = UserRegistrationForm() 
    if form.validate_on_submit(): 
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') 
            user = User( 
            first_name=form.first_name.data, 
            last_name=form.last_name.data, 
            email=form.email.data, 
            phone_number=form.phone_number.data, 
            password=hashed_password 
            ) 
            token = s.dumps(form.email.data, salt='email-confirm')
            msg = Message('Confirm Email', sender='teach2u.0000@gmail.com', recipients=[form.email.data])
            
            link = url_for('email_confirm', token=token,email=form.email.data, _external=True)
            msg.body = 'Your link is {}'.format(link)
            mail.send(msg)
            db.session.add(user)
            db.session.commit()
            flash(f'Ваш аккаунт успешно создан! Подтвердите почту', 'success')
            return redirect(url_for('login'))
 
    return render_template('register.html', title='Sign-up', form=form)

@app.route("/email_confirm/<token>/<email>")
def email_confirm(token, email):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
        user = User.query.filter_by(email=email).first()
        if user:
            user.email_confirm = True
            db.session.commit()
            flash(f'Успех! Теперь вы можете войти на сайт.', 'success')
            return redirect(url_for('login'))
    except SignatureExpired:
        user = user.query.filter_by(email=email).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            flash("Время выделенное на подтвеждение почты истекло! Пройдите регистрацию заново.", 'danger')
            return redirect(url_for('sign_up'))
    return render_template("email_confirm.html", title='Email confirm')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/profile")
@login_required
def profile():
   return render_template('profile.html', title='Profile')

@app.route("/profile-update", methods=['POST', 'GET'])
@login_required
def profile_update():
      form = UserUpdateForm()
      if request.method == "GET":
         form.first_name.data = current_user.first_name
         form.last_name.data = current_user.last_name
         form.email.data = current_user.email
         form.phone_number.data = current_user.phone_number
         return render_template('update.html', title='Update profile', form=form)
      else:
            if form.validate_on_submit():
                    email = User.query.filter_by(email=form.email.data).first()
                    phone = User.query.filter_by(phone_number=form.phone_number.data).first()

                    if (phone and phone.id == current_user.id) or (email and email.id == current_user.id) or (phone is None and email is None) :
                        current_user.first_name=form.first_name.data 
                        current_user.last_name=form.last_name.data 
                        current_user.email=form.email.data 
                        current_user.phone_number=form.phone_number.data 
                        db.session.commit()
                        flash("Данные успешно изменены!", 'success')
                        return redirect(url_for('profile'))
                    else:
                        flash("Почта или телефон уже заняты!", "danger")
                        return redirect(url_for('profile'))
            else:
                flash("Почта или телефон уже заняты!", "danger")
                return redirect(url_for('profile'))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetForm()
    if form.validate_on_submit():
        email = request.form['email']
        token = generate_password_reset_token(email)
        send_password_reset_email(email, token)
        flash('Инструкции по сбросу пароля были отправлены на почту {}'.format(email), "success")
        return redirect(url_for('login'))
    return render_template('reset_password.html', form = form)

def generate_password_reset_token(email):
    token = s.dumps(email, salt='password-reset')
    return token

def send_password_reset_email(email, token):
    msg = Message('Password Reset Request', 
                  sender='teach2u.0000@gmail.com', 
                  recipients=[email])
    msg.body = """Для сброса пароля нажмите на следующую ссылку:
{}
Если же вы не совершали запрос на сброс пароля проигнорируйте письмо.
""".format(url_for('reset_password_with_token', token = token,  _external=True))
    mail.send(msg)

@app.route('/reset_password_with_token/<token>', methods=['GET', 'POST'])
def reset_password_with_token(token):
    form = SetPasswordForm()
    email = s.loads(token, salt='password-reset', max_age=3600)

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User.query.filter_by(email=email).first() 
        if user:
            user.password = hashed_password
            db.session.commit()
            flash("Пароль был успешно изменен!" "success")
            return redirect(url_for('login'))
    return render_template('set_password.html', form= form)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/courses')
def courses():
    return render_template('courses.html', title='Courses')

@app.route('/contact')
def contact():
    return render_template('contact.html', title='Contact')

@app.route('/playlist')
def playlist():
    return render_template('playlist.html', title='Playlist')
    
@app.route('/teacher_profile')
def teacher_profile():
    return render_template('teacher_profile.html', title='Teacher')
    
@app.route('/watch_video')
def watch_video():
    return render_template('watch-video.html', title='Video')