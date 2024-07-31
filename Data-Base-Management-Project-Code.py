import sqlite3
from tabulate import tabulate
from datetime import datetime, timedelta

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('service_records.db')
cursor = conn.cursor()

# Create the table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS ServiceRecords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        date_of_purchase TEXT,
        phone_number TEXT,
        address TEXT,
        date_of_servicing TEXT,
        amount_paid REAL,
        amount_due REAL
    )
''')

# Function to add a new service record
def add_service_record():
    name = input("Enter name: ")
    date_of_purchase = input("Enter date of purchase (DD-MM-YYYY): ")
    phone_number = input("Enter phone number: ")
    address = input("Enter address: ")
    date_of_servicing = input("Enter date of servicing (DD-MM-YYYY): ")
    amount_paid = float(input("Enter amount paid: "))
    amount_due = float(input("Enter amount due: "))

    date_of_purchase_iso = datetime.strptime(date_of_purchase, '%d-%m-%Y').strftime('%Y-%m-%d')
    date_of_servicing_iso = datetime.strptime(date_of_servicing, '%d-%m-%Y').strftime('%Y-%m-%d')

    cursor.execute('''
        INSERT INTO ServiceRecords (name, date_of_purchase, phone_number, address, date_of_servicing, amount_paid, amount_due)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, date_of_purchase_iso, phone_number, address, date_of_servicing_iso, amount_paid, amount_due))
    conn.commit()
    print("Record added successfully!")

# Function to view all service records with sorting option
def view_service_records():
    sort_option = input("Do you want to sort the records? (yes/no): ").strip().lower()
    valid_sort_fields = ["name", "date_of_purchase", "date_of_servicing", "amount_paid", "amount_due"]
    
    if sort_option == 'yes':
        while True:
            sort_field = input("Enter the field to sort by (name, date of purchase, date of servicing, amount paid, amount due): ").strip().replace(" ", "_")
            if sort_field not in valid_sort_fields:
                print("Invalid sort field! Please choose a valid field.")
                continue
            query = f"SELECT * FROM ServiceRecords ORDER BY {sort_field}"
            break
    else:
        query = "SELECT * FROM ServiceRecords"
        
    cursor.execute(query)
    records = cursor.fetchall()
    headers = ["ID", "Name", "Date of Purchase", "Phone Number", "Address", "Date of Servicing", "Amount Paid", "Amount Due"]

    if records:
        records = [
            (
                rec[0], rec[1], datetime.strptime(rec[2], '%Y-%m-%d').strftime('%d-%m-%Y'), rec[3],
                rec[4], datetime.strptime(rec[5], '%Y-%m-%d').strftime('%d-%m-%Y'), rec[6], rec[7]
            )
            for rec in records
        ]

    print(tabulate(records, headers, tablefmt='grid'))

# Function to search records based on user input
def search_service_records():
    valid_fields = ["name", "date_of_purchase", "phone_number", "address", "date_of_servicing", "amount_paid", "amount_due"]
    while True:
        field = input("Enter the field to search by (name, date of purchase, phone number, address, date of servicing, amount paid, amount due): ").strip().replace(" ", "_")
        if field not in valid_fields:
            print("Invalid field! Please choose a valid field.")
            continue
        value = input(f"Enter the value to search for in {field.replace('_', ' ')}: ")
        query = f"SELECT * FROM ServiceRecords WHERE {field} LIKE ?"
        cursor.execute(query, ('%' + value + '%',))
        records = cursor.fetchall()
        
        if not records:
            print("No records found.")
            return None

        headers = ["ID", "Name", "Date of Purchase", "Phone Number", "Address", "Date of Servicing", "Amount Paid", "Amount Due"]
        if field in ["date_of_purchase", "date_of_servicing"]:
            records = [
                (
                    rec[0], rec[1], datetime.strptime(rec[2], '%Y-%m-%d').strftime('%d-%m-%Y'), rec[3],
                    rec[4], datetime.strptime(rec[5], '%Y-%m-%d').strftime('%d-%m-%Y'), rec[6], rec[7]
                )
                for rec in records
            ]

        while len(records) > 1:
            print("Multiple records found:")
            print(tabulate(records, headers, tablefmt='grid'))
            
            exit_choice = input("Do you want to exit the search? (yes/no): ").strip().lower()
            if exit_choice == 'yes':
                return None

            field = input("Enter the field to refine search by (name, date of purchase, phone number, address, date of servicing, amount paid, amount due): ").strip().replace(" ", "_")
            if field not in valid_fields:
                print("Invalid field! Please choose a valid field.")
                continue
            value = input(f"Enter the value to search for in {field.replace('_', ' ')}: ")
            query = f"SELECT * FROM ServiceRecords WHERE {field} LIKE ? AND id IN ({','.join(['?' for _ in records])})"
            record_ids = [record[0] for record in records]
            cursor.execute(query, ['%' + value + '%'] + record_ids)
            records = cursor.fetchall()

            if field in ["date_of_purchase", "date_of_servicing"]:
                records = [
                    (
                        rec[0], rec[1], datetime.strptime(rec[2], '%Y-%m-%d').strftime('%d-%m-%Y'), rec[3],
                        rec[4], datetime.strptime(rec[5], '%Y-%m-%d').strftime('%d-%m-%Y'), rec[6], rec[7]
                    )
                    for rec in records
                ]

        if records:
            print("Record found:")
            print(tabulate([records[0]], headers, tablefmt='grid'))
            return records[0]
        else:
            print("No records found.")
            return None

# Function to update a service record
def update_service_record():
    record = search_service_records()
    if not record:
        return

    record_id = record[0]
    fields = ["name", "date_of_purchase", "phone_number", "address", "date_of_servicing", "amount_paid", "amount_due"]

    while True:
        field = input(f"Which field would you like to update? {fields}: ").strip().replace(" ", "_")
        if field not in fields:
            print("Invalid field! Please choose a valid field.")
            continue

        new_value = input(f"Enter new value for {field.replace('_', ' ')} (leave blank to keep current value): ")
        if new_value:
            if field in ["amount_paid", "amount_due"]:
                new_value = float(new_value)
            if field in ["date_of_purchase", "date_of_servicing"]:
                new_value = datetime.strptime(new_value, '%d-%m-%Y').strftime('%Y-%m-%d')
            query = f"UPDATE ServiceRecords SET {field} = ? WHERE id = ?"
            cursor.execute(query, (new_value, record_id))
            conn.commit()
            print(f"{field.replace('_', ' ')} updated successfully!")

        more = input("Do you want to update another field? (yes/no): ").lower()
        if more != 'yes':
            break

    print("Record updated successfully!")

# Function to delete a service record by searching through any field
def delete_service_record():
    valid_fields = ["name", "date_of_purchase", "phone_number", "address", "date_of_servicing", "amount_paid", "amount_due"]
    while True:
        field = input("Enter the field to search by (name, date of purchase, phone number, address, date of servicing, amount paid, amount due): ").strip().replace(" ", "_")
        if field not in valid_fields:
            print("Invalid field! Please choose a valid field.")
            continue
        value = input(f"Enter the value to search for in {field.replace('_', ' ')}: ")
        query = f"SELECT * FROM ServiceRecords WHERE {field} LIKE ?"
        cursor.execute(query, ('%' + value + '%',))
        records = cursor.fetchall()
        
        if not records:
            print("No records found.")
            return

        headers = ["ID", "Name", "Date of Purchase", "Phone Number", "Address", "Date of Servicing", "Amount Paid", "Amount Due"]
        if field in ["date_of_purchase", "date_of_servicing"]:
            records = [
                (
                    rec[0], rec[1], datetime.strptime(rec[2], '%Y-%m-%d').strftime('%d-%m-%Y'), rec[3],
                    rec[4], datetime.strptime(rec[5], '%Y-%m-%d').strftime('%d-%m-%Y'), rec[6], rec[7]
                )
                for rec in records
            ]

        while len(records) > 1:
            print("Multiple records found:")
            print(tabulate(records, headers, tablefmt='grid'))
            
            delete_choice = input("Do you want to delete any of these records? (yes/no): ").strip().lower()
            if delete_choice == 'yes':
                delete_record_by_id(records)
                return
            
            exit_choice = input("Do you want to exit the search? (yes/no): ").strip().lower()
            if exit_choice == 'yes':
                return

            field = input("Enter the field to refine search by (name, date of purchase, phone number, address, date of servicing, amount paid, amount due): ").strip().replace(" ", "_")
            if field not in valid_fields:
                print("Invalid field! Please choose a valid field.")
                continue
            value = input(f"Enter the value to search for in {field.replace('_', ' ')}: ")
            query = f"SELECT * FROM ServiceRecords WHERE {field} LIKE ? AND id IN ({','.join(['?' for _ in records])})"
            record_ids = [record[0] for record in records]
            cursor.execute(query, ['%' + value + '%'] + record_ids)
            records = cursor.fetchall()

            if field in ["date_of_purchase", "date_of_servicing"]:
                records = [
                    (
                        rec[0], rec[1], datetime.strptime(rec[2], '%Y-%m-%d').strftime('%d-%m-%Y'), rec[3],
                        rec[4], datetime.strptime(rec[5], '%Y-%m-%d').strftime('%d-%m-%Y'), rec[6], rec[7]
                    )
                    for rec in records
                ]

        if records:
            print("Record found:")
            print(tabulate([records[0]], headers, tablefmt='grid'))
            delete_choice = input("Do you want to delete this record? (yes/no): ").strip().lower()
            if delete_choice == 'yes':
                delete_record_by_id(records)
                return

def delete_record_by_id(records):
    record_ids = [record[0] for record in records]
    while True:
        record_id = input(f"Enter the ID of the record to delete ({record_ids}): ").strip()
        if not record_id.isdigit() or int(record_id) not in record_ids:
            print("Invalid ID! Please enter a valid ID.")
            continue
        cursor.execute("DELETE FROM ServiceRecords WHERE id = ?", (record_id,))
        conn.commit()
        print("Record deleted successfully!")
        break

# Function to view records within a given number of days from a specified date
def view_records_within_days():
    while True:
        date_str = input("Enter a date (DD-MM-YYYY): ")
        try:
            date = datetime.strptime(date_str, '%d-%m-%Y')
            break
        except ValueError:
            print("Invalid date format! Please enter the date in DD-MM-YYYY format.")

    while True:
        try:
            days = int(input("Enter the number of days to view records within: "))
            break
        except ValueError:
            print("Invalid input! Please enter a valid number.")

    start_date = date
    end_date = date + timedelta(days=days)
    start_date_iso = start_date.strftime('%Y-%m-%d')
    end_date_iso = end_date.strftime('%Y-%m-%d')

    cursor.execute("SELECT * FROM ServiceRecords WHERE date_of_servicing BETWEEN ? AND ?", (start_date_iso, end_date_iso))
    records = cursor.fetchall()
    headers = ["ID", "Name", "Date of Purchase", "Phone Number", "Address", "Date of Servicing", "Amount Paid", "Amount Due"]

    if records:
        records = [
            (
                rec[0], rec[1], datetime.strptime(rec[2], '%Y-%m-%d').strftime('%d-%m-%Y'), rec[3],
                rec[4], datetime.strptime(rec[5], '%Y-%m-%d').strftime('%d-%m-%Y'), rec[6], rec[7]
            )
            for rec in records
        ]
        print(tabulate(records, headers, tablefmt='grid'))
    else:
        print("No records found within the given number of days.")

# Main program loop

view_records_within_days()
while True:
    
    print("1. Add a new service record")
    print("2. View all service records")
    print("3. Search for service records")
    print("4. Update a service record")
    print("5. Delete a service record")
    print("6. Exit")
    choice = input("Enter your choice: ")

    if choice == '1':
        add_service_record()
    elif choice == '2':
        view_service_records()
    elif choice == '3':
        search_service_records()
    elif choice == '4':
        update_service_record()
    elif choice == '5':
        delete_service_record()
    elif choice == '6':
        break
    else:
        print("Invalid choice! Please try again.")

# Close the database connection
conn.close()                 
