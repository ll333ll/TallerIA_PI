from django.shortcuts import render
from django.http import HttpResponse
from .models import Movie
import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64
import os
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI

# Cargar API Key de OpenAI
load_dotenv('openAI.env')
client = OpenAI(api_key=os.environ.get('openai_apikey'))

def home(request):
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm':searchTerm, 'movies':movies})

def about(request):
    return render(request, 'about.html')

def signup(request):
    email = request.GET.get('email') 
    return render(request, 'signup.html', {'email':email})

def statistics_view0(request):
    matplotlib.use('Agg')
    all_movies = Movie.objects.all()
    movie_counts_by_year = {}
    for movie in all_movies:
        year = movie.year if movie.year else "None"
        movie_counts_by_year[year] = movie_counts_by_year.get(year, 0) + 1

    bar_width = 0.5
    bar_positions = range(len(movie_counts_by_year))
    plt.bar(bar_positions, movie_counts_by_year.values(), width=bar_width, align='center')
    plt.title('Movies per year')
    plt.xlabel('Year')
    plt.ylabel('Number of movies')
    plt.xticks(bar_positions, movie_counts_by_year.keys(), rotation=90)
    plt.subplots_adjust(bottom=0.3)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png).decode('utf-8')
    return render(request, 'statistics.html', {'graphic': graphic})

def statistics_view(request):
    matplotlib.use('Agg')
    all_movies = Movie.objects.all()
    movie_counts_by_year = {}
    for movie in all_movies:
        year = movie.year if movie.year else "None"
        movie_counts_by_year[year] = movie_counts_by_year.get(year, 0) + 1

    year_graphic = generate_bar_chart(movie_counts_by_year, 'Year', 'Number of movies')

    movie_counts_by_genre = {}
    for movie in all_movies:
        genre = movie.genre.split(',')[0].strip() if movie.genre else "None"
        movie_counts_by_genre[genre] = movie_counts_by_genre.get(genre, 0) + 1

    genre_graphic = generate_bar_chart(movie_counts_by_genre, 'Genre', 'Number of movies')

    return render(request, 'statistics.html', {
        'year_graphic': year_graphic,
        'genre_graphic': genre_graphic
    })

def generate_bar_chart(data, xlabel, ylabel):
    keys = [str(key) for key in data.keys()]
    plt.bar(keys, data.values())
    plt.title('Movies Distribution')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=90)
    plt.tight_layout()
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    image_png = buffer.getvalue()
    buffer.close()
    return base64.b64encode(image_png).decode('utf-8')

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def recommend_movie(request):
    recommended = None
    similarity_score = 0

    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        response = client.embeddings.create(
            input=[prompt],
            model="text-embedding-3-small"
        )
        prompt_emb = np.array(response.data[0].embedding, dtype=np.float32)

        max_sim = -1
        best_match = None

        for movie in Movie.objects.all():
            movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
            sim = cosine_similarity(prompt_emb, movie_emb)
            if sim > max_sim:
                max_sim = sim
                best_match = movie

        recommended = best_match
        similarity_score = max_sim

    return render(request, 'recommend.html', {
        'recommended': recommended,
        'similarity': round(similarity_score, 4),
    })
