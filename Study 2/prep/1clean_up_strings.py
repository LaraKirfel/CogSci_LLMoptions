import pandas as pd 
import re

human = pd.read_csv('Study 3/data/Human_responses.csv')
llm = pd.read_csv('Study 3/data/LLM_responses.csv')

def format_sentence(s):
    if pd.isnull(s): # Handle NaN values 
        return ""
    if not s:
        return ""
    s = s.lstrip('#')  # Remove leading #
    s = s.strip()  # Remove leading and trailing whitespaces
    if not s:  # Check again after stripping
        return ""
    s = s[0].upper() + s[1:]   # Capitalize only the first letter
    if not s.endswith('.'):
        s += '.'
    return s

# Process human responses
human['response'] = human['response'].apply(format_sentence)

# Process LLM responses - split by # and create new rows
llm_expanded = []
for idx, row in llm.iterrows():
    response_text = row['response']
    if pd.isnull(response_text):
        response_text = ""
    
    # Remove <br> tags
    response_text = re.sub(r'<br\s*/?>', '', response_text, flags=re.IGNORECASE)
    
    # Split by # to get individual responses
    responses = re.split(r'#', response_text)
    
    # Filter out empty strings and process each response
    responses = [r.strip() for r in responses if r.strip()]
    
    if not responses:  # If no valid responses after splitting
        llm_expanded.append({
            'response_id': row['response_id'],
            'scenario': row['scenario'],
            'response_number': 1,
            'response': ""
        })
    else:
        for response_num, resp in enumerate(responses, start=1):
            formatted_resp = format_sentence(resp)
            llm_expanded.append({
                'response_id': row['response_id'],
                'scenario': row['scenario'],
                'response_number': response_num,
                'response': formatted_resp
            })

# Create new LLM dataframe with expanded rows
llm = pd.DataFrame(llm_expanded)

# sanity check
print(llm['response_number'].value_counts().sort_index())

human = human[['response_id', 'scenario', 'response_number', 'response']]
llm = llm[['response_id', 'scenario', 'response_number', 'response']]

# Sort the DataFrame by 'scenario' keep unique cleaned responses by scenario
human = human.sort_values(["scenario", "response_id", "response_number"])
llm = llm.sort_values(["scenario", "response_id", "response_number"])

human.to_csv('Study 3/data/Human_responses_3.csv', index=False)
llm.to_csv('Study 3/data/LLM_responses_3.csv', index=False)