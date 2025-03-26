import os
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Update movie image field using images from a folder"

    def handle(self, *args, **kwargs):
        # Ruta donde están almacenadas las imágenes ya generadas
        images_folder = 'media/movie/images/'
        updated_count = 0

        if not os.path.exists(images_folder):
            self.stderr.write(f"Image folder '{images_folder}' does not exist.")
            return

        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies")

        for movie in movies:
            image_filename = f"m_{movie.title}.png"
            image_path_full = os.path.join(images_folder, image_filename)

            if os.path.exists(image_path_full):
                movie.image = os.path.join('movie/images', image_filename)
                movie.save()
                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Updated image for: {movie.title}"))
            else:
                self.stderr.write(f"Image not found for: {movie.title} -> {image_filename}")

        self.stdout.write(self.style.SUCCESS(f"Finished updating {updated_count} movies with images."))
