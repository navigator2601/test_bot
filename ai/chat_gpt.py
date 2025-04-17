import openai

class ChatGPT:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = self.api_key

    def ask(self, prompt):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()