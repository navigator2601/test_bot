from google.cloud import aiplatform_v1
from config import GOOGLE_PROJECT_ID, GOOGLE_LOCATION

def predict_text(prompt):
    client = aiplatform_v1.PredictionServiceClient()
    endpoint = client.endpoint_path(
        project=GOOGLE_PROJECT_ID,
        location=GOOGLE_LOCATION,
        endpoint='text-bison'
    )
    instance = {"content": prompt}
    instances = [instance]
    parameters = {}
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )
    return response.predictions[0]["content"]