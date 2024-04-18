# CRUD (Create, Read, Update, Delete) operations for the database

import models
import dbConn
from fastapi import HTTPException
from datetime import datetime as dt

def all_products(items: models.Products):
    cursor = dbConn.conn.cursor()
    query = "SELECT ProductID, Name FROM Production_Product" # add LIMIT <amount> (if want to limit the response)
    cursor.execute(query)
    item = cursor.fetchall()
    cursor.close()
    return item

# function was edited to use only date, not date and time.
def product_sales(formatted_date: str): # GET endpoint that returns all sales for a specific date
    cursor = dbConn.conn.cursor()
    query = "SELECT * FROM Sales_SalesOrderDetail WHERE DATE(ModifiedDate) = %s"
    cursor.execute(query, (formatted_date,))
    result = cursor.fetchall()
    cursor.close()
    return result

def create_user(user: models.Users): # POST endpoint that creates a new user
    cursor = dbConn.conn.cursor() # create a cursor object using the connection
    query = ("INSERT INTO Users (id, username) VALUES (%s, %s)")
    cursor.execute(query, (user.id, user.username))
    cursor.close() # closes the cursor object (db session)
    dbConn.conn.commit() # commit the transaction
    return {"id": user.id, "username": user.username}

def create_vendor(vendor: models.Purchasing_Vendor): 
    # Create Pydantic model instance
    cursor = dbConn.conn.cursor() # create a cursor object using the connection
    query = ("INSERT INTO Purchasing_Vendor (BusinessEntityID, Name, AccountNumber, CreditRating, PreferredVendorStatus, " +
                "ActiveFlag, PurchasingWebServiceURL, ModifiedDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
    cursor.execute(query, (vendor.BusinessEntityID, vendor.Name, vendor.AccountNumber, vendor.CreditRating, 
                vendor.PreferredVendorStatus, vendor.ActiveFlag, vendor.PurchasingWebServiceURL, vendor.ModifiedDate))
    cursor.close() # closes the cursor object (db session)
    dbConn.conn.commit() # commit the transaction
    # Return the newly created vendor as a dictionary
    return {"BusinessEntityID": vendor.BusinessEntityID, "Name": vendor.Name, 
            "AccountNumber": vendor.AccountNumber, "CreditRating": vendor.CreditRating,
            "PreferredVendorStatus": vendor.PreferredVendorStatus, "ActiveFlag": vendor.ActiveFlag,"PurchasingWebServiceURL": vendor.PurchasingWebServiceURL, "ModifiedDate": vendor.ModifiedDate}

def update_vendor_active_flag(vendor: models.Purchasing_Vendor):
    cursor = dbConn.conn.cursor()
    query = ("UPDATE Purchasing_Vendor SET ActiveFlag = %s WHERE BusinessEntityID = %s")
    cursor.execute(query, (vendor.ActiveFlag, vendor.BusinessEntityID))
    cursor.close()
    dbConn.conn.commit()
    return {"BusinessEntityID": vendor.BusinessEntityID, "ActiveFlag": vendor.ActiveFlag}

# PUT endpoint that updates the price of a specific product
def update_product_price(product_id: int, price: float):
    cursor = dbConn.conn.cursor() # create a cursor object using the connection
    # Update the price of a product in the database
    query = ("UPDATE Production_Product SET ListPrice=%s WHERE ProductID=%s")
    cursor.execute(query, (price, product_id))
    cursor.close() # closes the cursor object (db session)
    return {"message": "Price updated successfully"}

# DELETE endpoint that deletes a specific product
def delete_jobcandidate(jobcandidate_id: int):
    # Delete a product from the database
    cursor = dbConn.conn.cursor() # create a cursor object using the connection
    query = ("DELETE FROM HumanResources_JobCandidate WHERE JobCandidateID=%s")
    cursor.execute(query, (jobcandidate_id))
    cursor.close() # closes the cursor object (db session)
    return {"message": "Job Candidate deleted successfully"}