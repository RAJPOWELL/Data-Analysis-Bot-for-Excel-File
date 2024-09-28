# app.py
import os
import pandas as pd
from flask import Flask, request, jsonify, render_template
import openai

# Load OpenAI API key
openai.api_key = ''

# Load Excel data into a Pandas DataFrame
df = pd.read_excel("")  # Load the correct file

# Flask app
app = Flask(__name__)

# Function to query GPT-4 turbo for answers based on a subset of the data
def ask_gpt(question, data_subset):
    prompt = f"The user asked: '{question}'. Here is the relevant data:\n{data_subset.to_string(index=False)}\nPlease provide insights or an answer based on this data."
    
    # Use the chat completion endpoint with gpt-4-turbo model
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",  # Use the turbo model (faster and cheaper version of GPT-4)
        messages=[
            {"role": "system", "content": "You are an AI bot providing data insights based on the provided data."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1500  # Adjust max tokens as needed
    )
    
    return response['choices'][0]['message']['content']

# Function to handle user queries and find relevant data in the DataFrame
def handle_query(question):
    # Simple keyword-based matching for demo purposes, more complex NLP can be added later
    if "show all data" in question.lower():
        # If the user wants all the data, return a small preview (limit size to fit within token limits)
        return df.head(100)  # Show only the first 100 rows to avoid token overflow
    elif "columns" in question.lower():
        # Return the list of columns in the dataset
        return pd.DataFrame({'Columns': df.columns})
    elif "rows" in question.lower():
        # Return the number of rows
        return pd.DataFrame({'Total Rows': [df.shape[0]]})
    else:
        # Default to searching specific columns based on keywords
        # For example, if the user asks for a specific column, filter the data
        for col in df.columns:
            if col.lower() in question.lower():
                return df[[col]].head(100)  # Return a subset of data (first 100 rows)
    
    # If no match, return an empty DataFrame
    return pd.DataFrame()

# Route for answering questions
@app.route('/ask', methods=['POST'])
def ask():
    user_question = request.json.get("question", "")
    # Handle query and extract relevant data
    data_subset = handle_query(user_question)
    
    if data_subset.empty:
        answer = "I couldn't find relevant data for your question."
    else:
        # Ask GPT to generate an answer based on the data subset
        answer = ask_gpt(user_question, data_subset)
    
    return jsonify({"answer": answer.strip()})

# Home route to render the frontend
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
