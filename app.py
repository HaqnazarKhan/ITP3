from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mymovielist.db'
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movies'
    

    id = db.Column(db.Integer, primary_key=True) 
    

    movie_title = db.Column(db.String(100), nullable=False)
    movie_description = db.Column(db.Text, nullable=True)
    release_year = db.Column(db.Integer, nullable=True)
    director = db.Column(db.String(100), nullable=True)
    poster = db.Column(db.String(255), nullable=True)
    backdrop = db.Column(db.String(255), nullable=True)
    
    reviews = db.relationship('Review', backref='movie', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Movie {self.id}: {self.movie_title}>'


class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    

    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    
    rating = db.Column(db.Integer, nullable=True)
    review_text = db.Column(db.Text, nullable=True)
    time_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review for Movie ID {self.movie_id}>'


@app.route('/')
@app.route("/home")
def index():

    all_movies = Movie.query.order_by(Movie.id.desc()).all()

    return render_template("index.html", movies=all_movies)




@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        title = request.form['title']
        release_year = request.form['release_year']
        director = request.form['director']


        file = request.files.get('movie_poster')
        poster_filename = None 


        if file and file.filename != '':
            poster_filename = file.filename

            file.save(os.path.join('static', 'pictures', poster_filename))


        new_movie = Movie(
            movie_title=title, 
            release_year=release_year, 
            director=director, 
            poster=poster_filename
        )
        
        db.session.add(new_movie)
        db.session.commit() 

        return redirect(url_for('movie_detail', movie_id=new_movie.id))

    return render_template('add_movie.html')


@app.route('/movie/<int:movie_id>', methods=['GET', 'POST'])
def movie_detail(movie_id):

    movie = Movie.query.get_or_404(movie_id)


    if request.method == 'POST':
        rating = request.form['rating']
        review_text = request.form['review_text']


        new_review = Review(movie_id=movie.id, rating=rating, review_text=review_text)
        db.session.add(new_review)
        db.session.commit()


        return redirect(url_for('movie_detail', movie_id=movie.id))


    return render_template('movie.html', movie=movie)

@app.route('/movie/<int:movie_id>/delete', methods = ['POST'])
def delete_movie(movie_id):
    movie_to_delete = Movie.query.get_or_404(movie_id)
    
    try:
        db.session.delete(movie_to_delete)
        db.session.commit()

        return redirect(url_for('index'))
    except:
        return "Error"


@app.route('/review/<int:review_id>/delete', methods = ['POST'])
def delete_review(review_id):
    review_to_delete = Review.query.get_or_404(review_id)
    movie_id= review_to_delete.movie_id
    
    try:
        db.session.delete(review_to_delete)
        db.session.commit()
        
        return redirect(url_for('movie_detail', movie_id = movie_id))
    except:
        return "deleting error"
    


    
@app.route('/movie/<int:movie_id>/update', methods=['GET', 'POST'])
def update_movie(movie_id):
    
    movie = Movie.query.get_or_404(movie_id)
    
    if request.method == 'POST':
        
        movie.movie_title = request.form['title']
        movie.release_year = request.form['release_year']
        movie.director = request.form['director']


        file = request.files.get('movie_poster')
        

        if file and file.filename != '':
            poster_filename = file.filename
            file.save(os.path.join('static', 'pictures', poster_filename))
            movie.poster = poster_filename 

        db.session.commit() 

        return redirect(url_for('movie_detail', movie_id=movie.id))

    return render_template('update_movie.html', movie= movie)


@app.route('/review/<int:review_id>/update', methods = ['GET', 'POST'])
def update_review(review_id):
        
    review = Review.query.get_or_404(review_id)
    movie_id = review.movie_id
    

    if request.method == 'POST':
        review.rating = request.form['rating']
        review.review_text = request.form['review_text']
        

        db.session.commit()


        return redirect(url_for('movie_detail', movie_id=movie_id))


    return render_template('update_review.html', review=review)


if __name__ == "__main__":
    app.run(debug=True)