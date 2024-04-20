# Here is where the Pydantic models are defined. 
# Pydantic models are used to validate the data that is sent to the API.

from pydantic import BaseModel
from typing import Optional
from datetime import datetime as dt

# <name>: <data-type> (Pydanitc way to declare types)

# Pydantic model to define the schema of the data for GET PUT POST DELETE

class Users(BaseModel):
    id: int
    username: str

class Products(BaseModel):
    ProductID: int 
    Name: str 

class Production_ProductInventory(BaseModel):
    ProductID: int
    LocationID: int
    Shelf: str
    Bin: int
    Quantity: int
    rowguid: str
    ModifiedDate: dt

class Sales_SalesOrderDetail(BaseModel):
    SalesOrderID: int
    SalesOrderDetailID: int
    CarrierTrackingNumber: Optional[str] # optional due to NULL values in the db
    OrderQty: int
    ProductID: int
    SpecialOfferID: int
    UnitPrice: float
    UnitPriceDiscount: float
    LineTotal: float
    rowguid: str
    ModifiedDate: dt

class Purchasing_Vendor(BaseModel):
    BusinessEntityID: int # Primary Key (not auto incremented)
    AccountNumber: str
    Name: str
    CreditRating: int
    PreferredVendorStatus: int
    ActiveFlag: int
    PurchasingWebServiceURL: str
    ModifiedDate: str

class HumanResources_JobCandidate(BaseModel):
    JobCandidateID: int
    BusinessEntityID: int
    Resume: str
    ModifiedDate: str