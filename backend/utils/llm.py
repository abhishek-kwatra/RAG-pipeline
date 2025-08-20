import os
from openai import OpenAI
from openai import APIConnectionError, AuthenticationError, RateLimitError, OpenAIError
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def ask_llm(context, question):
    prompt = f"Answer based on context:\n{context}\nQ: {question}\nA:"

    try:
        response = client.chat.completions.create(
            model="gpt-5", 
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return {
            response.choices[0].message.content.strip()
        }

    except RateLimitError:
        return {
            "Rate limit exceeded or quota exhausted. Please check your OpenAI account usage."
        }

    except AuthenticationError:
        return {
            "Authentication failed. Please check your API key."
        }

    except APIConnectionError:
        return {
            "Failed to connect to OpenAI servers. Please check your network."
        }

    except OpenAIError as e:
        return {
             f"An error occurred: {str(e)}"
        }
