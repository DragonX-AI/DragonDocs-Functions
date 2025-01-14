from joblib import load
import json
import openai

from fastapi import FastAPI, Request, Form

# FastAPI is a framework for creating web APIs
app = FastAPI()

from pydantic import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str = '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'

    class Config:
        env_file = '.env'

settings = Settings()
openai.api_key = settings.OPENAI_API_KEY

'''
GET Request
Path structure: http://localhost:8000/

A standard controller to confirm you are able to connect to your API.
'''
@app.get("/")
def index():
    return "This is a REST API for enabling my ML model to be used by other services."

'''
POST Request
Path structure: http://localhost:8000/predict?color={enter_color}&shape={enter_shape}

A controller for predicting a base happiness score for a pokemon based on their color and shape.
'''
@app.post("/predict")
def predict_happiness(color = 'black', shape = 'armor'):

    # Extract dictionaries saved from our jupyter notebook that map a category code to its name.
    with open('static/mappers/color_mapper.json', 'r') as colorfile:
        color_mapper = json.load(colorfile)
    with open('static/mappers/shape_mapper.json', 'r') as shapefile:
        shape_mapper = json.load(shapefile)

    # Map the query parameters "color" and "shape" to its corresponding category codes
    color_code = [int(k) for k,v in color_mapper.items() if v == color][0]
    shape_code = [int(k) for k, v in shape_mapper.items() if v == shape][0]

    # Load the model we saved from our jupyter notebook and predict a happiness score.
    model = load('./static/my_model.joblib')
    score = model.predict([[color_code, shape_code]])

    return { "happiness_score": score[0][0] }

@app.post("/api/ai/docs")
async def generateDocs(request: Request, aiReq: str = Form(...)):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt="class Log:\n"+aiReq+"Here's what the above class is doing, explained in a concise way:\n1.",
        temperature=0,
        max_tokens=150,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        stop=["\"\"\""]
    )
    result = response.choices[0].text
    
    return {"result": result, "request": aiReq}