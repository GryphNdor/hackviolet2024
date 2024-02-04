from modules import run 
from openai import OpenAI
import requests


def main():
    # Get a list of keywords from the endpoint https://safesound.vercel.com/generate-keywords
    client = OpenAI()
    trigger_response = requests.get('https://hack-violet-backend.vercel.app/get-topic')
    trigger = trigger_response.text
    
    keywords_response = requests.get('https://hack-violet-backend.vercel.app/get-json', json={'topic': trigger})
    keywords = keywords_response.json()
    print(keywords)
    
    run(trigger, keywords, client)
    
if __name__ == "__main__":
    main()