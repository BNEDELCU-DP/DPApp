import mysql.connector
from mysql.connector import Error

DBNAME = "dptest"

# Define database tables using nested dictionaries
DB_tables = {
    "coeffs": {
        "A1": {"value": None, "type": "FLOAT"},
        "B1": {"value": None, "type": "FLOAT"},
        "C1": {"value": None, "type": "FLOAT"},
        "A2": {"value": None, "type": "INT"},
        "B2": {"value": None, "type": "INT"},
        "C2": {"value": None, "type": "STR"},
    },
    "phases": {
        "A1": {"value": None, "type": "FLOAT"},
        "B1": {"value": None, "type": "FLOAT"},
        "C1": {"value": None, "type": "FLOAT"},
        "A2": {"value": None, "type": "INT"},
        "B2": {"value": None, "type": "INT"},
        "C2": {"value": None, "type": "STR"},
    },
    "phases2": {
        "A1": {"value": None, "type": "FLOAT"},
        "B1": {"value": None, "type": "FLOAT"},
        "C1": {"value": None, "type": "FLOAT"},
        "A2": {"value": None, "type": "INT"},
        "B2": {"value": None, "type": "INT"},
        "C2": {"value": None, "type": "STR"},
    },    
}

# Modify some values
DB_tables["coeffs"]["A1"]["value"] = 234234  # Update 'A1' in coeficienti
DB_tables["phases"]["A1"]["value"] = 123456  # Update 'A1' in phases
DB_tables["phases2"]["A2"]["value"] = 3456   # Update 'A2' in phases

# Print updated dictionaries
print(DB_tables)

#print("Updated coeffs:", DB_tables["coeffs"])
#print("Updated phases:", DB_tables["phases"])


def writeCoefsToDB(temp_dict, db_name, table_name, host, user, password):
    """
    Saves a nested dictionary to a MySQL table.

    Args:
        temp_dict (dict): Dictionary structured as {'A1': {'value': 1.23, 'type': 'FLOAT'}, ...}
        db_name (str): Database name.
        table_name (str): Table name.
        host (str): Database host.
        user (str): Database user.
        password (str): Database password.
    """
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(
            host=host, user=user, password=password, database=db_name
        )
        cursor = connection.cursor()

        # Check if the table exists
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        table_exists = cursor.fetchone()

        if not table_exists:
            # Create table dynamically based on the dictionary structure
            columns = []
            for key, value in temp_dict.items():
                data_type = value["type"]
                if data_type == "FLOAT":
                    columns.append(f"{key} FLOAT")
                elif data_type == "INT":
                    columns.append(f"{key} INT")
                elif data_type == "STR":
                    columns.append(f"{key} VARCHAR(255)")
                else:
                    raise ValueError(f"Unsupported data type: {data_type}")

            create_table_query = (
                f"CREATE TABLE {table_name} (id INT AUTO_INCREMENT PRIMARY KEY, {', '.join(columns)})"
            )
            cursor.execute(create_table_query)
            print(f"Table '{table_name}' created successfully.")

        # Prepare data for insertion
        columns = list(temp_dict.keys())
        values = [temp_dict[key]["value"] for key in columns]

        # Insert data, handling NULL values correctly
        placeholders = ", ".join(["%s"] * len(columns))
        insert_query = (
            f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        )
        cursor.execute(insert_query, values)
        connection.commit()
        print(f"Data inserted into table '{table_name}' successfully.")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Database connection closed.")


# Example usage
writeCoefsToDB(
    temp_dict=DB_tables["coeffs"],
    db_name=DBNAME,
    table_name="coeffs",
    host="localhost",
    user="root",
    password="simtech",
)

writeCoefsToDB(
    temp_dict=DB_tables["phases"],
    db_name=DBNAME,
    table_name="phases",
    host="localhost",
    user="root",
    password="simtech",
)

writeCoefsToDB(
    temp_dict=DB_tables["phases2"],
    db_name=DBNAME,
    table_name="phases2",
    host="localhost",
    user="root",
    password="simtech",
)
