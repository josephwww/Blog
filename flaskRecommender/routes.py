import os
from recommender.read_movies import get_movie
from flask import render_template, send_from_directory, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flaskRecommender import app, db, bcrypt
from flaskRecommender.forms import RegistrationForm, LoginForm, RatingForm
from flaskRecommender.models import User, Rating, Demography


def update_demography(user):
    # scores = dict()
    # for rating in user.ratings:
    #     scores[rating.film_id] = rating.score
    d = Demography(owner=user, male=30, age1=18, age1_p=60, age2=25, age2_p=30, occup1=1, occup1_p=50, occup2=6, occup2_p=30)
    db.session.add(user)
    db.session.commit()


@app.route('/')
def index():
    return redirect(url_for('home'))


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html', title='About')



@app.route('/vote', methods=['POST', 'GET'])
@login_required
def vote():
    form = RatingForm()
    ran_movie = get_movie()
    movie_id = ran_movie['movie_id']
    if form.validate_on_submit():
        if form.yes.data:
            rating = Rating(author=current_user, score=5, film_id=movie_id)
        elif form.no.data:
            rating = Rating(author=current_user, score=1, film_id=movie_id)
        elif form.unknown.data:
            # rating = Rating(author=current_user, score=0, film_id=movie_id)
            return render_template('vote.html', form=form, movie_info=ran_movie)
        else:
            rating = Rating(author=current_user, score=3, film_id=movie_id)
        db.session.add(rating)
        db.session.commit()
        update_demography(current_user)
    return render_template('vote.html', form=form, movie_info=ran_movie)


@app.route('/result', methods=['POST', 'GET'])
@login_required
def result():
    rating = Rating.query.filter_by(user_id=current_user.id)
    return render_template('result.html', title='Result', ratings=rating)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f"Your account has been created! You are now able to login", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                else:
                    return redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check your password', 'danger')
        flash('Login Unsuccessful. Email does not exist', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/rating/<int:rating_id>/delete", methods=['POST'])
@login_required
def delete_rating(rating_id):
    rating = Rating.query.get_or_404(rating_id)
    if rating.author != current_user:
        abort(403)
    db.session.delete(rating)
    db.session.commit()
    update_demography(current_user)
    return redirect(url_for('result'))