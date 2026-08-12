import csv
from datetime import datetime
from datetime import date
from decimal import Decimal
from app.models.transaction import Transaction 


def read_csv_standard(filepath):
        records = []

        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            for rows in reader:
                records.append(rows)

            return records

    #this is for changing the keys values 
def convert_to_datatypes(records):

        for record in records:
            record["transaction_id"] = int("".join(char for char in record["transaction_id"] if char.isdigit())) 
            record["transaction_date"] = date.fromisoformat(record["transaction_date"]) 
            record["amount"] = Decimal(record["amount"])

        return records

def convert_to_transactions(records):

        transactions = [] 
        for record in records:
            transaction = Transaction(record["transaction_id"],record["description"] ,record["transaction_date"] ,record["amount"] ,record["category"])
            transactions.append(transaction)

        return transactions

#I dont really understand why this works
def import_transactions(filepath):
        records = read_csv_standard(filepath)
        refined_records = convert_to_datatypes(records)
        imported_transactions = convert_to_transactions(refined_records)

        return imported_transactions