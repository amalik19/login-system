import requests

headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI1YmM0NGRhMmJlOGQzZWMyMThlODg3Njc0ZWRiYjU2MiIsIm5iZiI6MTc2MzExMTAyNS44MTYsInN1YiI6IjY5MTZmMDcxYWQ5ZTc2NmY1MzRjYTQzMCIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.pvs_TIXaz9_Sf27sl0h90s7bOJykpovn0mOWQpHtYyA"
    }

def get_popular_movies():
    url = "https://api.themoviedb.org/3/movie/popular?language=en-US&page=1"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        print("TMDb API Error:", response.status_code)
        return []