import psycopg2
from config import load_config

sql_statements = [
    # 1. add_phone procedure
    """
    CREATE OR REPLACE PROCEDURE add_phone(
        p_contact_name VARCHAR,
        p_phone VARCHAR,
        p_type VARCHAR DEFAULT 'mobile'
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        INSERT INTO phones (contact_id, phone, type)
        SELECT c.id, p_phone, p_type
        FROM contacts c
        WHERE c.name = p_contact_name;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Contact % not found', p_contact_name;
        END IF;
    END;
    $$;
    """,

    # 2. move_to_group procedure
    """
    CREATE OR REPLACE PROCEDURE move_to_group(
        p_contact_name VARCHAR,
        p_group_name VARCHAR
    )
    LANGUAGE plpgsql
    AS $$
    DECLARE
        v_group_id INT;
    BEGIN
        INSERT INTO groups (name) VALUES (p_group_name)
        ON CONFLICT (name) DO NOTHING;

        SELECT id INTO v_group_id FROM groups WHERE name = p_group_name;

        UPDATE contacts
        SET group_id = v_group_id
        WHERE name = p_contact_name;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'Contact % not found', p_contact_name;
        END IF;
    END;
    $$;
    """,

    # 3. search_contacts (extended) function
    """
    CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
    RETURNS TABLE(
        id INT,
        name VARCHAR,
        surname VARCHAR,
        email VARCHAR,
        birthday DATE,
        group_name VARCHAR,
        phones TEXT
    )
    LANGUAGE plpgsql
    AS $$
    BEGIN
        RETURN QUERY
        SELECT
            c.id,
            c.name,
            c.surname,
            c.email,
            c.birthday,
            g.name AS group_name,
            string_agg(p.phone || ' (' || p.type || ')', ', ') AS phones
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE
            c.name ILIKE '%' || p_query || '%'
            OR c.surname ILIKE '%' || p_query || '%'
            OR c.email ILIKE '%' || p_query || '%'
            OR EXISTS (
                SELECT 1 FROM phones ph
                WHERE ph.contact_id = c.id
                  AND ph.phone ILIKE '%' || p_query || '%'
            )
        GROUP BY c.id, g.name
        ORDER BY c.id;
    END;
    $$;
    """
]

conn = psycopg2.connect(**load_config())
cur = conn.cursor()
for stmt in sql_statements:
    cur.execute(stmt)
conn.commit()
cur.close()
conn.close()
print("Procedures created successfully.")