from tables import User_Preference
genre_map = {28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Science Fiction", 10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"}
genre_names = ["Action", "Adventure", "Animation", "Comedy", "Crime", "Drama", "Family", "Fantasy", "History", "Horror", "Music", "Mystery", "Romance", "Science Fiction", "TV Movie", "Thriller", "War", "Western"]

def vectorise_movie(movie):
    genre_ids = movie["genre_ids"]
    movie_genres = []

    for i in genre_ids:
        if i in genre_map:
            genre_name = genre_map[i]
            movie_genres.append(genre_name)
    movie_vector = []

    for i in genre_names:
        if i in movie_genres:
            movie_vector.append(1)
        else:
            movie_vector.append(0)
    return movie_vector

def vectorise_user(user):
    
    user_vector = []
    for genre in genre_names:
        preference = User_Preference.query.filter_by(user_id=user.id, genre=genre).first()
        score = preference.score
        user_vector.append(score)
    return user_vector