from modules import run 
from openai import OpenAI

def main():
    # Get a list of keywords from the endpoint https://safesound.vercel.com/generate-keywords
    client = OpenAI()
    
    run("apples", {'apple', 'apples'}, client)
    
if __name__ == "__main__":
    main()