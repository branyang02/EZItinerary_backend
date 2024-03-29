from flask import Flask, jsonify, request, make_response
import requests
from lxml import html
from openai import OpenAI
from flask_cors import CORS

client = OpenAI()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

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
    text = tree.xpath(
        "//p//text() | //h1//text() | //h2//text() | //h3//text() | //h4//text() | //h5//text() | //h6//text()"
    )
    webString = " ".join(text)
    return webString


def get_word_details(webString):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant designed to output JSON.",
            },
            {
                "role": "user",
                "content": f"here is the full blog post of a travel itinerary: '{webString}'. Process the detailed travel itinerary provided in the blog post and output a structured JSON object based on the interface {INTERFACE}. Make sure you clearly retrieve all the activities and their locations for every day in the itinerary. Make sure each acativity's location has a clear name that could be geocoded. Make sure the travel location is also clearly identified in the it.",
            },
        ],
    )

    return eval(response.choices[0].message.content)


@app.route("/api/itinerary", methods=["GET", "POST"])  # Now handling POST method
def index():
    # Extract 'url' from the JSON body of the request
    data = request.get_json()
    url = data.get("url") if data else None

    print(url)
    if url:
        webString = makeString(url)
        result = get_word_details(webString)
        data = {"result": result}
        return jsonify(data)
    else:
        return jsonify({"error": "Missing 'url' in request body"}), 400


@app.route("/api/hello-world")
def hello_world():
    return jsonify({"message": "Hello, World!"})


if __name__ == "__main__":
    app.run(port=5002, debug=True)
