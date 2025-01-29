from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the Excel file (make sure to update the filename)
excel_file = 'data.xlsx'

# Read the Excel sheet into a pandas DataFrame
df = pd.read_excel(excel_file)

@app.route('/')
def home():
    return render_template('index.html')  # Render the HTML form (search bar)

@app.route('/search', methods=['POST', 'GET'])
def search():
    # Populate filter options
    filter_options = {
        col: df[col].dropna().unique().tolist() for col in df.columns
    }

    # Define allowed columns for filtering (change these columns based on your needs)
    allowed_columns = ['category', 'brand', 'dimensions(")','weight(kg)','promotion?','price','review']  # Only 'category' and 'brand' will be shown for filtering

    # Filter the filter_options to only include allowed columns
    filtered_filter_options = {col: values for col, values in filter_options.items() if col in allowed_columns}

    # Extract form data (search query and filters)
    search_query = request.form.get('query', '')  # Search query
    filters = {key: request.form.getlist(key) for key in request.form.keys() if key in df.columns}

    # Start with the full DataFrame
    filtered_df = df.copy()

    # Apply filters
    for col, values in filters.items():
        if values:  # Apply filter only if values are selected
            filtered_df = filtered_df[filtered_df[col].astype(str).isin(values)]

    # Apply search query if any
    if search_query:
        filtered_df = filtered_df[filtered_df.apply(
            lambda row: row.astype(str).str.contains(search_query, case=False).any(), axis=1)]

    # Convert filtered data to a list of dictionaries
    results = filtered_df.to_dict(orient='records') if not filtered_df.empty else None

    return render_template(
        'searchResults.html',
        query=search_query,
        results=results,
        filter_options=filtered_filter_options,  # Pass only the filtered options
        filters=filters,
        allowed_columns=allowed_columns  # Pass allowed_columns to template
    )


if __name__ == '__main__':
    app.run(debug=True)
