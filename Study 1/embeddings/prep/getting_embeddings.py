import csv
import logging
from dotenv import load_dotenv
import os
from openai import AzureOpenAI, OpenAI

load_dotenv()

def _sanitize(v: str) -> str:
    return (v or "").strip().strip('"').strip("'")

# pick up keys/azure config
openai_key = _sanitize(os.getenv("OPENAI_API_KEY"))
azure_key = _sanitize(os.getenv("AZURE_OPENAI_KEY"))
azure_endpoint = _sanitize(os.getenv("AZURE_ENDPOINT"))

if openai_key and openai_key.startswith("sk-"):
    # OpenAI platform: only key required
    client = OpenAI(api_key=openai_key)
    model_name = "text-embedding-3-large"
elif azure_key:
    # Azure OpenAI: use AzureOpenAI client
    client = AzureOpenAI(
        api_version="2024-12-01-preview",
        azure_endpoint=azure_endpoint,
        api_key=azure_key,
    )
    model_name = "text-embedding-3-large"  # your Azure deployment name
else:
    raise SystemExit(
        "Missing configuration. Either set OPENAI_API_KEY (sk-...) for OpenAI, "
        "or set AZURE_OPENAI_KEY + AZURE_ENDPOINT for Azure."
    )

# ensure log directory exists before configuring logging
logfile = 'Study 3/embeddings/output/action_embedding_log.log'
os.makedirs(os.path.dirname(logfile), exist_ok=True)

logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def get_embedding(text):
    try:
        response = client.embeddings.create(input=[text], model=model_name)
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        logging.error(f"Error embedding text starting with {text[:30]}: {e}")
        return []

def main():
    input_file = 'Study 3/embeddings/data/actual_actions.csv'
    output_file = 'Study 3/embeddings/output/actual_actions_embedded.csv'

    with open(input_file, newline='', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['embedding']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for idx, row in enumerate(reader, start=1):
            text = row.get('action', '')
            if not text.strip():
                logging.warning(f"Row {idx} has empty 'action'. Skipping embedding.")
                row['embedding'] = ""
            else:
                embedding = get_embedding(text)
                row['embedding'] = embedding
                logging.info(f"Row {idx} embedded.")

            writer.writerow(row)

if __name__ == "__main__":
    main()