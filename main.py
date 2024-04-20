from itertools import product
from fastapi import FastAPI, HTTPException, Depends, status, Query, Path
from typing import List, Optional
from datetime import datetime as dt

# Caching call responses
from fastapi.responses import Response

from dbConn import conn
import models
import crud
    
# TODO: Configure the database connection to connect in the Uni Lab machines

app = FastAPI()

# Dependency
def get_db():
    # db = conn.cursor() # cursor is a pointer to the database
    db = conn.cursor() 
    # 'try' block is used to ensure that the session is closed after the request is finished
    try:
        # 'yield' is used to create a new obj for each request. 'return' would only create one obj
        yield db # 
    except Exception as e: # debugging
        # code '400' = server couldnt understand the request due to invalid syntax
        raise HTTPException(status_code=400, detail=f"Database error: {e} ")
    finally: # exit is executed even if there was an exception
        db.close()

# GET x2: One with parameters, one without
# POST x2: Inserts into table, needs suitable parameters
# PUT x2: Updates into table, needs suitable parameters
# DELETE x2: Deletes from table, needs suitable parameters

#----------------------------------------------------------
# GET endpoints
#----------------------------------------------------------

# # Route to return 50 products (MAX) from the production_product table via a GET request (no parameters used) using a Pydantic Datamodel
@app.get("/all-product-inventory", response_model=List[models.Production_ProductInventory])
def product_inventory(response: Response):
    product_inventory_list = crud.all_product_inventory()
    if product_inventory_list is None:
        raise HTTPException(status_code=404, detail="Error: No Products Found.")
    product_inventory_list = [
        models.Production_ProductInventory(
            ProductID=item[0], 
            LocationID=item[1], 
            Shelf=item[2], 
            Bin=item[3], 
            Quantity=item[4], 
            rowguid=item[5], 
            ModifiedDate=item[6]
        ) for item in product_inventory_list
    ]

    print("Products returned from database...")  # if cache is empty

    # Caching the response for 60 secs
    response.headers["Cache-Control"] = "max-age=60"  # response header seen by client on Swagger UI

    return product_inventory_list  # return list directly

@app.get("/sales-order-details/{modified_date}", response_model=List[models.Sales_SalesOrderDetail]) 
def get_sales_order_details(response: Response, modified_date: dt = Path(..., description="Format: YYYY-MM-DD")):
    formatted_date = modified_date.strftime('%Y-%m-%d')  # Format the date to only include year, month, and day
    order_details = crud.product_sales(formatted_date)  # Pass the formatted date
    if order_details is None:
        raise HTTPException(status_code=404, detail="Product not found")
    order_details = [
        # for each data row, insert the corresponding data into 
        models.Sales_SalesOrderDetail(
            SalesOrderID=order[0],
            SalesOrderDetailID=order[1],
            CarrierTrackingNumber=order[2],
            OrderQty=order[3],
            ProductID=order[4],
            SpecialOfferID=order[5],
            UnitPrice=order[6],
            UnitPriceDiscount=order[7],
            LineTotal=order[8],
            rowguid=order[9],
            ModifiedDate=order[10]
        ) for order in order_details
    ]
    # cache-control header, not cachable
    response.headers["Cache-Control"] = "no-store" # not cacheable because it changes frequently
    return order_details # return list directly

#----------------------------------------------------------
# POST endpoints
#----------------------------------------------------------

@app.post("/add-user/{id}", response_model=models.Users)
def add_user(response: Response, id: int, username: str):
    user = models.Users(id=id, username=username)
    try:
        created_user = crud.create_user(user)
        response.headers["Cache-Control"] = "no-store" # no need to cache this response. User data changes frequently
        return created_user
    except Exception as e:
        if created_user is None or created_user == "":
            raise HTTPException(status_code=400, detail="Username must be provided.")
        if e == "Duplicate entry":
            raise HTTPException(status_code=400, detail="Duplicate Entry Error: {e}")
        else:
            raise HTTPException(status_code=400, detail="Error: {e}")
    return {"id": id, "username": username}

# added functionality, may need to edit for better scalability
@app.post("/vendors/{business_entity_id}", response_model=models.Purchasing_Vendor)
# SQL (INSERT)
def add_vendor(response: Response ,business_entity_id: int, name: str, credit_rating: int, preferered_vendor_status: int, active_flag: int = Query(1), web_service: str = Query("NULL")): # parameters, name is required, web_service is optional
    account_number = name.replace(" ", "") # removes spaces from the name for the account number

    # formatting account number so its uppercase and formatting datetime.now() so miliseconds are removed
    vendor = models.Purchasing_Vendor(BusinessEntityID=business_entity_id, Name=name, AccountNumber=f'{account_number.upper()}0001', CreditRating=credit_rating, 
                                      PreferredVendorStatus=preferered_vendor_status , ActiveFlag=active_flag, PurchasingWebServiceURL=web_service, ModifiedDate=f'{dt.now().strftime("%Y-%m-%d %H:%M:%S")}')
    # try catch statment to catch any errors (needs more exeptions or better handling)
    try:
        created_vendor = crud.create_vendor(vendor)
        response.headers["Cache-Control"] = "no-store" # not cacheable because it changes frequently
        return created_vendor # needs to return type obj or dict to be valid
    except Exception as e:
        if created_vendor is None or created_vendor == "":
            raise HTTPException(status_code=400, detail=f"Name must be provided. Value entered: {name}")
        if e == "Duplicate entry":
            raise HTTPException(status_code=400, detail=f"Duplicate Entry Error: {e}")
        else:
            raise HTTPException(status_code=400, detail=f"Error: {e}")
        return {"vendor": vendor}

#----------------------------------------------------------
# PUT endpoints
#----------------------------------------------------------

@app.put("/update-vendor-active-flag/{business_entity_id}/{active_flag}")
def update_vendor_active_flag(business_entity_id: int, active_flag: int):
    vendor = models.Purchasing_Vendor(BusinessEntityID=business_entity_id, ActiveFlag=active_flag)
    try:
        updated = crud.update_vendor_active_flag(vendor)
        return updated
    except HTTPException as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail="Vendor not found.")
        else:
            raise HTTPException(status_code=400, detail="Error: {e}")
        return {"item"}

@app.put("/product_price/{product_id}", response_model=models.Products)
# SQL (UPDATE)
def update_product_price(product_id: int, price: float):
    crud.update_product_price(product_id, price)
    if product_id <= 0:
        raise HTTPException(status_code=400, detail="Product ID must be greater than 0.")
        return {"item"}
    
#----------------------------------------------------------
# DELETE endpoints
#----------------------------------------------------------

@app.delete("/delete-job-candidate/{jobcandidate_id}", response_model=models.HumanResources_JobCandidate)
# SQL (DELETE)
def delete_job_candidate(jobcandidate_id: int):
    crud.delete_jobcandidate(jobcandidate_id)
    if jobcandidate_id not in models.HumanResources_JobCandidate:
        raise HTTPException(status_code=400, detail="Job Candidate not found.")
        return {"item"}