from itertools import product
from fastapi import FastAPI, HTTPException, Depends, status, Query, Path
from typing import List, Optional
from datetime import datetime as dt
from sqlalchemy.exc import IntegrityError


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
@app.get("/all-product-inventory", response_model=List[models.Production_ProductInventory], status_code=200) # status code 200 = OK
def product_inventory(response: Response):
    try:
        product_inventory_list = crud.all_product_inventory()
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
    except HTTPException as e:
        if product_inventory_list is None:
            raise HTTPException(status_code=404, detail="Product not found")
        else:
            return {"error": str(e.detail)}, e.status_code

@app.get("/sales-order-details/{modified_date}", response_model=List[models.Sales_SalesOrderDetail], status_code=200) # status code 200 = OK
def get_sales_order_details(response: Response, modified_date: dt = Path(..., description="Format: YYYY-MM-DD HH:MM:SS")):
    try:
        formatted_date = modified_date.strftime('%Y-%m-%d')  # Format the date to only include year, month, and day
        order_details = crud.product_sales(formatted_date)  # Pass the formatted date
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
    except HTTPException as e:
        if order_details is None:
            raise HTTPException(status_code=404, detail="Product not found")
        else:
            return {"error": str(e.detail)}, e.status_code
    # cache-control header, not cachable
    response.headers["Cache-Control"] = "max-age=60" # not cacheable because it changes frequently
    return order_details # return list directly

#----------------------------------------------------------
# POST endpoints
#----------------------------------------------------------

# POST endpoint to create a new user
@app.post("/add-bill-of-materials/{bill_of_materials_id}", status_code=201) # status code 201 = created
def add_bill_of_materials(response: Response, bill_of_materials_id: int, component_id: int, unit_measure_code: str,
     bom_level: int, per_assembly_qty: int, start_date: dt = Path(..., description="Format: YYYY-MM-DD HH:MM:SS"), product_assembly_id: int = Query(None), end_date: dt = Query(None)):
    
    bill_of_mats = models.Production_BillOfMaterials(BillOfMaterialsID=bill_of_materials_id, ProductAssemblyID=product_assembly_id, ComponentID=component_id, StartDate=start_date,
                EndDate=end_date, UnitMeasureCode=unit_measure_code, BOMLevel=bom_level, PerAssemblyQty=per_assembly_qty, ModifiedDate=f'{dt.now().strftime("%Y-%m-%d %H:%M:%S")}')
    try: # try catch statment to catch any errors
        created_bill_of_mats = crud.create_bill_of_materials(bill_of_mats)
        response.headers["Cache-Control"] = "no-store" # no need to cache this response. User data changes frequently
        return created_bill_of_mats
    except HTTPException as e:
        if created_bill_of_mats is None or created_bill_of_mats == "":
            raise HTTPException(status_code=404, detail=f"Bill of materials not found.")
        else:
            return {"error": str(e.detail)}, e.status_code

# added functionality, may need to edit for better scalability
@app.post("/vendors/{business_entity_id}", response_model=models.Purchasing_Vendor, status_code=201) # status code 201 = created
# SQL (INSERT)
def add_vendor(response: Response ,business_entity_id: int, name: str, credit_rating: int, preferered_vendor_status: int, active_flag: int = Query(1), web_service: str = Query("NULL")): # parameters, name is required, web_service is optional
    account_number = name.replace(" ", "") # removes spaces from the name for the account number

    # formatting account number so its uppercase and formatting datetime.now() so miliseconds are removed
    vendor = models.Purchasing_Vendor(BusinessEntityID=business_entity_id, Name=name, AccountNumber=f'{account_number.upper()}0001', CreditRating=credit_rating, 
                                      PreferredVendorStatus=preferered_vendor_status , ActiveFlag=active_flag, PurchasingWebServiceURL=web_service, ModifiedDate=f'{dt.now().strftime("%Y-%m-%d %H:%M:%S")}')
    # try catch statment to catch any errors
    try:
        created_vendor = crud.create_vendor(vendor)
        response.headers["Cache-Control"] = "no-store" # not cacheable because it changes frequently
        return created_vendor # needs to return type obj or dict to be valid
    except HTTPException as e:
        if created_vendor is None or created_vendor == "":
            raise HTTPException(status_code=404, detail=f"Vendor not found.")
        else:
            return {"error": str(e.detail)}, e.status_code

#----------------------------------------------------------
# PUT endpoints
#----------------------------------------------------------

# PUT endpoint to update the active flag of a vendor
@app.put("/update-active-flag/{active_flag}/vendor-id/{business_entity_id}", status_code=200) # pydantic model not used because its required to use all fields
def update_vendor_active_flag(response: Response, business_entity_id: int, active_flag: int):
    try: # try catch statment to catch any errors
        updated = crud.update_vendor_active_flag(business_entity_id, active_flag)
        response.headers["Cache-Control"] = "no-store" # not cacheable because it changes frequently
        return updated
    except HTTPException as e:
        if updated is None or updated == "":
            raise HTTPException(status_code=404, detail="Vendor not found.")
        else:
            return {"error": str(e.detail)}, e.status_code

@app.put("/update-credit-card/{business_entity_id}", response_model=models.Sales_PersonCreditCard, status_code=200) # status code 200 = OK
# SQL (UPDATE)
def update_person_credit_card(response: Response, business_entity_id: int, credit_card_id: int):
    # Save data to pydantic model variables
    person_credit_card = models.Sales_PersonCreditCard(
        BusinessEntityID=business_entity_id, 
        CreditCardID=credit_card_id, 
        ModifiedDate=f'{dt.now().strftime("%Y-%m-%d %H:%M:%S")}' # current date formatted with h, m, s
    )
    try:
        updated = crud.update_person_credit_card(person_credit_card)
        response.headers["Cache-Control"] = "no-store" # not cacheable because it changes frequently
        return updated
    except HTTPException as e:
        if updated is None or updated == "":
            raise HTTPException(status_code=404, detail="Person or Credit Card not found.")
        else:
            return {"error": str(e.detail)}, e.status_code
    
#----------------------------------------------------------
# DELETE endpoints
#----------------------------------------------------------

@app.delete("/delete-job-candidate/{jobcandidate_id}", status_code=200) # status code 200 = OK
# SQL (DELETE)
def delete_job_candidate(response: Response, jobcandidate_id: int):
    try:
        crud.delete_jobcandidate(jobcandidate_id)
        response.headers["Cache-Control"] = "no-store" # not cacheable because it changes frequently
    except HTTPException as e:
        if jobcandidate_id is None:
            raise HTTPException(status_code=404, detail="Job Candidate not found.")
        else:
            return {"error": str(e.detail)}, e.status_code
            
@app.delete("/delete-bill-of-materials/{bill_of_materials_id}", status_code=200) # status code 200 = OK
# SQL (DELETE)
def delete_bill_of_materials(response: Response, bill_of_materials_id: int):
    try:
        crud.delete_bill_of_materials(bill_of_materials_id)
        response.headers["Cache-Control"] = "no-store" # not cacheable because it changes frequently
    except HTTPException as e:    
        if bill_of_materials_id is None:
            raise HTTPException(status_code=404, detail="Bill information not found.")
        else:
            return {"error": str(e.detail)}, e.status_code