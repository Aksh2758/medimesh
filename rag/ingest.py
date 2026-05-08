"""
Run once: python rag/ingest.py
Loads WHO IMCI guidelines and drug interactions into ChromaDB.
"""
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from config import CHROMA_DB_PATH

def ingest():
    print("Initialising ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # ── WHO IMCI Guidelines ──────────────────────────────────────────
    print("Loading WHO IMCI guidelines...")
    imci_col = client.get_or_create_collection(
        name="who_imci",
        metadata={"hnsw:space": "cosine"}
    )

    with open("data/who_imci_guidelines.json") as f:
        imci_data = json.load(f)

    imci_col.upsert(
        ids=[item["id"] for item in imci_data],
        documents=[item["text"] for item in imci_data],
        metadatas=[
            {"category": item["category"], "source": item["source"]}
            for item in imci_data
        ]
    )
    print(f"   Done: {len(imci_data)} IMCI guideline chunks loaded")

    # ── Drug Interactions ────────────────────────────────────────────
    print("Loading drug interactions...")
    drug_col = client.get_or_create_collection(
        name="drug_interactions",
        metadata={"hnsw:space": "cosine"}
    )

    with open("data/drug_interactions.json") as f:
        drug_data = json.load(f)["interactions"]

    drug_col.upsert(
        ids=[f"drug_{i:03d}" for i, _ in enumerate(drug_data)],
        documents=[
            f"{item['drug_a']} + {item['drug_b']}: {item['effect']}"
            for item in drug_data
        ],
        metadatas=[
            {
                "drug_a": item["drug_a"],
                "drug_b": item["drug_b"],
                "severity": item["severity"],
                "action": item["action"]
            }
            for item in drug_data
        ]
    )
    print(f"   Done: {len(drug_data)} drug interaction pairs loaded")

    print("\nChromaDB ingestion complete!")
    print(f"   Database saved to: {CHROMA_DB_PATH}")
    print(f"   Collections: who_imci ({len(imci_data)} docs), drug_interactions ({len(drug_data)} docs)")

if __name__ == "__main__":
    ingest()
