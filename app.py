from flask import Flask, request, render_template
import pyodbc
from azure.storage.blob import BlobServiceClient
import os 
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)

# Azure SQL Connection String
conn_str = os.getenv("CONN_STR")

@app.route("/", methods=["GET", "POST"])
def index():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        description = request.form["description"]
        image_url = request.form["image_url"]  # Later we'll use blob storage here

        cursor.execute("INSERT INTO Products (ProductName, Price, Description, ImageURL) VALUES (?, ?, ?, ?)",
                       (name, price, description, image_url))
        conn.commit()

    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()

    conn.close()
    return render_template("index.html", products=products)

blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_BLOB_STORAGE_CONN_STR"))

@app.route("/upload", methods=["POST"])
def upload_image():
    file = request.files['image']
    blob_client = blob_service_client.get_blob_client(container="product-images", blob=file.filename)
    blob_client.upload_blob(file)

    image_url = f"https://{productcataloguestorage}.blob.core.windows.net/products/{file.filename}"
    return image_url

if __name__ == "__main__":
    app.run(debug=True)
