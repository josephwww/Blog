import os
from recommender.read_movies import get_movie, get_random_movie
from recommender.rating_space import get_from_rating_space, get_from_LR
from flask import render_template, send_from_directory, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flaskRecommender import app, db, bcrypt
from flaskRecommender.forms import RegistrationForm, LoginForm, RatingForm
from flaskRecommender.models import User, Rating, Demography


def get_demo(ratings, user):
    '''
    get demographic information with given rating and user
    :return the Demographic Data object
    '''
    age1, age2, occu1, occu2, gender1, gender2 = get_from_rating_space(ratings)
    if gender1[0] == 'M':
        male = gender1[1]
    else:
        male = gender2[1]
    return Demography(owner=user, question_type=0, male=male, age1=age1[0], age1_p=age1[1] , age2=age2[0], age2_p=age2[1] ,
                   occup1=occu1[0], occup1_p=occu1[1] , occup2=occu2[0], occup2_p=occu2[1] )


def get_LR_demo(ratings, user):
    '''
    get demographic information with given rating and user using Logistic Regression
    :return the Demographic Data object

    '''
    age1, age2, occu1, occu2, gender1, gender2 = get_from_LR(ratings)
    if gender1[0] == 'M':
        male = gender1[1]
    else:
        male = gender2[1]
    return Demography(owner=user, question_type=0, male=male, age1=age1[0], age1_p=age1[1], age2=age2[0],
                      age2_p=age2[1],
                      occup1=occu1[0], occup1_p=occu1[1], occup2=occu2[0], occup2_p=occu2[1])


def update_demography(user):
    '''
    update current user's demographic
    :return None

    '''
    random_ratings = [(rate.film_id, rate.score) for rate in user.ratings if rate.question_type == 0]
    entropy_ratings = [(rate.film_id, rate.score) for rate in user.ratings if rate.question_type == 1]
    for demo in user.demographics:
        db.session.delete(demo)

    if len(random_ratings) >= 5:
        d = get_demo(random_ratings, user)
        d.question_type = 0
        db.session.add(d)

    if len(entropy_ratings) >= 5:
        d = get_demo(entropy_ratings, user)
        d.question_type = 1
        db.session.add(d)
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


@app.route('/random_vote', methods=['POST', 'GET'])
@login_required
def random_vote():
    form = RatingForm()
    ran_movie = get_random_movie()
    if form.validate_on_submit():
        if form.yes.data:
            rating = Rating(author=current_user, score=5, film_id=int(form.movieID.data), question_type=0)
            if current_user.ratings.count() == 10:
                flash('You have voted enough movies, please switch to Vote(Entropy) if you have not done so.')
        elif form.no.data:
            rating = Rating(author=current_user, score=1, film_id=int(form.movieID.data), question_type=0)
            if current_user.ratings.count() == 10:
                flash('You have voted enough movies, please switch to Vote(Entropy) if you have not done so.')
        elif form.unknown.data:
            return redirect(url_for('random_vote'))
        else:
            rating = Rating(author=current_user, score=3, film_id=int(form.movieID.data), question_type=0)
            if current_user.ratings.count() == 10:
                flash('You have voted enough movies, please switch to Vote(Entropy) if you have not done so.')
        db.session.add(rating)
        ran_movie = get_random_movie()
        db.session.commit()
        update_demography(current_user)
    return render_template('vote.html', form=form, movie_info=ran_movie, title='Random Vote')


@app.route('/entropy_vote', methods=['POST', 'GET'])
@login_required
def entropy_vote():
    form = RatingForm()
    ent_movie = get_movie(current_user.movie_rated)
    if form.validate_on_submit():
        if form.yes.data:
            rating = Rating(author=current_user, score=5, film_id=int(form.movieID.data), question_type=1)
        elif form.no.data:
            rating = Rating(author=current_user, score=1, film_id=int(form.movieID.data), question_type=1)
        elif form.unknown.data:
            current_user.movie_rated += 1
            db.session.commit()
            return redirect(url_for('entropy_vote'))
        else:
            rating = Rating(author=current_user, score=3, film_id=int(form.movieID.data), question_type=1)
        db.session.add(rating)
        current_user.movie_rated += 1
        ent_movie = get_movie(current_user.movie_rated)
        db.session.commit()
        update_demography(current_user)
    return render_template('vote.html', form=form, movie_info=ent_movie, title='Entropy Vote')


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
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, age=form.age.data, gender=form.gender.data, occupation=form.occupation.data)
        db.session.add(user)
        db.session.commit()
        flash(f"Your account has been created! You are now able to vote with random movies, after the result shows up on "
              f"the right or on the bottom if you use the phone, please complete the interview with high entropy "
              f"movies. Thank you!\n 账户创建成功，请给以下电影投票，下面电影时代可能比较久远，你可以根据电影的黄色标签来判断你是否喜欢这部"
              f"电影或者点进电影名字查阅电影信息。在右边结果栏出现数据以后请选择Vote(Entropy)再投票，待两个结果栏都有结果代表已经生成用户画像，"
              f"你可以继续投票以便让我们获取更多数据，谢谢你的参与！", 'success')
        login_user(user, remember=False)
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        else:
            return redirect(url_for('random_vote'))
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
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@app.route("/rating/<int:rating_id>/delete", methods=['POST'])
@login_required
def delete_rating(rating_id):
    rating = Rating.query.get_or_404(rating_id)
    if rating.author != current_user:
        abort(403)
    db.session.delete(rating)
    db.session.commit()
    flash('Vote has been deleted', 'success')
    update_demography(current_user)
    return redirect(url_for('result'))


@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.username != 'test':
        abort(403)
    LR_demo = []
    for user in User.query.all():
        if user.demographics.count() == 2:
            d = get_LR_demo([(rate.film_id, rate.score) for rate in user.ratings if rate.question_type == 1], user)
            LR_demo.append([user.gender, d.male, user.age, d.age1, user.occupation, d.occup1])
            d = get_demo([(rate.film_id, rate.score) for rate in user.ratings if rate.question_type == 0], user)
            LR_demo.append([user.gender, d.male, user.age, d.age1, user.occupation, d.occup1])
    return render_template('admin.html', title='admin', User=User, LR_demo=LR_demo)