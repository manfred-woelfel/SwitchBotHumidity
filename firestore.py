import os
from google.cloud import firestore

def get_firestore_client():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    local_key = os.path.join(base_dir, "gcp-key.json")

    if os.environ.get("GCP_SA_KEY"):
        temp_key = os.path.join(base_dir, "temp-github-key.json")
        with open(temp_key, "w", encoding="utf-8") as f:
            f.write(os.environ["GCP_SA_KEY"])
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_key
    elif os.path.exists(local_key):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_key
    else:
        print(f"[DEBUG] Could not find key at: {local_key}")
        return None

    return firestore.Client()