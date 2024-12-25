from sanic import Sanic, response
from sanic.response import json
import re

app = Sanic("SurveyProcessor")

# Store survey data in memory for now
survey_data_store = []

# Function to validate the payload
def validate_payload(data):
    if 'user_id' not in data or not re.match(r'^\w{5,}$', data['user_id']):
        return False, "Invalid user_id"
    
    survey_results = data.get("survey_results", [])
    if len(survey_results) != 10:
        return False, "survey_results must contain exactly 10 items"
    
    seen_questions = set()
    for result in survey_results:
        question_number = result.get("question_number")
        question_value = result.get("question_value")
        
        if not isinstance(question_number, int) or not (1 <= question_number <= 10):
            return False, "Each question_number must be an integer between 1 and 10"
        
        if question_number in seen_questions:
            return False, "Duplicate question_number found"
        seen_questions.add(question_number)
        
        if not isinstance(question_value, int) or not (1 <= question_value <= 7):
            return False, "Each question_value must be an integer between 1 and 7"
    
    return True, "Valid payload"

@app.route("/", methods=["GET"])
async def home(request):
    return response.html("<h1>Welcome to the Survey Processor App!</h1>")

@app.route("/survey", methods=["POST"])
async def handle_survey(request):
    survey_data = request.json  # Get the JSON data from the request body
    
    # Validate the data
    is_valid, validation_message = validate_payload(survey_data)
    
    if not is_valid:
        return json({"message": "Invalid survey data", "error": validation_message}, status=400)
    
    # Store the valid survey data
    survey_data_store.append(survey_data)
    
    return json({"message": "Survey data received!", "data": survey_data})

@app.route("/survey/view", methods=["GET"])
async def view_survey(request):
    # Fetch the survey data stored in memory or a database
    survey_data = request.app.config.get('survey_data', None)
    
    if not survey_data:
        return response.json({"message": "No survey data available."})
    
    # Build a structured response to display on the webpage
    survey_results_html = "<ul>"
    for result in survey_data.get("survey_results", []):
        survey_results_html += f"<li>Question {result['question_number']}: {result['question_value']}</li>"
    survey_results_html += "</ul>"
    
    # Construct the HTML page
    html_content = f"""
    <html>
        <head><title>Survey Data</title></head>
        <body>
            <h1>Survey Data</h1>
            <p>User ID: {survey_data.get("user_id")}</p>
            <h2>Survey Results:</h2>
            {survey_results_html}
        </body>
    </html>
    """
    
    return response.html(html_content)


@app.route("/survey/feedback", methods=["POST"])
async def handle_feedback(request):
    feedback = request.json
    # Process the feedback data
    return json({"message": "Feedback received!", "feedback": feedback})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
