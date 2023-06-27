import pandas as pd
import ast
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel

app = FastAPI()

# Leer el archivo CSV y crear el DataFrame 
df = pd.read_csv('movies_credits_limpio.csv', parse_dates=['release_date'])

list_columns = ['genres', 'production_companies', 'production_countries', 'spoken_languages', 'cast']
df[list_columns] = df[list_columns].applymap(lambda x: list(ast.literal_eval(x)))

# Preparar entorno para la recomendación
# Combinar las columnas "overview", "genres", "cast" y "director" en una sola columna
df['combined'] = df['overview'] + ' ' + df['genres'].apply(lambda x: ' '.join(x))

# Crear una instancia de TfidfVectorizer para vectorizar el texto combinado
tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))

# Aplicar TF-IDF al texto combinado
tfidf_matrix = tfidf.fit_transform(df['combined'])

# Menú de enlaces a cada endpoint
@app.get('/', response_class=HTMLResponse)
def menu():
    enlaces = [
        {
            'endpoint': '/cantidad_filmaciones_mes/enero',
            'nombre': 'Cantidad de Filmaciones por Mes',
            'descripcion': {
                'en': 'Function that returns the number of movies historically released in the specified month.',
                'es': 'Función que retorna la cantidad de películas que se estrenaron históricamente en el mes indicado.'
            }
        },
        {
            'endpoint': '/cantidad_filmaciones_dia/lunes',
            'nombre': 'Cantidad de Filmaciones por Día',
            'descripcion': {
                'en': 'Function that returns the number of movies historically released on the specified day.',
                'es': 'Función que retorna la cantidad de películas que se estrenaron históricamente en el día indicado.'
            }
        },
        {
            'endpoint': '/score_titulo/Titanic',
            'nombre': 'Score de Título',
            'descripcion': {
                'en': 'Function that returns the release year and score of the specified movie.',
                'es': 'Función que retorna año de estreno y score de la filmación indicada.'
            }
        },
        {
            'endpoint': '/votos_titulo/Titanic',
            'nombre': 'Votos de Título',
            'descripcion': {
                'en': 'Function that returns the release year, number of votes, and average rating of the specified movie, only if it has more than 2000 ratings.',
                'es': 'Función que retorna año de estreno, cantidad de votos y valor promedio de las votaciones de la filmación indicada, solo en caso que haya tenido más de 2000 valoraciones.'
            }
        },
        {
            'endpoint': '/get_actor/Leonardo DiCaprio',
            'nombre': 'Información de Actor',
            'descripcion': {
                'en': 'Function that returns the number of movies the actor has participated in, the success measured through return, and the average return.',
                'es': 'Función que retorna la cantidad de películas en las que ha participado el actor, el éxito medido a través del retorno y el promedio de retorno.'
            }
        },
        {
            'endpoint': '/get_director/James Cameron',
            'nombre': 'Información de Director',
            'descripcion': {
                'en': 'Function that returns the success measured through return of the director. It also returns the name of each movie with release date, individual return, budget, and revenue.',
                'es': 'Función que retorna el éxito medido a través retorno del director. Además, devuelve el nombre de cada película con fecha de lanzamiento, retorno individual, costo y ganancia.'
            }
        },
        {
            'endpoint': '/recomendacion/Titanic',
            'nombre': 'Recomendación',
            'descripcion': {
                'en': 'A function that returns a list of 5 movies similar to the one entered.',
                'es': 'Función que retorna una lista de 5 películas similares a la ingresada.'
            }
        }
    ]

    menu_html = '<h1>Movie recommender API</h1>'
    menu_html += '<ul>'
    for enlace in enlaces:
        menu_html += f'<li><a href="{enlace["endpoint"]}">{enlace["nombre"]}</a>'
        if 'descripcion' in enlace:
            menu_html += f'<br><span>{enlace["descripcion"]["en"]}</span><br><span style="font-size: 12px;">{enlace["descripcion"]["es"]}</span>'
        menu_html += '</li>'
    menu_html += '</ul>'

    menu_html += '<p style="font-size: 14px;"><strong>Note:</strong> month and day should be entered in Spanish.</p>'
    menu_html += '<p style="font-size: 12px;"><strong>Nota:</strong> mes y día se deben ingresar en español.</p>'

    return menu_html


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

@app.get("/recomendacion/{titulo}")
def recomendacioin(titulo: str):
    # Obtener los índices de todas las películas con el título dado
    indices = df[df['title'] == titulo].index

    # Verificar si hay películas duplicadas con el mismo título
    if len(indices) > 1:
        # Seleccionar la película con el mayor vote_average
        indice = df.loc[indices, 'vote_average'].idxmax()
    else:
        # Tomar el primer índice encontrado
        indice = indices[0] if len(indices) > 0 else None

    if indice is not None:
        # Calcular la matriz de similitud del coseno
        similitud_cos = linear_kernel(tfidf_matrix[indice], tfidf_matrix).flatten()

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
        return {"error": f"No se encontró ninguna película con el título '{titulo}'."}







