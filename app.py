from flask import Flask, request, render_template
import pyodbc
from azure.storage.blob import BlobServiceClient
import os

app = Flask(__name__)

# Read environment variables directly (works for both local and Azure App Service)
conn_str = os.getenv("CONN_STR")
blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_BLOB_STORAGE_CONN_STR"))

# Helper function to get a fresh DB connection when needed
def get_db_connection():
    return pyodbc.connect(conn_str)

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        ProductID = request.form["ProductID"]
        Name = request.form["Name"]
        CreatedDate = request.form["CreatedDate"]
        Price = float(request.form["Price"])
        Description = request.form["Description"]
        ImageURL = request.form["ImageURL"]

        # Insert product into database
        cursor.execute(
            "INSERT INTO Products (ProductID, Name, CreatedDate, Price, Description, ImageURL) VALUES (?, ?, ?, ?, ?, ?)",
            (ProductID, Name, CreatedDate, Price, Description, ImageURL)
        )
        conn.commit()

    # Fetch all products to display
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()

    conn.close()
    return render_template("index.html", products=products)

@app.route("/upload", methods=["POST"])
def upload_image():
    file = request.files['image']

    # Upload image to Azure Blob Storage
    blob_client = blob_service_client.get_blob_client(container="product-images", blob=file.filename)
    blob_client.upload_blob(file, overwrite=True)

    # Generate accessible URL for the uploaded image
    account_name = "productcataloguestorage"  # Replace if your storage account name is different
    image_url = f"https://{account_name}.blob.core.windows.net/product-images/{file.filename}"

    return image_url

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8000, debug=False)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Default to 5000 locally, Azure sets PORT=8000
    app.run(host='0.0.0.0', port=port)
