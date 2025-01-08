import pandas as pd
from fuzzywuzzy import fuzz, process

# Step 1: Load CSV and TXT data
csv_file = 'sales/top 120 best-selling mobile phones.csv'
txt_file = 'phone_links.txt'

# Read the CSV
csv_data = pd.read_csv(csv_file)
models = csv_data['Model'].str.strip().str.lower()

# Read the TXT file
with open(txt_file, 'r') as f:
    urls = [line.strip() for line in f.readlines()]

# Step 2: Preprocess the data
# Extract model names from URLs (e.g., xiaomi_mi_2a from URLs)
def extract_model_from_url(url):
    # Extract between 'gsmarena.com/' and '-<ID>.php'
    return url.split('/')[3].split('-')[0]

url_models = [extract_model_from_url(url).replace('_', ' ').lower() for url in urls]

# Step 3: Match Models
results = []  # Store the matches

for model in models:
    # Find the best match using fuzzy logic
    best_match, score = process.extractOne(model, url_models, scorer=fuzz.partial_ratio)
    if score > 75:  # Set a threshold for matching
        matched_url = urls[url_models.index(best_match)]
        results.append((matched_url))

# Step 4: Save Results
with open('matched_models.csv', 'w') as f:
    for r in results:
        f.writelines(r + '\n')

print("Matching completed. Results saved in 'matched_models.csv'.")
