import MySQLdb

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'passwd': 'Wilko777!!!',
    'db': 'AdventureWorks2019',
}
  
# Create a connection to the database
conn = MySQLdb.connect(**db_config)              
