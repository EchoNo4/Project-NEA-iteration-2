from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Load the Excel file (make sure to update the filename)
excel_file = 'data.xlsx'

# Read the Excel sheet into a pandas DataFrame
df = pd.read_excel(excel_file)

# Define a function to fetch product details by ID
def get_product_by_id(product_id):
    # Check if the product ID exists in the DataFrame
    if product_id in df.index:
        product = df.loc[product_id].to_dict()  # Convert the row to a dictionary
        return product
    return None  # Return None if the product ID is not found

@app.route('/')
def home():
    # Convert the first row of the DataFrame into a dictionary
    specific_item1 = df.iloc[0].to_dict()  # Use `iloc[0]` instead of `loc[0]` for safety
    specific_item2 = df.iloc[14].to_dict()
    specific_item3 = df.iloc[21].to_dict()
    specific_item4 = df.iloc[50].to_dict()
    
    return render_template('index.html', 
                           item1=specific_item1, 
                           item2=specific_item2,
                           item3=specific_item3, 
                           item4=specific_item4) # Render the HTML form (search bar)

@app.route('/search', methods=['POST', 'GET'])
def search():
    # Populate filter options
    filter_options = {
        col: df[col].dropna().unique().tolist() for col in df.columns
    }

    # Define allowed columns for filtering
    allowed_columns = ['category', 'brand', 'dimensions(")', 'weight(kg)', 'promotion?', 'review']

    # Filter the filter_options to only include allowed columns
    filtered_filter_options = {col: values for col, values in filter_options.items() if col in allowed_columns}

    # Extract form data (search query and filters)
    search_query = request.form.get('query', '')  # Search query
    filters = {key: request.form.getlist(key) for key in request.form.keys() if key in df.columns}

    # Extract range inputs for price and review
    min_price = request.form.get('min_price', '')
    max_price = request.form.get('max_price', '')
    min_review = request.form.get('min_review', '')
    max_review = request.form.get('max_review', '')

    # Start with the full DataFrame
    filtered_df = df.copy()

    # Apply filters
    for col, values in filters.items():
        if values:  # Apply filter only if values are selected
            filtered_df = filtered_df[filtered_df[col].astype(str).isin(values)]

    # Apply price range filter
    if min_price and max_price:
        filtered_df = filtered_df[
            (filtered_df['price'] >= float(min_price)) & (filtered_df['price'] <= float(max_price))
        ]

    # Apply review range filter
    if min_review and max_review:
        filtered_df = filtered_df[
            (filtered_df['review'] >= float(min_review)) & (filtered_df['review'] <= float(max_review))
        ]

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
        filter_options=filtered_filter_options,
        filters=filters,
        allowed_columns=allowed_columns,
        min_price=min_price,
        max_price=max_price,
        min_review=min_review,
        max_review=max_review
    )

@app.route('/product/<int:product_id>')
def product(product_id):
    # Fetch product details by ID
    product = get_product_by_id(product_id)  # Fetch product details from the DataFrame

    if product:
        return render_template('productPage.html', product=product)
    else:
        return "Product not found", 404

if __name__ == '__main__':
    # Ensure the index is numeric for product lookup by ID
    if df.index.dtype != 'int64':
        df.reset_index(drop=True, inplace=True)
    app.run(debug=True)
