from google.cloud import aiplatform

def generate_response(prompt):
    # Ініціалізація платформи
    aiplatform.init(project="YOUR_PROJECT_ID", location="us-central1")
    model = aiplatform.TextGenerationModel.from_pretrained("text-bison")

    # Генерація відповіді
    response = model.predict(prompt=prompt)
    return response.text