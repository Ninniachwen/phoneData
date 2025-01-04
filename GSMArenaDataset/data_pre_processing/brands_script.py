# by ML

import pandas as pd

brands_all = 'GSMArenaDataset/web_scrap/brand_links_all.txt'  # List of possible brands
output_file = 'GSMArenaDataset/web_scrap/brand_links.txt'  # List of interesting brands

# Input datasets
datasets = ['sales/top 120 best-selling mobile phones.csv', 'user/user_behavior_dataset.csv']

# Initialize an empty set to store unique brand matches
brand_matches = set()

for dataset in datasets:
    df = pd.read_csv(dataset)

    # Extract unique brands
    if 'Manufacturer' not in df.columns:
        df['Manufacturer'] = df['Device Model'].apply(lambda x: x.split()[0])
    brands: list[str] = df['Manufacturer'].dropna().unique()
    brand_list = [brand.strip().replace("Sony Ericsson", "sony").replace("Research in Motion (RIM)", "BlackBerry").replace("leTV", "LeEco") for brand in brands]  # Remove whitespaces

    print(f"Extracted Brands from {dataset}: {brand_list}")

    # Search for lines containing interesting brands
    with open(brands_all, 'r') as f:
        lines = f.readlines()
        for line in lines:
            for brand in brand_list:
                if brand.lower() in line.lower():
                    brand_matches.add(line.strip())  # Add unique lines

# Save to file
brand_matches_list = sorted(list(brand_matches))  # Sort for readability
with open(output_file, 'w') as f:
    for brand in brand_matches_list:
        f.writelines(brand + '\n')

# notes on brands & subbrands:
# some identified brands are not in the list of brands, however in this case their owening brand is in the list and appears in the other dataset. Therefore those subbrands can simply be ignored
# eg: iPhone by Apple