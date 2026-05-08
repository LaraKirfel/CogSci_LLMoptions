from openai import AzureOpenAI, OpenAI
import csv
import logging
from dotenv import load_dotenv
import os
import difflib
from difflib import SequenceMatcher

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
    model_name = "gpt-4o-mini"
elif azure_key:
    # Azure OpenAI: use AzureOpenAI client like in utils.py
    client = AzureOpenAI(
        api_version="2024-12-01-preview",
        azure_endpoint=azure_endpoint,
        api_key=azure_key,
    )
    model_name = "gpt-4o"  
else:
    raise SystemExit(
        "Missing configuration. Either set OPENAI_API_KEY (sk-...) for OpenAI, "
        "or set AZURE_OPENAI_KEY + AZURE_ENDPOINT for Azure."
    )

# ensure log directory exists before configuring logging
logfile = 'Study 3/prep/correction_log_human.log'
os.makedirs(os.path.dirname(logfile), exist_ok=True)

logging.basicConfig(
    filename=logfile,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def correct_text(text):
    prompt = f'''
You are a grammar and spelling correction assistant.  
Correct only spelling and grammar mistakes in the following text.  
Change as little as possible — only what's strictly necessary to fix errors.  
Do NOT rephrase, reword, or alter the meaning or tone in any way.  
Keep formatting (line breaks, punctuation) exactly as in the original text, except for correcting errors (e.g., adding missing commas or periods).  
If no correction is needed, return the original text exactly as it is.

Text: {text}
'''
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        corrected_text = response.choices[0].message.content.strip()
        return corrected_text
        
    except Exception as e:
        logging.error(f"Error correcting text starting with {text[:30]}: {e}")
        return text  # fallback: return original text if error occurs

def get_text_diff(original, corrected):
    """Generate a clean diff showing only the changes between original and corrected text."""
    if original == corrected:
        return "No changes"
    
    # For simple cases, use a more readable word-by-word comparison
    original_words = original.split()
    corrected_words = corrected.split()
    
    changes = []
    matcher = SequenceMatcher(None, original_words, corrected_words)
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            old_text = ' '.join(original_words[i1:i2])
            new_text = ' '.join(corrected_words[j1:j2])
            changes.append(f"{old_text} → {new_text}")
        elif tag == 'delete':
            deleted_text = ' '.join(original_words[i1:i2])
            changes.append(f"Removed: {deleted_text}")
        elif tag == 'insert':
            inserted_text = ' '.join(corrected_words[j1:j2])
            changes.append(f"Added: {inserted_text}")
    
    return " | ".join(changes) if changes else "No changes"


def main():
    input_file = 'Study 3/data/Human_responses_3.csv'
    output_file = 'Study 3/data/Human_responses_corrected.csv'

    with open(input_file, newline='', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['cleaned_response', 'diff']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        idx = 0
        for row in reader:
            idx += 1
            # if idx > 100:
            #     break  # stop after first 100 rows
            
            original_text = row.get('response', '')
            if not original_text.strip():
                logging.warning(f"Row {idx} has empty 'response'. Skipping correction.")
                row['cleaned_response'] = original_text
                row['diff'] = "No changes"
            else:
                cleaned_response = correct_text(original_text)
                row['cleaned_response'] = cleaned_response
                row['diff'] = get_text_diff(original_text, cleaned_response)
                
                logging.info(f"Row {idx} corrected.")

            writer.writerow(row)

if __name__ == "__main__":
    main()