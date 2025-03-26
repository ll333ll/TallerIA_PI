import numpy as np
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Print the first values of embeddings stored in the database"

    def handle(self, *args, **kwargs):
        for movie in Movie.objects.all():
            if movie.emb:
                emb_array = np.frombuffer(movie.emb, dtype=np.float32)
                self.stdout.write(f"{movie.title}: {emb_array[:5]}...")
            else:
                self.stdout.write(f"{movie.title}: ❌ No embedding stored")
