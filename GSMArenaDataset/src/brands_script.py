# by ML

import pandas as pd

brands_all = 'GSMArenaDataset/src/brand_links_all.txt'  # list of possible brands
output_file = 'GSMArenaDataset/src/brand_links_sales.txt'
brands_interesting = 'sales/Sales.csv'  # extract list of brands
df = pd.read_csv(brands_interesting)

# Extract unique brands
brands: list[str] = df['Brands'].dropna().unique()
brand_list = [brand.strip() for brand in brands]  # Clean whitespaces
print(f"Extracted Brands: {brand_list}")

# Search for lines containing interesting brands
results = []
with open(brands_all, 'r') as f:
    lines = f.readlines()
    for line in lines:
        for brand in brand_list:
            if brand.lower() in line.lower():
                results.append(line)
                break

# Save to file
with open(output_file, 'w') as f:
    f.writelines(results)
