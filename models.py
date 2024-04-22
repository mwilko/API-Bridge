# Here is where the Pydantic models are defined. 
# Pydantic models are used to validate the data that is sent to the API.

from pydantic import BaseModel
from typing import Optional
from datetime import datetime as dt

# <name>: <data-type> (Pydanitc way to declare types)

# Pydantic model to define the schema of the data for GET PUT POST DELETE

# ProductInventory table
class Production_ProductInventory(BaseModel):
    ProductID: int
    LocationID: int
    Shelf: str
    Bin: int
    Quantity: int
    rowguid: str
    ModifiedDate: dt

# SalesOrderDetail table
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

# Purchasing Vendor table
class Purchasing_Vendor(BaseModel):
    BusinessEntityID: int # Primary Key (not auto incremented)
    AccountNumber: str
    Name: str
    CreditRating: int
    PreferredVendorStatus: int
    ActiveFlag: int
    PurchasingWebServiceURL: str
    ModifiedDate: str

# Sales Person Credit Card table
class Sales_PersonCreditCard(BaseModel):
    BusinessEntityID: int
    CreditCardID: int
    ModifiedDate: str

# Human Resources Job Candidate table
class HumanResources_JobCandidate(BaseModel):
    JobCandidateID: int
    BusinessEntityID: int
    Resume: str
    ModifiedDate: str

# Production Bill of Materials table
class Production_BillOfMaterials(BaseModel):
    BillOfMaterialsID: int
    ProductAssemblyID: Optional[int]
    ComponentID: int
    StartDate: dt
    EndDate: Optional[dt]
    UnitMeasureCode: str
    BOMLevel: int
    PerAssemblyQty: float
    ModifiedDate: dt