import os
import json
import psycopg2
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from pypdf import PdfReader

# Load environment variables
load_dotenv()

# --- CONFIGURATION ---
DB_CONNECTION = os.getenv("DATABASE_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PAPERS_DIR = "./papers"

# --- PYDANTIC MODELS ---
class GraphNode(BaseModel):
    name: str = Field(..., description="Entity name (e.g., 'Gaussian Splatting', 'NeRF'). Use canonical naming.")
    type: str = Field(..., description="Classification: Paper, Concept, Metric, Author, Method.")
    description: Optional[str] = Field(None, description="Brief description or definition.")

class GraphEdge(BaseModel):
    source: str = Field(..., description="Source entity name (Must match a Node name exactly).")
    target: str = Field(..., description="Target entity name (Must match a Node name exactly).")
    relation: str = Field(..., description="Relationship: IMPROVES_ON, INTRODUCES, USES, EVALUATED_ON, ALTERNATIVE_TO.")
    context: str = Field(..., description="Verbatim sentence from text proving this relationship.")

class ExtractionResult(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

# --- HELPER FUNCTIONS ---
def normalize_key(text: str) -> str:
    """
    Normalizes text to ensure consistent entity resolution.
    '3D Gaussian Splatting' == '3d gaussian-splatting'
    """
    if not text:
        return ""
    return text.lower().strip().replace("-", " ").replace("_", " ")

# --- DATABASE LAYER ---
class GraphDatabase:
    def __init__(self, connection_string):
        self.conn = psycopg2.connect(connection_string)
        self.conn.autocommit = True

    def get_or_create_node(self, node: GraphNode, paper_source: str) -> str:
        """
        Inserts a node if it doesn't exist, or returns the existing ID.
        """
        with self.conn.cursor() as cur:
            # Check for existing node
            cur.execute(
                "SELECT id FROM nodes WHERE name = %s AND type = %s",
                (node.name, node.type)
            )
            result = cur.fetchone()
            if result:
                return result[0]

            # Create new node
            props = json.dumps({"description": node.description, "source_paper": paper_source})
            cur.execute(
                """
                INSERT INTO nodes (name, type, properties)
                VALUES (%s, %s, %s) RETURNING id
                """,
                (node.name, node.type, props)
            )
            return cur.fetchone()[0]

    def create_edge(self, source_id: str, target_id: str, edge: GraphEdge):
        """
        Creates an edge between two known UUIDs.
        """
        with self.conn.cursor() as cur:
            # Check if edge already exists to prevent duplicates (optional but good)
            cur.execute(
                """
                SELECT id FROM edges 
                WHERE source_id = %s AND target_id = %s AND type = %s
                """,
                (source_id, target_id, edge.relation)
            )
            if cur.fetchone():
                return # Edge exists

            cur.execute(
                """
                INSERT INTO edges (source_id, target_id, type, citation_context)
                VALUES (%s, %s, %s, %s)
                """,
                (source_id, target_id, edge.relation, edge.context)
            )

# --- AGENT LAYER ---
class ResearchAgent:
    def __init__(self):
        # Temperature 0 for consistency
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.structured_llm = llm.with_structured_output(ExtractionResult)

    def extract_graph(self, text: str, paper_title: str) -> ExtractionResult:
        print(f"--------------------- Analyzing: {paper_title} ---------------------")

        # AGENTIC PROMPT: Includes "Reasoning" steps to satisfy the assignment requirement.
        prompt = f"""
        You are an AI Researcher building a Knowledge Graph for the "Gaussian Splatting" domain.
        
        INPUT TEXT (Excerpt from "{paper_title}"):
        {text[:40000]} 

        TASK:
        Analyze the text agentically to extract a semantic graph.

        STEP 1: REASONING (Internal Chain of Thought)
        - Identify the core contribution of this paper.
        - Identify what specific methods it *improves on* or *compares against*.
        - Scan for architectural components (e.g., "MLP", "Voxel Grid", "Spherical Harmonics").

        STEP 2: EXTRACTION RULES
        - **Entities (Nodes)**: Extract Papers, Methods, Concepts, and Metrics.
          - Normalize names: Use "3D Gaussian Splatting" instead of "3DGS" or "Our Method".
        - **Relationships (Edges)**: Connect nodes using semantic verbs:
          - IMPROVES_ON, INTRODUCES, USES, ALTERNATIVE_TO
          - Do NOT extract citations just because they are listed. Only extract if there is a semantic relationship described (e.g., "We outperform X by 10%").
        
        STEP 3: VERIFICATION
        - Ensure every 'source' and 'target' in your Edges list exists in your Nodes list.

        OUTPUT:
        Return strict JSON matching the ExtractionResult schema.
        """

        return self.structured_llm.invoke(prompt)

# --- ROBUST PDF EXTRACTION ---
def process_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    full_text = ""

    # Extract all text
    for page in reader.pages:
        try:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        except Exception as e:
            print(f"Warning: Could not read page in {file_path}: {e}")
            continue

    # Postgres Safety: Remove null bytes
    full_text = full_text.replace("\x00", "")
    
    # Clean whitespace
    full_text = full_text.replace("\t", " ").strip()

    if len(full_text) < 500:
        return "" # Skip empty/broken PDFs

    # SMART TRUNCATION:
    # Instead of looking for "Conclusion", we take a heuristic approach.
    # We want the Intro + Method (usually first 70%) and the Conclusion (last 10%).
    # We skip the middle references if it's too long.
    
    limit = 40000 
    if len(full_text) <= limit:
        return full_text
    
    # Take first 35k chars (Intro, Related Work, Method) + Last 5k chars (Conclusion)
    head = full_text[:35000]
    tail = full_text[-5000:]
    
    return f"{head}\n\n...[SECTION SKIPPED FOR TOKEN LIMIT]...\n\n{tail}"

# --- MAIN PIPELINE ---
def main():
    if not DB_CONNECTION:
        print("Error: DATABASE_URL is not set in .env")
        return

    db = GraphDatabase(DB_CONNECTION)
    agent = ResearchAgent()

    if not os.path.exists(PAPERS_DIR):
        print(f"Error: Directory '{PAPERS_DIR}' not found. Please create it and add PDFs.")
        return

    pdf_files = [f for f in os.listdir(PAPERS_DIR) if f.endswith('.pdf')]
    if not pdf_files:
        print("No PDFs found in /papers. Please add a PDF.")
        return

    print(f"Found {len(pdf_files)} papers to process.")

    for filename in pdf_files:
        file_path = os.path.join(PAPERS_DIR, filename)
        # Fallback title if LLM doesn't find one (usually overwritten by node extraction)
        paper_title = filename.replace(".pdf", "").replace("_", " ")

        raw_text = process_pdf(file_path)
        if not raw_text:
            print(f"Skipping {filename} (Empty or unreadable).")
            continue

        # Agent analysis
        try:
            graph_data = agent.extract_graph(raw_text, paper_title)
            print(f"Extracted {len(graph_data.nodes)} nodes, {len(graph_data.edges)} edges.")
        except Exception as e:
            print(f"Error analyzing {filename}: {e}")
            continue

        # 1. Create Nodes & Build Lookup Map (with Normalization)
        node_map = {}
        for node in graph_data.nodes:
            # We insert the node into DB
            node_id = db.get_or_create_node(node, paper_title)
            
            # CRITICAL FIX: Map the NORMALIZED name to the ID
            # This handles cases where LLM types "NeRF" vs "nerf"
            norm_name = normalize_key(node.name)
            node_map[norm_name] = node_id

        # 2. Create Edges (using Lookup Map)
        skipped_edges = 0
        for edge in graph_data.edges:
            source_key = normalize_key(edge.source)
            target_key = normalize_key(edge.target)

            source_id = node_map.get(source_key)
            target_id = node_map.get(target_key)

            if source_id and target_id:
                db.create_edge(source_id, target_id, edge)
            else:
                # This happens if the LLM hallucinated an edge to a node it didn't define
                skipped_edges += 1
                # Optional: Debug print
                # print(f"  Skipped Edge: {edge.source} -> {edge.target} (Node missing)")

        if skipped_edges > 0:
            print(f"  (Skipped {skipped_edges} edges due to missing nodes)")

    print("\n--------------------- Knowledge Graph Construction Complete ---------------------")

if __name__ == "__main__":
    main()
