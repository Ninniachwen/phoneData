# cleans existing files of false line breaks and special characters
# by ML

import re

# Input and output file paths
input_file = '2023_GSM_raw.csv'
output_file = '2023_GSM_parsed.csv'

# Define regex pattern for valid rows: start with a number and comma
valid_row_pattern = re.compile(r'^\d*,')

# Read and process the file
with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8') as outfile:
    buffer = ""
    for line in infile:
        line = line.replace("\n", "").replace("\r", "").replace("‑", "-").replace(" ", " ").replace(" ", " ").replace("   ", " ").replace("  ", " ")    # remove linebreaks & spec. char.
        if valid_row_pattern.match(line):  # Line matches the pattern, it's a valid new row
            if buffer:
                outfile.write(buffer.strip() + "\n")  # Write the previous valid row
            buffer = line  # Start a new buffer
        else:
            buffer += " " + line.strip()  # Append invalid line to the current buffer

    # Write the last buffered row if exists
    if buffer:
        outfile.write(buffer.strip() + "\n")