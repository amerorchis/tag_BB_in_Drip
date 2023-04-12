import requests
import json

def chunk_names(names, email, batch):
    chunks = [names[i:i+25] for i in range(0, len(names), 25)]
    
    # Make a POST request for each chunk
    for i, chunk in enumerate(chunks):
        batch += f" ({i+1} of {len(chunks)})"
        payload = {"names": chunk, "batch": batch, "email":email}
        r = requests.post("https://tag-constit.vercel.app", data=json.dumps(payload))
    
    return "All chunks posted successfully"