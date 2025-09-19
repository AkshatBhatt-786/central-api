# --- dependencies ---
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import secrets
import string

# --- Database Connection Function ---
def get_db_connection():
    """Establishes and returns a connection to the Supabase database."""
    try:
        conn = psycopg2.connect(os.getenv('SUPABASE_DB_URI'))
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

# --- Helper Function: Generate Secure License Key ---
def generate_secure_license_key(prefix="PREP", block_size=4, blocks=4):
    """
    Generates a cryptographically secure random license key.
    Format: PREFIX-ABCD-1234-EF56
    """
    alphabet = string.ascii_uppercase + string.digits
    # Remove ambiguous characters like 0, O, 1, I for clarity
    alphabet = ''.join(c for c in alphabet if c not in '0O1I')
    
    key_blocks = []
    for _ in range(blocks):
        block = ''.join(secrets.choice(alphabet) for _ in range(block_size))
        key_blocks.append(block)
    
    return f"{prefix}-{'-'.join(key_blocks)}"

# --- Core Database Operations ---
def get_all_organizations():
    """
    Fetches all organizations from the database.
    Returns a list of organizations or an empty list on error.
    """
    conn = get_db_connection()
    if conn is None:
        return []
        
    try:
        # RealDictCursor returns results as a dictionary (key-value pairs)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # This SQL query joins the organizations table with the license_keys table
        # to get the license_key value, not just its ID.
        query = """
            SELECT o.*, lk.license_key, lk.license_name 
            FROM organizations o 
            LEFT JOIN license_keys lk ON o.current_license_key_id = lk.id;
        """
        cur.execute(query)
        organizations = cur.fetchall()
        cur.close()
        conn.close()
        return organizations
    except Exception as e:
        print(f"Error fetching organizations: {e}")
        return []

def create_organization(org_id, org_name, contact_email, tier, license_name):
    """
    Creates a new organization and generates its first license key in the database.
    This is a complex operation that involves multiple steps wrapped in a transaction.
    Returns the new organization record on success, None on failure.
    """
    conn = get_db_connection()
    if conn is None:
        return None

    try:
        cur = conn.cursor()
        # Generate the secure, random key for the database
        secure_license_key = generate_secure_license_key()

        # Inserting the new license key into the license_keys table
        license_query = """
            INSERT INTO license_keys (license_key, license_name, tier, valid_until)
            VALUES (%s, %s, %s, NOW() + INTERVAL '1 year')
            RETURNING id;
        """
        cur.execute(license_query, (secure_license_key, license_name, tier))
        new_license_id = cur.fetchone()[0] # Get the ID of the newly created license

        # Inserting the new organization, linking it to the license key we just created
        org_query = """
            INSERT INTO organizations (org_id, name, contact_email, subscription_tier, current_license_key_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *;
        """
        cur.execute(org_query, (org_id, org_name, contact_email, tier, new_license_id))
        new_org = cur.fetchone()

        # Commit the transaction (save both changes to the database)
        conn.commit()
        cur.close()
        conn.close()
        
        # Return the results. In a more advanced version, we would do a JOIN to return both org and key details.
        return {
            "org_id": org_id,
            "name": org_name,
            "license_key": secure_license_key, # This is the key to send to the customer
            "license_name": license_name
        }

    except Exception as e:
        # If anything goes wrong, rollback the entire transaction to avoid partial data
        conn.rollback()
        print(f"Error creating organization and license: {e}")
        return None