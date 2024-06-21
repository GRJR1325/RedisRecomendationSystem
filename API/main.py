from fastapi import FastAPI, HTTPException, status
import pandas as pd
from pathlib import Path
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

def searchAndRecomendation(sceneTitle):
    # Obtener la ruta del directorio actual
    current_dir = Path(__file__).parent

    # Construir la ruta completa al archivo
    file_path = current_dir.parent / 'content' / 'DatasetEscenas.csv'

    # Cargar el dataset
    try:
        scenes_data = pd.read_csv(file_path)
        # Imprimir las primeras 5 filas del dataframe
        print(scenes_data.head())

        scenes_data.shape
        selected_features = ['id','genres','keywords','title','views','likes','director']

        # replacing the null valuess with null string
        for feature in selected_features:
            scenes_data[feature] = scenes_data[feature].fillna('')

        # combining all the selected features
        combined_features = scenes_data['genres']+' '+ scenes_data['keywords']+'  '+ scenes_data['title']+' '+ scenes_data['director']

        vectorizer = TfidfVectorizer()

        feature_vectors = vectorizer.fit_transform(combined_features)

        # getting the similarity scores using cosine similarity
        similarity = cosine_similarity(feature_vectors)

        # getting the movie name from the API
        movie_name = sceneTitle 

        # creating a list with all the movie names given in the dataset
        list_of_all_titles = scenes_data['title'].tolist()

        # finding the close match for the movie name given by the user
        find_close_match = difflib.get_close_matches(movie_name, list_of_all_titles)    

        close_match = find_close_match[0]

        index_of_the_scenes = scenes_data[scenes_data.title == close_match]['index'].values[0]

        # getting a list of similar movies
        similarity_score = list(enumerate(similarity[index_of_the_scenes]))

        sorted_similar_scenes = sorted(similarity_score, key=lambda x: x[1], reverse=True)

        recommendations = []
        i = 1

        for movie in sorted_similar_scenes:
            index = movie[0]
            title_from_index = scenes_data[scenes_data.index == index]['title'].values[0]
            if i < 30:
                recommendations.append(title_from_index)
                i += 1

        return recommendations

    except FileNotFoundError:
        print(f"El archivo {file_path} no se encuentra.")
        return []
    except Exception as error:
        print(f'ERROR: {error.args}')
        return []


@app.get(
    "/recomendar/{sceneTitle}",
    summary="Obtener recomendaciones",
    description="API para obtener recomendaciones"
)
async def get_title(sceneTitle: str):
    try:
        if not sceneTitle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se detecto un titulo ingresado"
            )

        print(f'Titulo elegido: {sceneTitle}')
        recommendations = searchAndRecomendation(sceneTitle)

        if not recommendations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontraron recomendaciones"
            )

        return {"recommendations": recommendations}

    except HTTPException as http_err:
        raise http_err
    except Exception as error:
        print(f'ERROR: {error.args}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ERROR INESPERADO"
        )