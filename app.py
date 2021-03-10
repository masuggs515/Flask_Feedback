from flask import Flask, render_template, session, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///auth_practice'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "abc123"

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/register', methods=["GET", "POST"])
def user_sign_up():
    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
        db.session.commit()
        if new_user:
            session["username"] = new_user.username
            return redirect(f'/users/{new_user.username}')
    else:
        return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def user_login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session["username"] = form.username.data
            return redirect(f'/users/{user.username}')
    else:
        return render_template('login.html', form=form)


@app.route('/users/<username>')
def user_details(username):
    
    if 'username' in session:
        user = User.query.filter_by(username=username).first()
        feedback = Feedback.query.all()
        return render_template('user_details.html', user=user, feedback=feedback)
    else:
        flash('You must be logged in.')
        return redirect('/')

@app.route('/logout')
def log_user_out():
    session.pop('username')
    return redirect('/')

@app.route('/users/<username>/delete')
def delete_user(username):
    user = User.query.filter_by(username=username).first()
    if user.username == session["username"]:
        db.session.delete(user)
        db.session.commit()
        flash(f'User {user.username} has been deleted')
        return redirect('/')
    else:
        flash('You do not have permission to delete this user.')
        return redirect(f'/users/{user.username}')

@app.route('/users/<username>/feedback/add', methods=["POST", "GET"])
def add_feedback(username):
    form = FeedbackForm()

    user = User.query.filter_by(username=username).first()
    
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(title=title, content=content, username= user.username)
        db.session.add(new_feedback)
        db.session.commit()
        return redirect(f'/users/{user.username}')
    else:
        return render_template('add_feedback_form.html', form=form, user=user)

@app.route('/feedback/<feedback_id>/update', methods=["GET", "POST"])
def update_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        return redirect(f'/users/{feedback.user.username}')
    else:
        return render_template('update_feedback.html', form=form, feedback=feedback)
        
@app.route('/feedback/<feedback_id>/delete')
def delete_post(feedback_id):
    delete_feedback = Feedback.query.get_or_404(feedback_id)
    if delete_feedback.user.username == session["username"]:
        db.session.delete(delete_feedback)
        db.session.commit()
        return redirect(f'/users/{delete_feedback.user.username}')