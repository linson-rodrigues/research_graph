import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def reset_database():
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        conn.autocommit = True
        cur = conn.cursor()

        print("Dropping old tables (Cleaning up)...")
        cur.execute("DROP TABLE IF EXISTS edges;")
        cur.execute("DROP TABLE IF EXISTS nodes;")

        print("Recreating schema...")
        
        # 1. Enable UUID extension
        cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

        # 2. Create Nodes Table
        cur.execute("""
            CREATE TABLE nodes (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                properties JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                CONSTRAINT unique_node_name_type UNIQUE (name, type)
            );
        """)

        # 3. Create Edges Table (With the correct columns!)
        cur.execute("""
            CREATE TABLE edges (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                source_id UUID NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
                target_id UUID NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
                type TEXT NOT NULL,
                citation_context TEXT,
                properties JSONB DEFAULT '{}',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)

        print("Database successfully reset! Tables 'nodes' and 'edges' are ready.")
        cur.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    reset_database()