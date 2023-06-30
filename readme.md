<p align=left><img src=src\logo.png width="35%">

# **Proyecto Individual 1:** Machine Learning Operations (MLOps)
### by Nilda Pérez Otero

Hola! Este es mi primer proyecto individual de Labs de la carrera de Data Sciende de Soy Henry. Bienvenidos! 

# Proyecto de Recomendación de Películas

En este proyecto se asume el rol de _Data Engineer_. Se partió de cero, con un conjunto de datos anidados y sin transformar hasta llegar a un sistema que recomiende películas a los usuarios basándose en películas similares. Para ello se siguieron varias etapas que se describen en este `readme.md`.

## 1. Proceso de [ETL](<notebooks/PI01 ETL.ipynb>)

ETL (por las siglas en inglés de Extraer, Transformar y Cargar) es el proceso utilizado en la gestión de datos. Es un enfoque común para recopilar, transformar y cargar datos desde diferentes fuentes en un sistema de destino, como un almacén de datos o una base de datos.

### Extraer 
Se consideraron los dos archivos `.csv` provistos: [`movies_dataset.csv` y `credits.csv`](https://drive.google.com/drive/folders/1hW0XAeLp07ka2b1dLNk1LP1Hej0H0t0i?usp=sharing)

### Transformar

Se realizaron las transformaciones [solicitadas](https://github.com/HX-PRomero/PI_ML_OPS#readme):
+ Se desanidaron los campos que tienen un diccionario o una lista como valores en cada fila.
+ Se rellenaron con **0** los valores nulos de los campos _revenue_ y _budget_.
+ Se eliminaron las filas con valores nulos en el campo release_date.
+ Al campo _release_date_ se le dió el formato **AAAA-mm-dd**.
+ Se crearon las columnas 'release_year' que contiene el año de la fecha de estreno y 'return' (retorno de inversión) que contien el cociente entre _revenue_ y _budget_.
+ Se eliminaron las columnas 'video', 'imdb_id' ,'adult', 'original_title', 'poster_path' y 'homepage'.

Otras transformaciones:
+ Se solucionó un problema de celdas desfasadas.
+ Se eliminaron duplicados.
+ Los campos vacíos de las columnas de tipo texto se completaron con la cadena **'sin dato'**.
+ De la columna 'crew' del credits.csv se extrajo solo el Director, para cumplir por los solicitado en los _endpoints_
+ Se combinaron los dos _dataframes_ en un solo.

### Cargar
 El _dataframe_ combincado se guardó como [`movies_credits_limpio.csv`](https://github.com/nilperez/movie-recommender/blob/main/movies_credits_limpio.csv) para ser consumido en las próximas etapas.

## 2. Proceso de [EDA](<notebooks/PI01 EDA.ipynb>)

El Análisis Exploratorio de Datos (EDA, por sus siglas en inglés) es un proceso de investigación y exploración de los datos para descubrir patrones, tendencias y características significativas que ayuden a comprender mejor los datos y guiar el análisis posterior.

En esta etapa se hizo uso de las siguientes técnicas comunes del EDA:

+ Nubes de palabras
+ Gráficos (histogramas, _pie chart_, dispersión)
+ Identificación de valores atípicos
+ Análisis de distribuciones de variables
+ Matrices de correlación.

## 3. Sistema de [recomendación de películas](<notebooks/PI01 ML.ipynb>)

Se utilizaron técnicas de procesamiento de texto y similitud del coseno para recomendar 5 películas similares a la película ingresada por el usuario.
A continuación, se explica cómo funciona la recomendación paso a paso:

+ Se seleccionan las columnas del que contienen la información relevante para el sistema de recomendación.
+ Se crea una  que se utilizará para convertir el texto de las columnas seleccionadas en una matriz de términos.
+ Las columnas seleccionadas se concatenan en un solo texto para cada película. 
+ Se utiliza instancia del objeto `CountVectorizer` de la biblioteca _scikit-learn_ en los textos concatenados para crear una matriz de términos.
+ Para encontrar películas similares, se utiliza la similitud del coseno. Se calcula la similitud del coseno entre el vector de términos de la película ingrsada y el vector de términos de todas las demás películas en la matriz. Esto da como resultado un arreglo de similitudes.
+ Finalmente, se seleccionan las 5 películas más similares de la lista ordenada de similitudes y se devuelve una lista con los títulos de éstas 5 películas.

## 4. Desarrollo API

Se disponibilizaron los datos usando el framework FastAPI. Las consultas disponibles son las siguientes:

+ [cantidad_filmaciones_mes(mes)](https://ml-ops-movie-recommender.onrender.com/docs#/default/cantidad_filmaciones_mes_cantidad_filmaciones_mes__mes__get): Se ingresa un mes en idioma Español, devuelve la cantidad de películas que fueron estrenadas históricamente en el mes consultado.
+ [cantidad_filmaciones_dia(dia)](https://ml-ops-movie-recommender.onrender.com/docs#/default/cantidad_filmaciones_dia_cantidad_filmaciones_dia__dia__get): Se ingresa un día en idioma Español. Devuelve la cantidad de películas que fueron estrenadas históricamente en el día consultado.
+ [score_titulo(titulo_de_la_filmación)](https://ml-ops-movie-recommender.onrender.com/docs#/default/score_titulo_score_titulo__titulo__get): Se ingresa el título de una filmación y da como respuesta el título, el año de estreno y el score.
+ [votos_titulo(titulo_de_la_filmación)](https://ml-ops-movie-recommender.onrender.com/docs#/default/votos_titulo_votos_titulo__titulo__get): Se ingresa el título de una filmación y si esta cuenta al menos con 2000 valoraciones, da como respuesta el título, la cantidad de votos y el valor promedio de las votaciones, caso contrario, da un mensaje avisando que no cumple esta condición.
+ [get_actor(nombre_actor)](https://ml-ops-movie-recommender.onrender.com/docs#/default/get_actor_get_actor__nombre_actor__get): Se ingresa el nombre de un actor que se encuentre dentro del dataset y devuelve su éxito medido a través del retorno. Además devuelve la cantidad de películas que en las que ha participado y el promedio de retorno.
+ [get_director(nombre_director)](https://ml-ops-movie-recommender.onrender.com/docs#/default/get_director_get_director__nombre_director__get): Se ingresa el nombre de un director que se encuentre dentro del dataset debiendo devolver su éxito medido a través del retorno. Además devuenve el nombre de cada película que dirigió con la fecha de lanzamiento, retorno individual, costo y ganancia.
+ [recomendacion(titulo)](https://ml-ops-movie-recommender.onrender.com/docs#/default/recomendacion_recomendacion__titulo__get): Se ingresa el nombre de una película y devuelve como resultado una lista con las 5 películas más similares.
## 5. Deployment
El despliegue de la API se hizo mediante [Render](https://render.com/).

# Enlaces

- [Repositorio del proyecto en GitHub](https://github.com/nilperez/movie-recommender/)
- [Documentación de la API](https://ml-ops-movie-recommender.onrender.com/docs)
- [Video]()

Si tienes alguna pregunta adicional, no dudes en [contactarme](nilperez@gmail.com). ¡Gracias por tu interés en mi proyecto de Recomendación de Películas!
