from dotenv import load_dotenv, find_dotenv
import json
import os
from openai import OpenAI
#from openai.embeddings_utils import get_embedding, cosine_similarity
import numpy as np

_ = load_dotenv('openAI.env')
client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get('openai_api_key'),
)

with open('movie_descriptions_embeddings.json', 'r') as file:
    file_content = file.read()
    movies = json.loads(file_content)

#Esta función devuelve una representación numérica (embedding) de un texto, en este caso
#la descripción de las películas
    
def get_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

#Si se tuviera un prompt por ejemplo: Película de la segunda guerra mundial, podríamos generar el embedding del prompt y comparar contra 
#los embeddings de cada una de las películas de la base de datos. La película con la similitud más alta al prompt sería la película
#recomendada.

req = "película de un pianista"
emb = get_embedding(req)

sim = []
for i in range(len(movies)):
  sim.append(cosine_similarity(emb,movies[i]['embedding']))
sim = np.array(sim)
idx = np.argmax(sim)
print(movies[idx]['title'])


