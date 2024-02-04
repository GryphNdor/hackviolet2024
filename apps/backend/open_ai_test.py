from openai import OpenAI

client = OpenAI()
# defaults to getting the key using os.environ.get("OPENAI_API_KEY")
# if you saved the key under a different environment variable name, you can do something like:
# client = OpenAI(
#   api_key=os.environ.get("CUSTOM_ENV_NAME"),
# )
setx OPENAI_API_KEY "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"