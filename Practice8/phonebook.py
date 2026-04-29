import psycopg2
from config import load_config

def connect_db():
    config = load_config()
    return psycopg2.connect(**config)

def search_contacts(pattern):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", (pattern,))
            return cur.fetchall()

def paginate_contacts(limit=10, offset=0):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
            return cur.fetchall()

def upsert_contact(name, phone, surname=None):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL upsert_contact(%s, %s, %s)", (name, phone, surname))
            conn.commit()

def bulk_insert_contacts(names, phones, surnames=None):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM bulk_insert_contacts(%s, %s, %s)", (names, phones, surnames))
            errors = cur.fetchall()
            conn.commit()
            return errors

def delete_contact_by_name_or_phone(search_term):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_contact_by_name_or_phone(%s)", (search_term,))
            conn.commit()

if __name__ == '__main__':
    # 1. Pattern search
    print("1. Pattern search for 'ohn':")
    for row in search_contacts('ohn'):
        print(row)

    # 2. Upsert
    print("\n2. Upsert John Doe:")
    upsert_contact('John', '1234567890', 'Doe')
    print("Done.")
    for row in search_contacts('John'):
        print(row)

    # 3. Bulk insert (with one invalid phone)
    print("\n3. Bulk insert:")
    names = ['Alice', 'Bob', 'Charlie']
    phones = ['+77011234567', 'bad', '9876543210']
    surnames = ['Smith', 'Johnson', 'Brown']
    errors = bulk_insert_contacts(names, phones, surnames)
    print("Incorrect entries:", errors)
    print("All contacts:")
    for row in paginate_contacts(100, 0):
        print(row)

    # 4. Pagination
    print("\n4. First 2 contacts:")
    for row in paginate_contacts(2, 0):
        print(row)

    # 5. Delete
    print("\n5. Delete contacts containing 'Smith':")
    delete_contact_by_name_or_phone('Smith')
    print("Done.")
    for row in paginate_contacts(100, 0):
        print(row)