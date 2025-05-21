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
