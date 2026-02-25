import re
import os
import pandas as pd
#import odfpy
import random


# Path to your file
FILE_PATH = r"C:\Users\user\Documents\GitHub\Situations_Resolutions\Situations-n-Resolutions-with-sections.xlsx"

def display_card(row):
    """Helper function to display a situation and wait for the resolution."""
    print(f"\n--- SECTION: {row['Section']}  #{row['Number']} ---")
    print(f"Situation:")
    print(f"\n{row['Situation']}")
    
    input("\n[Press Enter to see the Resolution...]")
    
    print("\n" + "-"*30)
    print(f"\n--- SECTION: {row['Section']}  #{row['Number']} ---")
    print(f"RECOMMENDED RESOLUTION:")
    print(f"{row['Recommended resolution']}")
    print(f"\nAPPLICABLE RULE: {row['Applicable Rule']}")
    print("-"*30)

def get_section_choice(df):
    """Helper to let user pick a section from the list."""
    sections = sorted(df['Section'].dropna().unique())
    print("\nAvailable Sections:")
    for i, section in enumerate(sections, 1):
        print(f"{i}. {section}")
    
    while True:
        choice = input("\nSelect a Section number (or 'b' to go back): ").strip().lower()
        if choice == 'b': return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(sections):
                return sections[idx]
            print("Invalid number.")
        except ValueError:
            print("Please enter a valid number.")

# --- MODE 1: Review BY SECTION (Continuous Study) ---
def mode_review_by_section(df):
    selected_section = get_section_choice(df)
    
    # If user didn't pick a section (hit 'b'), go back to Main Menu
    if not selected_section:
        return 

    while True:
        # Filter and pick a random row
        section_df = df[df['Section'] == selected_section]
        random_row = section_df.sample(n=1).iloc[0]
        
        # Show the situation and resolution
        display_card(random_row)
        
        # Navigation prompt
        print(f"\nCurrently Studying: {selected_section}")
        choice = input("Enter: Next random situation | 's': Change section | 'm': Main Menu: ").strip().lower()
        
        if choice == 'm':
            break  # Exit to Main Menu
        
        elif choice == 's':
            # Let them pick a new section without leaving Mode 1
            new_section = get_section_choice(df)
            if new_section:
                selected_section = new_section
                continue
            else:
                break # If they hit 'b' in the section menu, go back to Main Menu
        
        # If they just hit Enter, the loop repeats with the current selected_section

# --- MODE 2: SEQUENTIAL REVIEW (Continuous) ---
def mode_sequential_review(df):
    while True:
        selected_section = get_section_choice(df)
        
        # If user hits 'b' in the section list, go back to Main Menu
        if not selected_section:
            break

        # Sort values by 'Number' to ensure they appear in order (1, 2, 3...)
        section_df = df[df['Section'] == selected_section].sort_values(by='Number')
        print(f"\n--- Starting sequential review of: {selected_section} ---")
        
        for _, row in section_df.iterrows():
            display_card(row)
            
            print(f"\n[Studying: {selected_section}]")
            choice = input("Enter: Next Item | 's': Switch Section | 'm': Main Menu: ").strip().lower()
            
            if choice == 'm':
                return  # Exit the function entirely back to Main Menu
            
            if choice == 's':
                break  # Exit the row loop to choose a different section
        
        else:
            # This triggers only if the 'for' loop finishes naturally (reached the end)
            print(f"\n*** You have completed all situations in {selected_section}! ***")
            input("[Press Enter to return to Section Selection]")

# --- MODE 3: REVIEW SPECIFIC NUMBER (Continuous Search) ---
def mode_specific_number(df):
    while True:
        print("\n" + "-"*40)
        num_choice = input("Enter Situation # to Find | 'm' for Main Menu): ").strip().lower()
        
        # Exit condition
        if num_choice == 'm':
            break
            
        # Filter by the 'Number' column
        # Converting both to string ensures a match even if Excel loaded them as integers
        """A Minor "Safety" Suggestion
        In Mode 3 (Search by Number), since you're converting everything to strings for comparison, 
        users might accidentally type something like 12.0 or add a space. To make it even more robust, 
        you can use .str.strip() during the comparison.
        Here is that one specific line updated for better "user-proofing":"""
        # Updated filter in Mode 3
        results = df[df['Number'].astype(str).str.strip() == num_choice.strip()]
        
        if results.empty:
            print(f"\n[!] No situation found with Number: {num_choice}")
            print("Please try a different number.")
        else:
            # Since you confirmed numbers are unique, we just take the first match
            row = results.iloc[0]
            display_card(row)
            
            # After viewing, the loop restarts to let them search for another number

# --- MODE 4: TOTALLY RANDOM (Continuous Shuffle) ---
def mode_totally_random(df):
    count = 0
    print("\n" + "!" * 40)
    print("ENTERING TOTAL SHUFFLE MODE")
    print("Picking random situations from all sections...")
    print("!" * 40)

    while True:
        # Pick a random row from the entire dataframe
        random_row = df.sample(n=1).iloc[0]
        count += 1
        
        # Display the card
        display_card(random_row)
        
        print(f"\n[Total reviewed this session: {count}]")
        choice = input("Enter: Next random situation | 'm': Back to Main Menu: ").strip().lower()
        
        if choice == 'm':
            print(f"Shuffle session ended. You reviewed {count} situations.")
            break
        
        # If they hit Enter or anything else, the loop continues...

# --- MAIN MANAGER ---
def main_menu():
    try:
        # Load data once at the start
        df = pd.read_excel(FILE_PATH)
        df.dropna(subset=['Situation'])
        df.columns = [c.strip() for c in df.columns] # Clean columns
        
        while True:
            print("\n" + "="*50)
            print("          USA SWIMMING OFFICIALS")
            print("              Stroke & Turn")
            print("         Situations and Resolutions")
            print("="*50)
            print("1. Review by Section (Random Item)")
            print("2. Sequential Review (Item-by-Item)")
            print("3. Search by Situation Number")
            print("4. Total Random Shuffle")
            print("Q. Quit")
            print("="*50)
            
            choice = input("\nSelect a Mode: ").strip().lower()
            
            if choice == '1':
                mode_review_by_section(df)
            elif choice == '2':
                mode_sequential_review(df)
            elif choice == '3':
                mode_specific_number(df)
            elif choice == '4':
                mode_totally_random(df)
            elif choice == 'q':
                print("Happy Officiating! See you on the deck.")
                break
            else:
                print("Invalid selection. Please try again.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main_menu()