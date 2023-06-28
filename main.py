import pandas as pd
import ast
from fastapi import FastAPI
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Leer el archivo CSV y crear el DataFrame 
df = pd.read_csv('movies_credits_limpio.csv', parse_dates=['release_date'])

# Endpoint para obtener la cantidad de filmaciones por mes
@app.get('/cantidad_filmaciones_mes/{mes}')
def cantidad_filmaciones_mes(mes: str):
    # Diccionario para mapear los nombres de los meses en español a sus números correspondientes
    meses = {
        'enero': 1,
        'febrero': 2,
        'marzo': 3,
        'abril': 4,
        'mayo': 5,
        'junio': 6,
        'julio': 7,
        'agosto': 8,
        'septiembre': 9,
        'octubre': 10,
        'noviembre': 11,
        'diciembre': 12
    }
    # Obtener el número del mes correspondiente al nombre en español
    numero_mes = meses.get(mes.lower())
    if numero_mes:
        # Filtrar el DataFrame por el mes correspondiente en release_date
        df_mes = df[df['release_date'].dt.month == numero_mes]
        # Obtener la cantidad de películas en el mes consultado
        cantidad = len(df_mes)
        # Crear el diccionario de salida
        respuesta = {'mes': mes, 'cantidad': cantidad}
        # Retornar la respuesta
        return respuesta
    else:
        return {'error': f"No se encontró el mes '{mes}' en el dataset"}

# Endpoint para obtener la cantidad de filmaciones por día
@app.get('/cantidad_filmaciones_dia/{dia}')
def cantidad_filmaciones_dia(dia: str):
    # Diccionario para mapear los nombres de los días de la semana en español a sus números correspondientes
    dia_semana = {
        'lunes': 0,
        'martes': 1,
        'miércoles': 2,
        'miercoles': 2,  # Añadido para aceptar "miercoles" sin acento
        'jueves': 3,
        'viernes': 4,
        'sábado': 5,
        'sabado': 5,  # Añadido para aceptar "sabado" sin acento
        'domingo': 6
    }
    dia_lower = dia.lower()
    if dia_lower in dia_semana:
        # Filtrar el DataFrame por el día de la semana correspondiente en release_date
        df_dia = df[df['release_date'].dt.dayofweek == dia_semana[dia_lower]]
        # Obtener la cantidad de películas en el día de la semana consultado
        cantidad = len(df_dia)
        # Crear el diccionario de salida
        respuesta = {'dia': dia, 'cantidad': cantidad}
        # Retornar la respuesta
        return respuesta
    else:
        return {'error': f"No se encontró el día '{dia}' en el dataset"}

# Endpoint para obtener el score de una película por título
@app.get('/score_titulo/{titulo}')
def score_titulo(titulo: str):
    # Filtrar la película por título
    pelicula = df[df['title'].str.contains(titulo, case=False)]    
    if pelicula.empty:
        # No se encontró ninguna película que coincida con el título buscado
        return {'error': f"No se encontró una película con el título '{titulo}'"}   
    # Obtener la primera película que coincide con el título buscado
    pelicula = pelicula.iloc[0]
    # Obtener los datos de la película y convertir los valores numéricos a tipos de datos nativos
    titulo_pelicula = str(pelicula['title'])
    anio_estreno = int(pelicula['release_year'])
    score = float(pelicula['vote_average'])
    # Crear el diccionario de salida
    respuesta = {'titulo': titulo_pelicula, 'anio': anio_estreno, 'popularidad': score}
    # Retornar la respuesta
    return respuesta

# Endpoint para obtener los votos de una película por título
@app.get('/votos_titulo/{titulo}')
def votos_titulo(titulo: str):
    # Filtrar la película por título
    pelicula = df[df['title'].str.contains(titulo, case=False)].iloc[0]    
    if pelicula.empty:
        # No se encontró ninguna película que coincida con el título buscado
        return {'error': f"No se encontró una película con el título '{titulo}'"}
    # Obtener los datos de la película
    titulo_pelicula = str(pelicula['title'])
    anio_estreno = int(pelicula['release_year'])
    votos = int(pelicula['vote_count'])
    promedio_votos = pelicula['vote_average']
    # Verificar la cantidad de valoraciones
    if votos < 2000:
        return {'error': f"La película '{titulo_pelicula}' no cumple con la cantidad mínima de valoraciones (2000)"}
    # Crear el diccionario de salida
    respuesta = {'titulo': titulo_pelicula, 'anio': anio_estreno, 'votos_totales': votos, 'votos_promedio': promedio_votos}
    # Retornar la respuesta
    return respuesta

# Endpoint para obtener información de un actor
@app.get('/get_actor/{nombre_actor}')
def get_actor(nombre_actor: str):
    # Separar el nombre y apellido del actor
    nombre, apellido = nombre_actor.split(" ", 1) if " " in nombre_actor else (nombre_actor, "")
    # Verificar si se proporcionó solo el nombre sin apellido
    if apellido == "":
        return {'error': "Debe proporcionar el nombre y el apellido del actor"}
    # Filtrar las películas en las que ha participado el actor
    peliculas_actor = df[df['cast'].apply(lambda x: nombre.lower() in x.lower() and apellido.lower() in x.lower())]
    if peliculas_actor.empty:
        # No se encontraron películas en las que el actor haya participado
        return {'error': f"No se encontraron películas en las que el actor '{nombre_actor}' haya participado"}
    # Obtener los datos de interés
    cantidad_filmaciones = len(peliculas_actor)
    retorno_total = round(peliculas_actor['return'].sum(), 2)
    retorno_promedio = round(peliculas_actor['return'].mean(), 2)
    # Crear el diccionario de salida
    respuesta = {'actor': nombre_actor, 'cantidad_filmaciones': cantidad_filmaciones, 'retorno_total': retorno_total, 'retorno_promedio': retorno_promedio}
    # Retornar la respuesta
    return respuesta

# Endpoint para obtener información de un director
@app.get('/get_director/{nombre_director}')
def get_director(nombre_director: str):
    # Filtrar las películas dirigidas por el director
    peliculas_director = df[df['director'] == nombre_director]
    # Verificar si se encontraron películas para el director especificado
    if peliculas_director.empty:
        return {'error': f"No se encontraron películas dirigidas por '{nombre_director}'"}
    # Obtener los datos de interés de cada película
    peliculas_info = []
    for _, pelicula in peliculas_director.iterrows():
        pelicula_info = {
            'titulo': pelicula['title'],
            'anio': pelicula['release_year'],
            'retorno_pelicula': pelicula['return'],
            'budget_pelicula': pelicula['budget'],
            'revenue_pelicula': pelicula['revenue']
        }
        peliculas_info.append(pelicula_info)
    # Calcular el retorno total del director
    retorno_total_director = round(peliculas_director['return'].sum(), 2)
    # Crear el diccionario de salida
    respuesta = {
        'director': nombre_director,
        'retorno_total_director': retorno_total_director,
        'peliculas': peliculas_info
    }
    return respuesta

# Preparar data para la recomendación
# Descargar las stopwords en inglés si no están disponibles
nltk.download('stopwords')
# Obtener las stopwords en inglés
stop_words = set(stopwords.words('english'))
stop_words.update(',',';','!','?','.','(',')','$','#','+',':','...',' ','')

# Función para limpiar el texto
def clean_text(text):
    # Tokenizar el texto en palabras individuales
    tokens = text.split()
    # Eliminar las stopwords y los signos de puntuación
    tokens_cleaned = [token.lower() for token in tokens if token.lower() not in stop_words]
    # Unir las palabras limpias en un solo texto nuevamente
    text_cleaned = ' '.join(tokens_cleaned)
    return text_cleaned

@app.get("/recomendacion/{titulo}")
def recomendacioin(titulo: str):
    # Seleccionar las columnas relevantes para la matriz de términos
    df1 = df[['genres', 'overview', 'popularity', 'title', 'vote_average', 'release_year', 'cast', 'director']]
    # Convertir las columnas 'genres' y 'cast' en listas de Python
    list_columns = ['genres', 'cast']
    df1.loc[:, list_columns] = df1.loc[:, list_columns].apply(lambda x: x.apply(ast.literal_eval).apply(tuple))
    # Crear una instancia del vectorizador
    vectorizer = CountVectorizer()
    # Concatenar las columnas 'overview', 'genres', 'cast' y 'director' en un solo texto
    textos_concatenados = df1['overview'] + ' ' + df1['genres'].apply(lambda x: ' '.join(x)) + ' ' + df1['cast'].apply(lambda x: ' '.join(x)) + ' ' + df1['director']
    # Crear la matriz de términos
    terminos_mat = vectorizer.fit_transform(textos_concatenados)
   
    indices = df1[df1['title'] == titulo].index
    # Verificar si hay múltiples películas con el mismo título
    if len(indices) > 1:
        # Se encontraron múltiples películas con el mismo título
        return {"error": f"Se encontraron múltiples películas con el título '{titulo}'."}
    elif len(indices) == 1:
        # Seleccionar la película con el mayor vote_average
        indice = indices[0]
        # Obtener el vector de características de la película seleccionada
        vector_pelicula = terminos_mat[indice]
        # Calcular la similitud del coseno entre la película seleccionada y todas las demás películas
        similitud_cos = cosine_similarity(vector_pelicula, terminos_mat)[0]
        # Obtener las puntuaciones de similitud para todas las películas
        scores_similares = list(enumerate(similitud_cos))
        # Ordenar las películas por puntuación de similitud en orden descendente
        scores_similares = sorted(scores_similares, key=lambda x: x[1], reverse=True)
        # Obtener los índices de las 5 películas más similares (excluyendo la película de entrada)
        indices_movie = [i[0] for i in scores_similares[1:6]]
        # Obtener los títulos de las películas más similares
        lista_recomendada = df['title'].iloc[indices_movie].tolist()
        # Crear el diccionario de salida
        respuesta = {
            'lista_recomendada': lista_recomendada
        }
        # Retornar la respuesta
        return respuesta
    else:
        # No se encontró ninguna película con el título dado
        return {"error": f"No se encontró ninguna película con el título '{titulo}'."}