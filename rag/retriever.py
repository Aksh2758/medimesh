"""
RAG retrieval functions for MediMesh agents.
Each agent calls these to get relevant evidence before reasoning.
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from config import CHROMA_DB_PATH

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return _client


def query_imci(query: str, n_results: int = 3) -> str:
    """
    Retrieve relevant WHO IMCI guideline chunks for a clinical query.
    Returns a formatted string ready to paste into an agent prompt.
    """
    try:
        col = _get_client().get_collection("who_imci")
        results = col.query(query_texts=[query], n_results=n_results)
        docs = results["documents"][0]
        metas = results["metadatas"][0]

        if not docs:
            return "No relevant IMCI guidelines found."

        output = []
        for doc, meta in zip(docs, metas):
            output.append(
                f"[{meta.get('category', 'general').upper()} — {meta.get('source', '')}]\n{doc}"
            )
        return "\n\n".join(output)

    except Exception as e:
        return f"RAG query failed: {str(e)}. Proceed with clinical reasoning only."


def query_drug_interactions(drugs: list[str]) -> str:
    """
    Check a list of drug names against the interaction database.
    Returns flagged interactions as a formatted string.
    """
    if not drugs:
        return "No drugs provided for interaction check."

    try:
        col = _get_client().get_collection("drug_interactions")

        # Build a natural language query from the drug list
        query = " ".join(drugs) + " drug interaction"
        results = col.query(query_texts=[query], n_results=5)

        docs = results["documents"][0]
        metas = results["metadatas"][0]

        if not docs:
            return "No significant drug interactions found in database."

        flags = []
        drug_names_lower = [d.lower() for d in drugs]

        for doc, meta in zip(docs, metas):
            da = meta.get("drug_a", "").lower()
            db = meta.get("drug_b", "").lower()

            # Only flag if both drugs in the pair match something in the input list
            # (fuzzy: check if drug name is a substring)
            a_match = any(da in d or d in da for d in drug_names_lower)
            b_match = any(db in d or d in db for d in drug_names_lower)

            if a_match or b_match:
                flags.append(
                    f"⚠️ [{meta.get('severity', 'UNKNOWN')} INTERACTION] "
                    f"{meta.get('drug_a', '')} + {meta.get('drug_b', '')}\n"
                    f"   Effect: {doc}\n"
                    f"   Action: {meta.get('action', '')}"
                )

        if not flags:
            return "No interactions detected for the specified drugs."

        return "\n\n".join(flags)

    except Exception as e:
        return f"Drug interaction check failed: {str(e)}."
