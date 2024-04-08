from itertools import product
from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
from dbConn import conn
    
app = FastAPI()

# TODO: Configure the database connection to connect in the Uni Lab machines

# Pydantic model to define the schema of the data for PU POST DELETE
class Products(BaseModel):
    ProductID: int 
    Name: str 
     
@app.get("/")
def root():
    return {"message": "Introducing my coursework"}

# Route to return 50 products (MAX) from the production_product table via a GET request (no parameters used) without using a datamodel
@app.get("/products/allnomdel")
def get_all_products():
    cursor = conn.cursor()
    cursor.execute("SELECT ProductID, Name FROM Production_Product LIMIT 50")
    result = cursor.fetchall()
    return {"products": result}
    
# Route to return 50 products (MAX) from the production_product table via a GET request (no parameters used) using a Pydantic Datamodel
    
@app.get("/products/all", response_model=List[Products])
def read_item():
    cursor = conn.cursor()
    query = "SELECT ProductID, Name FROM Production_Product LIMIT 50"
    cursor.execute(query)
      
    item = cursor.fetchall()
    cursor.close()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    item = [Products(ProductID=productitem[0], Name=productitem[1]) for productitem in item]
    return item

# Route to return a specific product from the production_product table item via a GET request using a parameter (ProductID)
@app.get("/products/{product_id}", response_model=Products)
def read_item(product_id: int):
    cursor = conn.cursor()
    query = "SELECT ProductID, Name FROM Production_Product WHERE ProductID=%s"
    cursor.execute(query, (product_id,))
    item = cursor.fetchone()
    cursor.close()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"ProductID": item[0], "Name": item[1]}

@app.post("/products/{product_id}", response_model=Products)
def add_item(product_name: str, product_id: int):
    cursor = conn.cursor()
    query = "INSERT INTO Production_Product(ProductID, Name) VALUES (%s, %s)"
    if product_id <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0.")
        return {"item"}
    
@app.put("/products/{product_id}", response_model=Products)
def add_item(product_name: str, product_id: int):
    cursor = conn.cursor()
    if product_id <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be greater than 0.")
        return {"item"}
    
@app.delete("/products/{product_id}", response_model=Products)
def delete_item(product_id: int):
    cursor = conn.cursor()
    if product_id not in Products:
        raise HTTPException(status_code=400, detail="product not found.")
        return {"item"}
