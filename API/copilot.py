from fastapi import FastAPI, HTTPException, status
import requests
import json

app = FastAPI()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "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"


@app.get(
    "/copilot/",
    summary="Obtener recomendaciones para keywords",
    description="API para obtener recomendaciones de keywords basandose en el titulo de la escena y su descripcion",
)
async def get_description_and_title(sceneTitle: str, description: str):
    """
    Obtencion del titulo de la escena y de la descripcion
    """
    if not sceneTitle or not description:
        raise HTTPException(
            status_code=status_HTTP_404_BAD_REQUEST,
            detail="Was not detected a sceneTitle and a description",
        )

    try:
        keywords = fetch_keywords(sceneTitle, description)
        if not keywords:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontraron recomendaciones de keywords",
            )
        return {"keywords": keywords}
    except HTTPException as http_err:
        raise http_err
    except Exception as error:
        print(f"ERROR: {error.args}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="ERROR INESPERADO"
        )


def fetch_keywords(sceneTitle: str, description: str, stream=False):
    """
    Llamar a la API externa para obtener las keywords mediante un prompt
    """

    prompt = (
        f'Dame una lista de 10 Keywords para el siguiente titulo y descripción, solo quiero las 10 palabras claves.'
        f'Titulo:{sceneTitle}. Descripcion: {description}.' 
        f'Al final solo dame la lista de las 10 palabras sin enumerar ni nada solo las palabras.'
    )
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "model": "llama3-8b-8192",
        "temperature": 1,
        "max_tokens": 1024,
        "top_p": 1,
        "stream": stream,
        "stop": None,
    }

    try:
        response = requests.post(
            GROQ_API_URL, data=json.dumps(payload), headers=headers, stream=stream
        )
        response.raise_for_status() 

        if stream:
            result = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    result += json.loads(decoded_line).get("content", "")
            return result
        else:
            response_json = response.json()
            content = (
                response_json.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "No se encontró respuesta")
            )
            return content
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
