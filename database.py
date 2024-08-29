import sqlite3

def read_sqlite_file(file_path):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(file_path)
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Get the list of tables in the database
        cursor.execute("SELECT name FROM config WHERE type='table';")
        tables = cursor.fetchall()
        
        # Print the tables and their contents
        for table in tables:
            table_name = table[0]
            print(f"Table: {table_name}")
            
            # Get all rows from the table
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            print("Columns:", column_names)
            
            # Print each row
            for row in rows:
                print(row)
            
            print("\n")
        
        # Close the connection
        conn.close()
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

read_sqlite_file('/database/database.db')
