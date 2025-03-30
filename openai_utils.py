from transformers import pipeline

# Ініціалізація моделі LLaMA через Hugging Face
generator = pipeline('text-generation', model='meta-llama/Meta-Llama-3-8B')

def generate_response(prompt):
    response = generator(prompt, max_length=150, num_return_sequences=1)
    return response[0]['generated_text']