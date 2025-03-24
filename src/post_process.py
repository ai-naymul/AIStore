from google import genai
import os
import logging
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class PostProcess():
    def __init__(self):
        self.client = genai.Client(api_key='GEMINI_API_KEY', http_options={'api_version':'v1alpha'})
    
    def process_post(self, content):
        try:
            response = self.client.models.generate_content(model='gemini-2.0-flash-thinking-exp', contents=content)
            if response:
                logging.info(f"Generated the post for {content}")
                return response.text
        except Exception as e:
            logging.error(f"Error generating post from gemini with: {str(e)}")
