import os
import psycopg2
from dotenv import load_dotenv

# Load credentials
load_dotenv()

def check_database():
    try:
        # Connect to Postgres
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()

        # 1. Count Nodes
        cur.execute("SELECT count(*) FROM nodes;")
        node_count = cur.fetchone()[0]

        # 2. Count Edges
        cur.execute("SELECT count(*) FROM edges;")
        edge_count = cur.fetchone()[0]

        print(f"✅ STATUS CHECK:")
        print(f"Nodes in DB: {node_count}")
        print(f"Edges in DB: {edge_count}")

        if node_count == 0:
            print("⚠️ WARNING: Database is empty. Did main.py run successfully?")
            return

        # 3. Show Sample Nodes
        print("\n--- 🔍 Sample Nodes ---")
        cur.execute("SELECT name, type FROM nodes LIMIT 5;")
        for name, type_ in cur.fetchall():
            print(f"• {name} [{type_}]")

        # 4. Show Sample Edges (with names resolved)
        print("\n--- 🔗 Sample Relationships ---")
        query = """
        SELECT source.name, edge.type, target.name 
        FROM edges edge
        JOIN nodes source ON edge.source_id = source.id
        JOIN nodes target ON edge.target_id = target.id
        LIMIT 5;
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        if not rows:
            print("No edges found (Nodes exist, but they aren't connected).")
        
        for source, relation, target in rows:
            print(f"{source} --({relation})--> {target}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error connecting to database: {e}")

if __name__ == "__main__":
    check_database()