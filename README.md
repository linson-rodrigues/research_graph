
# **Agentic Research Graph**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Graph%20DB-blue?logo=postgresql)](https://www.postgresql.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-orange?logo=openai)](https://platform.openai.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Agent%20Pipeline-green)](https://python.langchain.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

> An intelligent, LLM-driven system that **reads research papers**, **extracts scientific concepts**, and structurally **maps the evolution of ideas** in the Gaussian Splatting ecosystem.

---

# **Knowledge Graph Preview**

![Knowledge Graph Visualization](./image.png)

This visualization captures **424 nodes**, **442 edges**, and relationships extracted from **48+ Gaussian Splatting & NeRF-related papers**.

---

# **Table of Contents**

* [Overview](#overview)
* [Core Capabilities](#core-capabilities)
* [System Output Summary](#system-output-summary)
* [System Architecture](#system-architecture)
* [Technology Stack](#technology-stack)
* [Design Principles](#design-principles)
* [How to Run](#how-to-run)
* [Future Enhancements](#future-enhancements)
* [Conclusion](#conclusion)
* [Contact](#contact)

---

# 🌐 **Overview**

This project builds an **agentic pipeline** that autonomously:

* Reads & parses academic PDFs
* Extracts scientific **entities** (Methods, Metrics, Concepts, Datasets, Papers, Authors)
* Identifies **semantic relationships**
* Constructs a **knowledge graph** in PostgreSQL
* Visualizes it in an interactive PyVis graph

It moves beyond citation graphs — instead uncovering *true scientific meaning* behind paper-to-paper and method-to-method connections.

### Extracted Relationship Types

* **IMPROVES_ON**
* **EXTENDS**
* **USES**
* **EVALUATED_ON**
* **ACHIEVES**

Examples:

```
EAGLES --(IMPROVES_ON)--> 3D Gaussian Splatting  
3DGS --(IMPROVES_ON)--> NeRF  
MobileNeRF --(ACHIEVES)--> Interactive Frame Rates  
```

---

# **Core Capabilities**

### **Semantic Entity Extraction**

Automatically extracts central research concepts:

* Methods
* Concepts
* Metrics
* Datasets
* Authors
* Papers

### **Relationship Extraction**

Identifies how ideas relate across papers using an LLM-driven reasoning pipeline.

### **Strict SQL Schema**

* UUID primary keys
* JSONB metadata
* ON DELETE CASCADE
* Idempotent `get_or_create` logic

### **Interactive Knowledge Graph**

PyVis HTML visualization featuring:

* Hover tooltips
* Zoom/pan
* Colored node types
* Evidence-backed edges

---

# **System Output Summary**

From the Gaussian Splatting corpus:

```
Papers:            48+
Nodes:             424
Edges:             442
```

Entities are normalized and deduplicated (e.g., "NeRF" = "Neural Radiance Fields").

---

# **System Architecture**

<details>
<summary> <strong>Click to Expand Architecture Diagram</strong></summary>

<br>

![System Architecture](./architecture-diagram.png)

</details>

### Agent Pipeline (Combined Overview)

1. **PDF Reader (PyPDF)**
   Extracts raw text from PDFs, sanitizes input.

2. **SectionSplitterAgent**
   Identifies Title, Abstract, Conclusion, and key sections.

3. **EntityExtractionAgent**
   Extracts Methods, Concepts, Metrics, Datasets, and Paper meta-nodes.

4. **RelationExtractionAgent**
   Determines semantic relationships between extracted entities.

5. **ValidationAgent**
   Deduplicates, normalizes, and enforces graph consistency.

6. **Storage Layer (PostgreSQL)**
   Inserts nodes/edges with UUIDs and JSONB metadata.

7. **Visualization Layer (PyVis)**
   Generates `knowledge_graph.html`, an interactive representation.

---

# **Technology Stack**

### **Languages & Frameworks**

* Python 3.9+
* LangChain
* OpenAI GPT-4o

### **Database Layer**

* PostgreSQL
* JSONB fields for flexible metadata
* Future-proof for pgvector embeddings

### **Visualization**

* NetworkX
* PyVis

### **Parsing**

* PyPDF

---

# **Design Principles**

### Agentic Reasoning (Chain-of-Thought)

LLM workflow:

1. Understand core idea of paper
2. Normalize synonyms (NeRF ↔ Neural Radiance Fields)
3. Produce structured JSON (nodes + edges)

### Security & Data Integrity

* UUID identity
* Idempotent operations
* Cascading deletes
* Clean schema
* Text sanitization to prevent encoding failures

### Strict Schema for Controlled Ontology Growth

Nodes are typed (`Concept`, `Method`, `Metric`, `Dataset`, `Author`, `Paper`)
Edges enforce scientific meaning.

---

# ▶**How to Run**

### 1. Clone the repository

```bash
git clone https://github.com/linson-rodrigues/research-graph.git
cd research-graph
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure `.env`

```ini
DATABASE_URL=postgresql://user:password@localhost:5432/research_graph
OPENAI_API_KEY=sk-proj-...
```

### 4. Initialize the database

```bash
python reset_db.py
```

### 5. Run the ingestion pipeline

```bash
python main.py
```

### 6. Visualize the graph

```bash
python visualize_interactive.py
```

This opens `knowledge_graph.html` automatically.

---

# **Future Enhancements**

### 1. **Semantic Entity Resolution (pgvector)**

Automatically merge:

* “3DGS”
* “Gaussian Splatting”
* “3D Gaussian Splatting”

### 2. **Parallel PDF Processing**

Using Dockerized workers + Redis queues.

### 3. **Full Web UI**

React Flow / Graphology:

* Interactive inspectors
* Evidence view
* Expand-on-click

### 4. **Continuous Research Ingestion**

Auto-pull new papers from arXiv (`cs.CV`).

---

# **Conclusion**

This project demonstrates how **Agentic LLM pipelines**, combined with graph-structured data systems, can:

* extract meaningful scientific knowledge
* reveal hidden relationships across research
* and turn PDFs into a **navigable map of scientific evolution**

starting with the Gaussian Splatting ecosystem — and scalable across domains.

---

# **Contact**

**Author:** Linson Rodrigues
**GitHub:** [https://github.com/linson-rodrigues](https://github.com/linson-rodrigues)

---

