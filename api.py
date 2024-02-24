from flask import Flask, jsonify, request
import requests
from lxml import html
from openai import OpenAI

client = OpenAI()
app = Flask(__name__)

INTERFACE = """
interface Activity {
  activity: string;
  description: string;
  location: string;
}

interface DayItinerary {
  activities: Activity[];
  day: number;
}

interface ItineraryResult {
  itinerary: DayItinerary[];
  travel_location: string;
}
"""


def makeString(url):
    resp = requests.get(url)
    tree = html.fromstring(resp.content)
    text = tree.xpath("//text()")
    webString = " ".join(text)
    return webString


def get_word_details(webString):
    response = client.chat.completions.create(
        model="gpt-4-0125-preview",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant designed to output JSON.",
            },
            {
                "role": "user",
                "content": f"here is the full blog post of a travel itinerary: '{webString}'. Process the detailed travel itinerary provided in the blog post and output a structured JSON object based on the interface {INTERFACE}.",
            },
        ],
    )

    return eval(response.choices[0].message.content)


@app.route("/")
def index():
    url = request.args.get("url")

    print(url)
    if url:
        webString = makeString(url)
        result = get_word_details(webString)
        data = {"result": result}
        return jsonify(data)
    else:
        return jsonify({"error": "Missing 'url' parameter"}), 400


if __name__ == "__main__":
    app.run()
