from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mymovielist.db'
db = SQLAlchemy(app)

# --- Таблица 1: Фильмы ---
class Movie(db.Model):
    __tablename__ = 'movies'
    
    # Меняем movie_id просто на id, чтобы оно совпадало с ForeignKey
    id = db.Column(db.Integer, primary_key=True) 
    
    # Остальные твои колонки (тут я оставил твой вариант с префиксами)
    movie_title = db.Column(db.String(100), nullable=False)
    movie_description = db.Column(db.Text, nullable=True)
    release_year = db.Column(db.Integer, nullable=True)
    director = db.Column(db.String(100), nullable=True)
    poster = db.Column(db.String(255), nullable=True)
    backdrop = db.Column(db.String(255), nullable=True)
    
    reviews = db.relationship('Review', backref='movie', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Movie {self.id}: {self.movie_title}>'

# --- Таблица 2: Твои отзывы ---
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    
    # Теперь он будет успешно ссылаться на колонку id в таблице movies
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    
    rating = db.Column(db.Integer, nullable=True)
    review_text = db.Column(db.Text, nullable=True)
    time_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review for Movie ID {self.movie_id}>'


@app.route('/')
@app.route("/home")
def index():
    return render_template("index.html")


@app.route('/movies')
def movies():
    movies = Movie.query.order_by(Movie.release_year).all()
    return render_template('movies.html',movies = movies)



# methods=['GET', 'POST'] означает, что эта страница может и показывать форму (GET), и принимать из нее данные (POST)
@app.route('/add', methods=['GET', 'POST'])
def add_movie():
    if request.method == 'POST':
        # 1. Забираем данные, которые ты ввел в HTML-форму
        title = request.form['title']
        release_year = request.form['release_year']
        director = request.form['director']
        movie_description = request.form['movie_description']
        
        # Получаем файл постера
        file = request.files.get('movie_poster')
    
        if file:
            filename = file.filename
            file.save(f"static/posters/{filename}") # Сохраняем файл в папку
        else:
            filename = None


        # 2. Создаем фильм и сохраняем, чтобы получить его ID
        new_movie = Movie(
            movie_title=title,
            release_year=release_year,
            director=director,  # <-- ВАЖНО
            poster=filename,          # <-- тоже исправил
            movie_description=movie_description
)
        
        try:
            db.session.add(new_movie)
            db.session.commit() 
            return redirect(url_for('index'))
        except:
            return 'Error happend'

    # Если мы просто зашли на страницу (GET), показываем пустую форму
    return render_template('add.html')
    



if __name__ == "__main__":
    app.run(debug=True)