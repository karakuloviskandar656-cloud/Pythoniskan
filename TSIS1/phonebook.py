import psycopg2
import json
import csv
from config import load_config

def connect_db():
    return psycopg2.connect(**load_config())

# ---------- Existing functions from Practice 8 ----------
def search_by_pattern(pattern):
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

def delete_contact_by_name_or_phone(search_term):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL delete_contact_by_name_or_phone(%s)", (search_term,))
            conn.commit()

# ---------- New TSIS1 procedures ----------
def add_phone_proc(contact_name, phone, ptype='mobile'):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL add_phone(%s, %s, %s)", (contact_name, phone, ptype))
            conn.commit()

def move_to_group_proc(contact_name, group_name):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("CALL move_to_group(%s, %s)", (contact_name, group_name))
            conn.commit()

def extended_search(query):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (query,))
            return cur.fetchall()

# ---------- Helper functions ----------
def list_groups():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM groups ORDER BY id")
            return cur.fetchall()

def filter_by_group(group_name):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, c.surname, c.email, c.birthday,
                       g.name AS group_name,
                       string_agg(p.phone || ' (' || p.type || ')', ', ') AS phones
                FROM contacts c
                JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON c.id = p.contact_id
                WHERE g.name = %s
                GROUP BY c.id, g.name
                ORDER BY c.id
            """, (group_name,))
            return cur.fetchall()

# ---------- JSON import / export ----------
def export_json(filename='contacts.json'):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, c.surname, c.email, c.birthday,
                       g.name AS group_name,
                       array_agg(json_build_object('phone', p.phone, 'type', p.type))
                           FILTER (WHERE p.phone IS NOT NULL) AS phones
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON c.id = p.contact_id
                GROUP BY c.id, g.name
                ORDER BY c.id
            """)
            rows = cur.fetchall()
    contacts = []
    for row in rows:
        contacts.append({
            'id': row[0],
            'name': row[1],
            'surname': row[2],
            'email': row[3],
            'birthday': str(row[4]) if row[4] else None,
            'group': row[5],
            'phones': row[6] if row[6] else []
        })
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)
    print(f"Exported {len(contacts)} contacts to {filename}")

def import_json(filename='contacts.json'):
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    with connect_db() as conn:
        with conn.cursor() as cur:
            for item in data:
                cur.execute("SELECT id FROM contacts WHERE name = %s", (item['name'],))
                existing = cur.fetchone()
                if existing:
                    answer = input(f"Contact '{item['name']}' already exists. Overwrite? (y/n): ")
                    if answer.lower() != 'y':
                        continue
                    cur.execute("""
                        UPDATE contacts SET surname = %s, email = %s, birthday = %s
                        WHERE name = %s
                    """, (item.get('surname'), item.get('email'), item.get('birthday'), item['name']))
                else:
                    cur.execute("""
                        INSERT INTO contacts (name, surname, email, birthday, group_id)
                        SELECT %s, %s, %s, %s, id FROM groups WHERE name = %s
                    """, (item['name'], item.get('surname'), item.get('email'), item.get('birthday'), item.get('group')))
                conn.commit()
    print(f"Imported from {filename}")

# ---------- CSV import (extended, fixed) ----------
def import_csv(filename='contacts.csv'):
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        with connect_db() as conn:
            with conn.cursor() as cur:
                for row in reader:
                    name = row['name']
                    cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
                    existing = cur.fetchone()
                    if existing:
                        answer = input(f"Contact '{name}' already exists. Overwrite? (y/n): ")
                        if answer.lower() != 'y':
                            continue   # skip completely, no phone added
                        cur.execute("""
                            UPDATE contacts SET surname = %s, email = %s, birthday = %s
                            WHERE name = %s
                        """, (row.get('surname'), row.get('email'), row.get('birthday'), name))
                        conn.commit()
                        contact_id = existing[0]
                    else:
                        group_name = row.get('group', 'Other')
                        cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                        group_id = cur.fetchone()
                        if not group_id:
                            cur.execute("INSERT INTO groups (name) VALUES (%s) ON CONFLICT (name) DO NOTHING", (group_name,))
                            conn.commit()
                            cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
                            group_id = cur.fetchone()
                        cur.execute("""
                            INSERT INTO contacts (name, surname, email, birthday, group_id)
                            VALUES (%s, %s, %s, %s, %s) RETURNING id
                        """, (name, row.get('surname'), row.get('email'), row.get('birthday'), group_id[0]))
                        contact_id = cur.fetchone()[0]
                        conn.commit()
                    # Add phone if present
                    if row.get('phone'):
                        phone_type = row.get('phone_type', 'mobile')
                        cur.execute("""
                            INSERT INTO phones (contact_id, phone, type)
                            VALUES (%s, %s, %s)
                        """, (contact_id, row['phone'], phone_type))
                        conn.commit()
    print(f"Imported from {filename}")

# ---------- Paginated console loop ----------
def paginated_view():
    per_page = 3
    offset = 0
    while True:
        rows = paginate_contacts(per_page, offset)
        if not rows:
            print("No more contacts.")
            break
        for r in rows:
            print(f"{r[0]}: {r[1]} {r[2] or ''} - {r[3]}")
        print(f"\nPage {offset//per_page + 1}. [N]ext, [P]rev, [Q]uit")
        cmd = input().strip().lower()
        if cmd == 'n' and len(rows) == per_page:
            offset += per_page
        elif cmd == 'p' and offset > 0:
            offset -= per_page
        elif cmd == 'q':
            break

# ---------- Sorted listing ----------
def list_sorted(sort_by='name'):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.name, c.surname, c.email, c.birthday,
                       g.name AS group_name,
                       string_agg(p.phone || ' (' || p.type || ')', ', ') AS phones,
                       c.created_at
                FROM contacts c
                LEFT JOIN groups g ON c.group_id = g.id
                LEFT JOIN phones p ON c.id = p.contact_id
                GROUP BY c.id, g.name
                ORDER BY
                    CASE %s
                        WHEN 'name' THEN c.name
                        WHEN 'birthday' THEN c.birthday::text
                        WHEN 'date' THEN c.created_at::text
                        ELSE c.name
                    END
            """, (sort_by,))
            return cur.fetchall()

# ---------- Main menu ----------
def main():
    while True:
        print("\n--- TSIS 1 PhoneBook ---")
        print("1. Search by pattern (name/surname/phone)")
        print("2. Search extended (email, phones too)")
        print("3. Filter by group")
        print("4. Add phone number to existing contact")
        print("5. Move contact to group")
        print("6. Paginated view (next/prev)")
        print("7. Sort by name / birthday / date added")
        print("8. Upsert contact (simple)")
        print("9. Delete contact by name/phone")
        print("10. Export to JSON")
        print("11. Import from JSON")
        print("12. Import from CSV (extended)")
        print("0. Exit")
        choice = input("Choice: ").strip()

        if choice == '1':
            pattern = input("Pattern: ")
            for r in search_by_pattern(pattern):
                print(r)
        elif choice == '2':
            query = input("Query: ")
            for r in extended_search(query):
                print(r)
        elif choice == '3':
            groups = list_groups()
            for g in groups:
                print(f"{g[0]}. {g[1]}")
            gname = input("Group name: ")
            for r in filter_by_group(gname):
                print(r)
        elif choice == '4':
            name = input("Contact name: ")
            phone = input("Phone: ")
            ptype = input("Type (home/work/mobile): ")
            add_phone_proc(name, phone, ptype)
            print("Phone added.")
        elif choice == '5':
            name = input("Contact name: ")
            group = input("Group name: ")
            move_to_group_proc(name, group)
            print("Moved.")
        elif choice == '6':
            paginated_view()
        elif choice == '7':
            print("Sort by: name / birthday / date")
            sort_option = input().strip()
            rows = list_sorted(sort_option)
            for r in rows:
                print(r)
        elif choice == '8':
            name = input("Name: ")
            phone = input("Phone: ")
            surname = input("Surname (optional): ")
            upsert_contact(name, phone, surname)
            print("Done.")
        elif choice == '9':
            term = input("Delete by name or phone: ")
            delete_contact_by_name_or_phone(term)
            print("Deleted.")
        elif choice == '10':
            export_json()
        elif choice == '11':
            import_json()
        elif choice == '12':
            filename = input("CSV filename: ")
            import_csv(filename)
        elif choice == '0':
            break
        else:
            print("Invalid choice")

if __name__ == '__main__':
    main()