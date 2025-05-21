import mysql.connector
from mysql.connector import Error
from ReadCSVFiles import readCSVFile
import numpy as np


DBNAME = "dptest"

coeficienti = {
    'A1': None,
    'B1': None,
    'C1': None,
    'A2': None,
    'B2': None,
    'C2': None        
}

phases = {
    'A1': {'value': None, 'type': 'FLOAT'},
    'B1': {'value': None, 'type': 'FLOAT'},
    'C1': {'value': None, 'type': 'FLOAT'},
    'A2': {'value': None, 'type': 'INT'},
    'B2': {'value': None, 'type': 'INT'},
    'C2': {'value': None, 'type': 'STR'}
}

# Store the dictionaries in a dictionary with keys of the same name
DB_tables = {
    'coeficienti': coeficienti,
    'phases': phases
}

# Modify the dictionaries
DB_tables['coeficienti']['A1'] = 234234  # Update 'A1' in the first dictionary (coeficienti)
DB_tables['phases']['A1'] = 123456  # Update 'A1' in the second dictionary (fazeaaa)

# Print the updated dictionaries
print("coeficienti:", DB_tables['coeficienti'])
print("phases:", DB_tables['phases'])


import mysql.connector
from mysql.connector import Error

def writeCoefsToDB(temp_dict, db_name, table_name, host, user, password):
    """
    Saves a dictionary to a MariaDB table.
    
    Args:
        temp_dict (dict): The dictionary to save, e.g., {'A1': {'value': 1.23, 'type': 'FLOAT'}, ...}
        db_name (str): The name of the database.
        table_name (str): The name of the table to save the data to.
        host (str): The MariaDB host.
        user (str): The MariaDB user.
        password (str): The MariaDB password.
    """
    try:
        # Connect to MariaDB
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        cursor = connection.cursor()

        # Check if the table exists
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        table_exists = cursor.fetchone()

        if not table_exists:
            # Create the table if it doesn't exist
            columns = []
            for key, value in temp_dict.items():
                data_type = value['type']
                if data_type == 'FLOAT':
                    columns.append(f"{key} FLOAT")
                elif data_type == 'INT':
                    columns.append(f"{key} INT")
                elif data_type == 'STR':
                    columns.append(f"{key} VARCHAR(255)")
                else:
                    raise ValueError(f"Unsupported data type: {data_type}")

            create_table_query = f"CREATE TABLE {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, {', '.join(columns)})"
            cursor.execute(create_table_query)
            print(f"Table '{table_name}' created successfully.")

        # Prepare the data for insertion
        columns = list(temp_dict.keys())
        values = [temp_dict[key]['value'] for key in columns]

        # Insert or update the data
        placeholders = ', '.join(['%s'] * len(columns))
        insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        cursor.execute(insert_query, values)
        connection.commit()
        print(f"Data inserted/updated in table '{table_name}' successfully.")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MariaDB connection closed.")

# Example usage
phases = {
    'A1': {'value': 1.23, 'type': 'FLOAT'},
    'B1': {'value': 4.56, 'type': 'FLOAT'},
    'C1': {'value': 7.89, 'type': 'FLOAT'},
    'A2': {'value': 10, 'type': 'INT'},
    'B2': {'value': 20, 'type': 'INT'},
    'C2': {'value': 'Hello', 'type': 'STR'}
}

writeCoefsToDB(
    temp_dict=phases,
    db_name="dptest",
    table_name="phases",
    host="localhost",
    user="root",
    password="your_password"
)


def writeCoefsToDB(coeficienti, coeficienti_units, row_names):
    try:
        # Verificăm tipul datelor pentru a le pregăti pentru inserare
        if not isinstance(coefs, list):
            print("Tipul datelor nu este listă.")
            return

        # Verificăm dacă row_names este un string, care trebuie să conțină numele coloanelor
        if not isinstance(row_names, str):
            print("row_names trebuie să fie un șir de caractere.")
            return
        
        # Despărțim numele coloanelor în listă
        columns = [col.strip() for col in row_names.split(",")]

        # Verificăm dacă lista de date are aceeași lungime ca numărul de coloane
        if len(coefs) != len(columns):
            print(f"Numărul de coloane ({len(columns)}) nu se potrivește cu numărul de seturi de date ({len(coefs)}).")
            return
        
        # Pregătim valorile pentru inserare, în fiecare listă din `data` fiind un element care trebuie să fie un float
        values = [(float(val[0]) for val in coefs)]  # Convertim fiecare element într-un tuple de valori (float)

        # Conectare la MySQL
        connection = mysql.connector.connect(
            host='localhost',
            database='dptest',
            user='root',
            password='simtech'
        )

        if connection.is_connected():
            print("Conexiune reușită!")
            cursor = connection.cursor()

            # Construim SQL cu numele coloanelor
            sql = f"INSERT INTO `{table}` ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"
            print(f"SQL Query: {repr(sql)}")  # Afișăm exact cum arată query-ul
            print("Values:", values)  # Afișăm lista de valori inserate

            # Executăm inserarea
            cursor.executemany(sql, values)
            connection.commit()

            print(f"{cursor.rowcount} rânduri inserate cu succes în tabelul `{table}`.")

    except mysql.connector.Error as e:
        print(f"Eroare la MySQL: {e}")
    except TypeError as te:
        print(f"Eroare de tip: {te}")
    except ValueError as ve:
        print(f"Eroare de conversie numerică: {ve}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()



