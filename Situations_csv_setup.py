import re
import os
import pandas as pd
#import odfpy
import random

input_filename = "C:/Users/user/Documents/USA Swimming/Situations-n-Resolutions-fixed.txt"
output_filename = "C:/Users/user/Documents/USA Swimming/Situations-n-Resolutions-with-sections.txt"
# Update this path to match your actual file location
csv_file_path = r"C:\Users\user\Documents\USA Swimming\Situations-n-Resolutions-with-sections.xlsx"


def open_file_get_content(input_filename):
    try:
        # 1. Open and read the entire file
        with open(input_filename, 'r', encoding='utf-8') as file:
            content = file.read()
            print(f"Successfully read and captured input file {input_filename}.")
        return content
    except FileNotFoundError:
        print(f"Error: The file '{input_filename}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def replace_Space_period_with_Tilde(input_filename, output_filename):
        
        content = open_file_get_content(input_filename)
        # 2. Define the pattern
        # Group 1: (\n\d{1,3}) -> Newline followed by 1 to 3 digits
        # Group 2: (\.\s+)     -> The period and one or more spaces
        pattern = r"(\n\d{1,3})(\.\s+)"

        # 3. Perform the substitution
        # \1 keeps the newline and numbers, ~ replaces the period and spaces
        modified_content = re.sub(pattern, r"\1~", content)

        # 4. Write the results to a new file
        with open(output_filename, 'w', encoding='utf-8') as file:
            file.write(modified_content)

        print(f"Modified content saved to {output_filename}.")

def flatten_swimming_data(input_file, output_file):
    section_name = ""
    processed_lines = []

    try:
        with open(input_file, 'r', encoding='utf-8') as file:
            for line in file:
                # Remove leading/trailing whitespace (including newlines)
                clean_line = line.strip()

                # 1. Skip truly blank lines
                if not clean_line:
                    continue

                # 2. Identify if this is a Section Name (no tildes)
                if "~" not in clean_line:
                    # Store as variable and add the tilde to the right side
                    section_name = clean_line + "~"
                    continue # Move to next line, don't save the header as its own row

                # 3. If it has a tilde, it's a data row
                # Prepend the section_name and add to our list
                new_row = section_name + clean_line
                processed_lines.append(new_row)

        # 4. Write the flattened data to the output file
        with open(output_file, 'w', encoding='utf-8') as out_file:
            # Join lines with newlines
            out_file.write("\n".join(processed_lines))

        print(f"Success! {len(processed_lines)} rows processed.")
        print(f"File saved to: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

def quiz_situations(csv_file_path):
    try:
        # Load the data
        df = pd.read_excel(csv_file_path)
        #df = pd.read_csv(csv_file_path)
        
        # Standardize column names (stripping any accidental leading/trailing spaces)
        df.columns = [c.strip() for c in df.columns]

        while True:
            # 1. Get unique sections
            sections = sorted(df['Section'].dropna().unique())
            
            print("\n" + "="*50)
            print("USA SWIMMING OFFICIALS")
            print("Stroke & Turn - Situations and Resolutions")
            print("="*50)
            print("Available Sections:")
            for i, section in enumerate(sections, 1):
                print(f"{i}. {section}")
            
            # 2. User selection
            choice = input("\nSelect a Section number (or 'q' to quit): ").strip().lower()
            
            if choice == 'q':
                print("Exiting. Happy Officiating!")
                break
            
            try:
                # Convert input to index
                section_idx = int(choice) - 1
                if section_idx < 0 or section_idx >= len(sections):
                    print("Invalid choice. Please choose a number from the list.")
                    continue
                
                selected_section = sections[section_idx]
                
                # Filter rows for that section
                section_df = df[df['Section'] == selected_section]
                
                # 3. Present a random Situation from that section
                random_row = section_df.sample(n=1).iloc[0]
                
                print(f"\n--- SECTION: {selected_section} ---")
            
                print(f"Situation {selected_section} #{random_row['Number']}:")
                print(f"\n{random_row['Situation']}")
                
                # 4 & 5. Pause and wait for user
                input("\n[Press Enter to see the Resolution...]")
                
                print("\n" + "-"*30)
                print(f"RECOMMENDED RESOLUTION: - Situation {selected_section} #{random_row['Number']}::")
                print(f"{random_row['Recommended resolution']}")
                print(f"\nAPPLICABLE RULE: {random_row['Applicable Rule']}")
                print("-"*30)
                
                input("\n[Press Enter to return to the Main Menu]")

            except ValueError:
                print("Invalid input. Please enter a number or 'q'.")

    except Exception as e:
        print(f"An error occurred: {e}")

# --- RUN THE SCRIPT ---

quiz_situations(csv_file_path)

#flatten_swimming_data(input_filename, output_filename)
#replace_Space_period_with_Tilde(input_filename, output_filename)

