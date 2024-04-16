# CRUD (Create, Read, Update, Delete) operations for the database

import models
import dbConn

def create_vendor(vendor: models.Purchasing_Vendor):
    # Create Pydantic model instance
    cursor = dbConn.conn.cursor() # create a cursor object using the connection
    cursor.execute("INSERT INTO Purchasing_Vendor (BusinessEntityID, Name, AccountNumber, CreditRating, PreferredVendorStatus, " +
                "ActiveFlag, PurchasingWebServiceURL, ModifiedDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                (vendor.BusinessEntityID, vendor.Name, vendor.AccountNumber, vendor.CreditRating, vendor.PreferredVendorStatus, 
                vendor.ActiveFlag, vendor.PurchasingWebServiceURL, vendor.ModifiedDate))
    cursor.close() # closes the cursor object (db session)
    # Return the newly created vendor as a dictionary
    return {"BusinessEntityID": vendor.BusinessEntityID, "Name": vendor.Name, 
            "AccountNumber": vendor.AccountNumber, "CreditRating": vendor.CreditRating,
            "PreferredVendorStatus": vendor.PreferredVendorStatus, "ActiveFlag": vendor.ActiveFlag,"PurchasingWebServiceURL": vendor.PurchasingWebServiceURL, "ModifiedDate": vendor.ModifiedDate}

# PUT endpoint that updates the price of a specific product
def update_product_price(product_id: int, price: float):
    cursor = dbConn.conn.cursor() # create a cursor object using the connection
    # Update the price of a product in the database
    cursor.execute("UPDATE Production_Product SET ListPrice=%s WHERE ProductID=%s", (price, product_id))
    cursor.close() # closes the cursor object (db session)
    return {"message": "Price updated successfully"}

# DELETE endpoint that deletes a specific product
def delete_jobcandidate(jobcandidate_id: int):
    # Delete a product from the database
    cursor = dbConn.conn.cursor() # create a cursor object using the connection
    cursor.execute("DELETE FROM HumanResources_JobCandidate WHERE JobCandidateID=%s", (jobcandidate_id,))
    cursor.close() # closes the cursor object (db session)
    return {"message": "Job Candidate deleted successfully"}