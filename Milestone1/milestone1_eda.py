import os
import glob
import pandas as pd

# 1. Define the folder where your contracts are stored
contract_folder = os.path.join('Data', 'Raw', 'full_contract_txt')

# 2. Find all .txt files in that folder
txt_files = glob.glob(os.path.join(contract_folder, '*.txt'))

print(f"--- MILESTONE 1: SYSTEM CHECK ---")
print(f"Searching in: {os.path.abspath(contract_folder)}")

# 3. Check if any files were found
if len(txt_files) > 0:
    print(f"✅ Status: Found {len(txt_files)} files.")

    records = []
    for file_path in txt_files:
        try:
            # Use 'ignore' to prevent crashes on messy text files
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            records.append({
                'file_name': os.path.basename(file_path),
                'word_count': len(content.split()),
                'length': len(content)
            })
        except Exception as e:
            print(f'❌ Error reading {file_path}: {e}')

    # 4. Create the DataFrame and show the summary
    df = pd.DataFrame(records)
    print("\n--- CONTRACT ANALYSIS SUMMARY ---")
    print(df)

    # Milestone 1 Requirement: Basic Statistics
    print(f"\nAverage Word Count: {df['word_count'].mean():.2f}")
else:
    print("❌ Status: No files found! Make sure your sample_1.txt and sample_2.txt are in the folder.")