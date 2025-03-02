from flask import Flask, request, render_template
import pyodbc
from azure.storage.blob import BlobServiceClient
import os 
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Environment Variables
conn_str = os.getenv("CONN_STR")
blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZURE_BLOB_STORAGE_CONN_STR"))

@app.route("/", methods=["GET", "POST"])
def index():
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        description = request.form["description"]
        image_url = request.form["image_url"]

        cursor.execute("INSERT INTO Products (ProductName, Price, Description, ImageURL) VALUES (?, ?, ?, ?)",
                       (name, price, description, image_url))
        conn.commit()

    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()

    conn.close()
    return render_template("index.html", products=products)

@app.route("/upload", methods=["POST"])
def upload_image():
    file = request.files['image']
    blob_client = blob_service_client.get_blob_client(container="product-images", blob=file.filename)
    blob_client.upload_blob(file, overwrite=True)

    account_name = "productcataloguestorage"
    image_url = f"https://{account_name}.blob.core.windows.net/product-images/{file.filename}"
    return image_url

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

