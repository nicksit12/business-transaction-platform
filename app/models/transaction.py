import datetime
from decimal import Decimal

"""Requirment: 
    - Class transation with each having a unique id 
    - instances of transaction will have unique: int id,  string description, datetime date, decimal amount, string category
"""


class Transaction:

    def __init__(self, transaction_id, description, transaction_date, amount, category):
        self.transaction_id = transaction_id
        self.description = description
        self.transaction_date = transaction_date
        self.amount = amount
        self.category = category 




    
    