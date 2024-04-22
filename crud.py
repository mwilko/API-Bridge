# CRUD (Create, Read, Update, Delete) operations for the database

import models
import dbConn
from fastapi import HTTPException
from datetime import datetime as dt

#----------------------------------------------------------
# GET endpoints
#----------------------------------------------------------

def all_product_inventory(): # GET endpoint that returns all products
    cursor = dbConn.conn.cursor()
    query = "SELECT * FROM Production_ProductInventory"
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result

# function was edited to use only date, not date and time.
def product_sales(formatted_date: str): # GET endpoint that returns all sales for a specific date
    cursor = dbConn.conn.cursor()
    # limited to 50 because if the response is too much, the program would output a error
    query = "SELECT * FROM Sales_SalesOrderDetail WHERE DATE(ModifiedDate) = %s LIMIT 50"
    cursor.execute(query, (formatted_date,))
    result = cursor.fetchall()
    cursor.close()
    return result # return all sales for a specific date (LIMIT 50)

#----------------------------------------------------------
# POST endpoints
#----------------------------------------------------------

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

#----------------------------------------------------------
# PUT endpoints
#----------------------------------------------------------

# PUT endpoint that updates the active flag of a vendor
def update_vendor_active_flag(business_entity_id: int, active_flag: bool):
    cursor = dbConn.conn.cursor()
    current_date = dt.now().strftime('%Y-%m-%d %H:%M:%S')
    query = "UPDATE Purchasing_Vendor SET ActiveFlag = %s, ModifiedDate = %s WHERE BusinessEntityID = %s"
    cursor.execute(query, (active_flag, current_date, business_entity_id))
    dbConn.conn.commit()
    cursor.close()

    return {"BusinessEntityID": business_entity_id, "ActiveFlag": active_flag, "ModifiedDate": current_date}

# PUT endpoint that updates the credit card of a business entity
def update_person_credit_card(person_credit_card: models.Sales_PersonCreditCard):
    cursor = dbConn.conn.cursor()
    query = "UPDATE Sales_PersonCreditCard SET CreditCardID = %s, ModifiedDate = %s WHERE BusinessEntityID = %s"
    cursor.execute(query, (person_credit_card.CreditCardID, person_credit_card.ModifiedDate, person_credit_card.BusinessEntityID))
    dbConn.conn.commit()
    cursor.close()

    # Return the updated Sales_PersonCreditCard instance
    return person_credit_card

#----------------------------------------------------------
# DELETE endpoints
#----------------------------------------------------------

# DELETE endpoint that deletes a specific product
def delete_jobcandidate(jobcandidate_id: int):
    cursor = dbConn.conn.cursor()
    query = "DELETE FROM HumanResources_JobCandidate WHERE JobCandidateID = %s"
    cursor.execute(query, (jobcandidate_id,))  # Note the comma after jobcandidate_id
    dbConn.conn.commit()
    cursor.close()
    return {"JobCandidateID": jobcandidate_id} # return the deleted job candidate's JobCandidateID

# DELETE endpoint that deletes a specific employee
# Companies could keep the record up to six years (For possible legal reasons)
def delete_employee(business_entity_id: int):
    cursor = dbConn.conn.cursor()
    # constaints are set in the database to delete the records in the related tables
    query = "DELETE FROM HumanResources_EmployeeDepartmentHistory WHERE BusinessEntityID = %s"
    cursor.execute(query, (business_entity_id,))
    query = "DELETE FROM HumanResources_EmployeePayHistory WHERE BusinessEntityID = %s"
    cursor.execute(query, (business_entity_id,))
    query = "DELETE FROM HumanResources_Employee WHERE BusinessEntityID = %s"
    cursor.execute(query, (business_entity_id,))
    dbConn.conn.commit()
    cursor.close()