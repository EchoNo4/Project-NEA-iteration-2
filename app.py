from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the Excel file (make sure to update the filename)
excel_file = 'data.xlsx'

# Read the Excel sheet into a pandas DataFrame
df = pd.read_excel(excel_file)

# Route to show the HTML form
@app.route('/')
def home():
    return render_template('index.html')  # Render the HTML form

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']

    # Search for the query in the DataFrame
    results = df[df.apply(lambda row: row.astype(str).str.contains(query, case=False).any(), axis=1)]

    # If there are results, convert them to a list of dictionaries
    if not results.empty:
        all_results = results.to_dict(orient='records')  # Convert all rows to dictionaries
    else:
        all_results = None

    return render_template('searchResults.html', query=query, results=all_results)

if __name__ == '__main__':
    app.run(debug=True)