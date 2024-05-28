from toolbox import tool
from agent import Agent
import os
from dotenv import load_dotenv
import requests
import config as cfg

load_dotenv()
client = cfg.ollama_non
model = "mistral:v0.3"
weather_key = os.environ.get("WEATHER_API")
api_type = "ollama"

@tool
def fetch_weather(location: str, unit: str = "farenheit") -> str:
    """Retrieves the current weather for a given location."""
    q = location
    response = requests.get(f"https://api.weatherapi.com/v1/forecast.json?q={q}&key={weather_key}")
    weather_data = response.json()
    forecast = weather_data["forecast"]["forecastday"][0]["day"]["condition"]
    return forecast

@tool
def fetch_news(topic: str) -> str:
    """Retrieves the latest news for a given topic."""
    response = requests.get(f"https://newsapi.org/v2/everything?q={topic}&apiKey={os.environ.get('NEWS_API')}")
    news_data = response.json()
    articles = news_data["articles"]
    return articles[0]["title"]

if __name__ == "__main__":
    # Create an instance of the Agent class with the desired LLM client, model, and API type
    agent = Agent(client, model, api_type)

    # Start the conversation loop
    while True:
        user_input = input("User: ")
        response = agent.chat(user_input)
        print(f"Agent: {response}")