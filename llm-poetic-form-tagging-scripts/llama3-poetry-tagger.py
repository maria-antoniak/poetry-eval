
# LLM (Llama3 via Replicate) Poetry Tagging Script 🤖 📚

# This script will evaluate poems from a supplied Google Sheet (if the data is structured in the right way) and dump results into another Google Sheet

# Install and Load Libraries
import pytz
from datetime import datetime
import pandas as pd
import re
import csv

# Google Sheets
#from google.colab import auth
import gspread
#from google.auth import default

# Import argparse
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--input_file', type=str, default = None)
parser.add_argument('--output_file', type=str, default = None)
parser.add_argument('--output_existing', type=str, default = "")
parser.add_argument('--optional_version', type=str, default = "")
args = parser.parse_args()


# Connect to Google Drive / Google Sheets
# --------------------------------------------------------------
# Create a Google sheet for results

#autenticating to google
gc = gspread.service_account()

date = datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d')
full_date = datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S')

# If no input file provided
if args.input_file == None:
  # Default to all poetry foundation poems as input
  input_file = "poetry_foundation_poems_2024-04-02_all"
else:
   # otherwise, use provided sheet name as input
   input_file = args.input_file

# if no output file provided
if args.output_file == None:
  # Construct file name modeled after input file with current date
  output_file = f"{input_file}-tagged-by-LLMs-{full_date}"
  # Create new Google sheet
  output_worksheet = gc.create(title=output_file, folder_id = "1YGyRflfZ8Q0lfcB5lgl7FxQlVJU1T3Yi")

# if output file name is provided
else:
  # if output file is not existing (new)
  if args.output_existing != "yes":
    # use provided title
    output_file = args.output_file
    # create new Google sheet
    output_worksheet = gc.create(title=output_file, folder_id = "1YGyRflfZ8Q0lfcB5lgl7FxQlVJU1T3Yi")

  # if output file is existing
  else:
    output_file = args.output_file
    # Open existing spreadsheet
    output_worksheet = gc.open(output_file)
    #print(output_worksheet)


input_worksheet = gc.open(input_file).sheet1

# Read in poem CSV
poem_df = pd.DataFrame(input_worksheet.get_all_records())

# Drop poems that are blanks
poem_df = poem_df[poem_df['poem_text'] != ""]

# Fill na with Unknown
poem_df = poem_df.fillna("Unknown")

# possible poetic forms
#possible_forms = poem_df['form'].value_counts().index.to_list()

# ------------------------------------------------------------------------------------------
# Define Poetic Forms and Groups

forms = {"verse forms": { "limerick": 261, "pantoum": 272, "haiku": 260, "sestina": 262, "sonnet": 263, "villanelle": 266, "ballad": 257,  "ghazal": 290},

        "stanza forms": { "couplet": 258,
                         # "ottava rima": 264, "terza rima": 265, "rhymed stanza": 282, "mixed": 284, 
                         "tercet": 292, "quatrain": 293},

        "meters" : {"free verse": 259, "blank verse": 268, 
                    #"syllabic": 271, 
                    "common measure": 283},

       # "techniques": { "epigraph": 270, "assonance": 273, "consonance": 274, "alliteration": 275, "allusion": 276, "simile": 277, "metaphor": 278, "imagery": 279, "refrain": 280, "aphorism": 287, "persona": 294, "imagist": 296, "confessional": 297, "symbolist": 298, "anaphora": 305},

        "types/modes": {"ode": 250, "pastoral": 251, "aubade": 252, "dramatic monologue": 253, "elegy": 254, 
                        #"epistle": 255, "epithalamion": 256,
                         "concrete or pattern poetry": 267,
                          # "epigram": 269,
                           "prose poem": 281,
                            # "series/sequence": 285, "visual poetry": 286,
                             "ars poetica": 288, "ekphrasis": 289,
                              # "epic": 291, "nursery rhymes": 295
                              }
         }

for form_group in forms.keys():
    possible_forms = list(forms[form_group].keys())
    #print(possible_forms)


# -------------------
# POETS DOT ORG PROMPTS
    
# CREATED PROMPTS WITH JUST TEXT

constructed_prompts = []

for form_group in forms.keys():
    possible_forms = list(forms[form_group].keys())

    smaller_poem_df = poem_df[poem_df['form'].isin(possible_forms)]

    for index, poem in smaller_poem_df.iterrows():
        constructed_prompts.append({"form_group": form_group,
                                    "prompt_type": "text",
                                        "prompt": f"""Read the following poem and then choose the form of the poem from one of these possible {form_group}: {possible_forms}. All of the poems have been tagged by experts as one of these forms. You must pick one of these options.
                Please also provide an elaborated rationale for why you think the poem is in this form, a one-word summary rationale, and a score ranking your confidence in your answer from 0 to 1.

        Please report the single poetic form, elaborated rationale, one-word rationale, and confidence score in the following format.

        1. Poetic Form: Ballad
        2. Elaborated Rationale: This poem is a ballad because...
        3. One-Word Summary: Meter
        4. Confidence Score : 0.91


        1. Poetic Form: Sonnet
        2. Elaborated Rationale: This poem is a sonnet because...
        3. One-Word Summary: Meter
        4. Confidence Score : 0.73


        Poem Text (in full): {poem["poem_text"].strip()[:5000]}

        Pick ONE of these possible {form_group}: {possible_forms}
        """,
      #   'poem': poem["poem_text"].strip(),
      #   'form': poem["form"],
      #   'author': poem["clean_author"],
      #   'title': poem["poem_title"],
      #   'birth_death_dates': poem["birth_death_dates"],
      # 'tags': poem["tags"],
      #   'link': poem["poem_link"]
      'poem': poem["poem_text"].strip(),
      'form': poem["form"],
      #'author': poem["clean_author"],
      'author': poem["author"],
      'title': poem["poem_title"],
      'birth_death_dates': poem["birth_death_dates"],
      #'tags': poem["tags"],
      'form_tags': poem["form_tags"],
      'theme_tags': poem["theme_tags"],
      'occasion_tags': poem["occasion_tags"],
      'link': poem["poem_link"]})


# # # PROMPTS WITH TEXT + AUTHOR + TITLE

# for form_group in forms.keys():
#     possible_forms = list(forms[form_group].keys())

#     smaller_poem_df = poem_df[poem_df['form'].isin(possible_forms)]

#     for index, poem in smaller_poem_df.iterrows():
#         constructed_prompts.append({"form_group": form_group,
#                                     "prompt_type": "text+author+title",
#                                         "prompt": f"""Read the following poem and then choose the form of the poem from one of these possible {form_group}: {possible_forms}. All of the poems have been tagged by experts as one of these forms. You must pick one of these options.
#                 Please also provide an elaborated rationale for why you think the poem is in this form, a one-word summary rationale, and a score ranking your confidence in your answer from 0 to 1.

#         Please report the single poetic form, elaborated rationale, and one-word rationale in the following format.

#         1. Poetic Form: Ballad
#         2. Elaborated Rationale: This poem is a ballad because...
#         3. One-Word Summary: Meter
#         4. Confidence Score : 0.91


#         1. Poetic Form: Sonnet
#         2. Elaborated Rationale: This poem is a sonnet because...
#         3. One-Word Summary: Meter
#         4. Confidence Score : 0.73

#         Poem Title: {poem["poem_title"]}
#         Author: {poem["author"]}
#         Poem Text (in full): {poem["poem_text"].strip()[:5000]}

#         Pick ONE of these possible {form_group}: {possible_forms}
#         """,
#       #   'poem': poem["poem_text"].strip(),
#       #   'form': poem["form"],
#       #   'author': poem["clean_author"],
#       #   'title': poem["poem_title"],
#       #   'birth_death_dates': poem["birth_death_dates"],
#       # 'tags': poem["tags"],
#       #   'link': poem["poem_link"]
#       'poem': poem["poem_text"].strip(),
#       'form': poem["form"],
#       #'author': poem["clean_author"],
#       'author': poem["author"],
#       'title': poem["poem_title"],
#       'birth_death_dates': poem["birth_death_dates"],
#       #'tags': poem["tags"],
#       'form_tags': poem["form_tags"],
#       'theme_tags': poem["theme_tags"],
#       'occasion_tags': poem["occasion_tags"],
#       'link': poem["poem_link"]})

# PROMPTS WITH AUTHOR + TITLE
for form_group in forms.keys():
    possible_forms = list(forms[form_group].keys())

    smaller_poem_df = poem_df[poem_df['form'].isin(possible_forms)]

    for index, poem in smaller_poem_df.iterrows():
        constructed_prompts.append({"form_group": form_group,
                                    "prompt_type": "author+title",
                                        "prompt": f"""Based on what you know or can guess about this poem from the author and title, choose the form of the poem from one of these possible {form_group}: {possible_forms}. All of the poems have been tagged by experts as one of these forms. You must pick one of these options.
                Please also provide an elaborated rationale for why you think the poem is in this form, a one-word summary rationale, and a score ranking your confidence in your answer from 0 to 1.

        Please report the single poetic form, elaborated rationale, one-word rationale, and confidence score in the following format.

        1. Poetic Form: Ballad
        2. Elaborated Rationale: This poem is a ballad because...
        3. One-Word Summary: Meter
        4. Confidence Score : 0.91


        1. Poetic Form: Sonnet
        2. Elaborated Rationale: This poem is a sonnet because...
        3. One-Word Summary: Meter
        4. Confidence Score : 0.73

        Poem Title: {poem["poem_title"]}
        Author: {poem["author"]}

        Pick ONE of these possible {form_group}: {possible_forms}
        """,
      #   'poem': poem["poem_text"].strip(),
      #   'form': poem["form"],
      #   'author': poem["clean_author"],
      #   'title': poem["poem_title"],
      #   'birth_death_dates': poem["birth_death_dates"],
      # 'tags': poem["tags"],
      #   'link': poem["poem_link"]
      'poem': poem["poem_text"].strip(),
      'form': poem["form"],
      #'author': poem["clean_author"],
      'author': poem["author"],
      'title': poem["poem_title"],
      'birth_death_dates': poem["birth_death_dates"],
      #'tags': poem["tags"],
      'form_tags': poem["form_tags"],
      'theme_tags': poem["theme_tags"],
      'occasion_tags': poem["occasion_tags"],
      'link': poem["poem_link"]})

# PROMPTS WITH TITLE + FIRST LINE
# import re
# pattern = re.compile(r'\b[A-Za-z]+\b')

# for form_group in forms.keys():
#     possible_forms = list(forms[form_group].keys())

#     smaller_poem_df = poem_df[poem_df['form'].isin(possible_forms)]
    

#     for index, poem in smaller_poem_df.iterrows():
#       # to determine a good first line, create list of lines that have words -- exclude excerpt declaration, dedications, highlight actions
#       poem_lines =  [line for line in poem["poem_text"].split("\n") if pattern.search(line)]
#       if "excerpt" in poem_lines[0] or "(for" in poem_lines[0].lower() or "highlight actions" in poem_lines[0].lower():
#         first_line = poem_lines[1]
#       else:
#         first_line = poem_lines[0]
#       constructed_prompts.append({"form_group": form_group,
#                                   "prompt_type": "title+first line",
#                                       "prompt": f"""Read the first line of the following poem and then choose the form of the poem from one of these possible {form_group}: {possible_forms}. All of the poems have been tagged by experts as one of these forms. You must pick one of these options.
#               Use your existing knowledge of the poem based on this information.
#               Please also provide an elaborated rationale for why you think the poem is in this form, a one-word summary rationale, and a score ranking your confidence in your answer from 0 to 1.

#       Please report the single poetic form, elaborated rationale, and one-word rationale in the following format.

#       1. Poetic Form: Ballad
#       2. Elaborated Rationale: This poem is a ballad because...
#       3. One-Word Summary: Meter
#       4. Confidence Score : 0.91


#       1. Poetic Form: Sonnet
#       2. Elaborated Rationale: This poem is a sonnet because...
#       3. One-Word Summary: Meter
#       4. Confidence Score : 0.73

#       Poem Title: {poem["poem_title"]}
#       Poem Text (first line): {first_line}
#       """,
#       # 'poem': poem["poem_text"].strip(),
#       # 'form': poem["form"],
#       # 'author': poem["clean_author"],
#       # 'title': poem["poem_title"],
#       # 'birth_death_dates': poem["birth_death_dates"],
#       # 'tags': poem["tags"],
#       # 'link': poem["poem_link"]
#       'poem': poem["poem_text"].strip(),
#       'form': poem["form"],
#       #'author': poem["clean_author"],
#       'author': poem["author"],
#       'title': poem["poem_title"],
#       'birth_death_dates': poem["birth_death_dates"],
#       #'tags': poem["tags"],
#       'form_tags': poem["form_tags"],
#       'theme_tags': poem["theme_tags"],
#       'occasion_tags': poem["occassion_tags"],
#       'link': poem["poem_link"]})


# PROMPTS WITH FIRST LINE
import re
line_pattern = re.compile(r'\b[A-Za-z]+\b')

def contains_word_longer_than_two_chars(line):
    # Regular expression to match words longer than 2 characters that are not numbers
    pattern = re.compile(r'\b[a-zA-Z]{3,}\b')
    return bool(pattern.search(line))

def is_valid_first_line(line):
    # Exclude lines containing specific phrases
    invalid_phrases = ["(excerpt)", "highlight actions", "(for"]
    if any(phrase in line.lower() for phrase in invalid_phrases):
        return False
    return contains_word_longer_than_two_chars(line)

def find_first_valid_line(poem_lines):
    for i in range(min(5, len(poem_lines))):  # Loop through the first 5 lines or the total number of lines if less than 5
        line = poem_lines[i]
        if is_valid_first_line(line):
            return line  # Return the first valid line
    # If no valid line is found in the first 4 lines, return the 5th line
    return poem_lines[4] if len(poem_lines) >= 5 else poem_lines[-1] if poem_lines else None

for form_group in forms.keys():
    possible_forms = list(forms[form_group].keys())

    smaller_poem_df = poem_df[poem_df['form'].isin(possible_forms)]
    

    for index, poem in smaller_poem_df.iterrows():
      # to determine a good first line, create list of lines that have words -- exclude excerpt declaration, dedications, highlight actions
      poem_lines =  [line for line in poem["poem_text"].split("\n") if line_pattern.search(line)]
      first_line = find_first_valid_line(poem_lines)
      constructed_prompts.append({"form_group": form_group,
                                  "prompt_type": "first line",
                                      "prompt": f"""Read the first line of the following poem and then choose the form of the poem from one of these possible {form_group}: {possible_forms}. All of the poems have been tagged by experts as one of these forms. You must pick one of these options.
              Use your existing knowledge or guess of the poem based on this first line.
              Please also provide an elaborated rationale for why you think the poem is in this form, a one-word summary rationale, and a score ranking your confidence in your answer from 0 to 1.

      Please report the single poetic form, elaborated rationale, one-word rationale, and confidence score in the following format.

      1. Poetic Form: Ballad
      2. Elaborated Rationale: This poem is a ballad because...
      3. One-Word Summary: Meter
      4. Confidence Score : 0.91


      1. Poetic Form: Sonnet
      2. Elaborated Rationale: This poem is a sonnet because...
      3. One-Word Summary: Meter
      4. Confidence Score : 0.73

      Poem Text (first line): {first_line}

      Pick ONE of these possible {form_group}: {possible_forms}
      """,
      # 'poem': poem["poem_text"].strip(),
      # 'form': poem["form"],
      # 'author': poem["clean_author"],
      # 'title': poem["poem_title"],
      # 'birth_death_dates': poem["birth_death_dates"],
      # 'tags': poem["tags"],
      # 'link': poem["poem_link"]
      'poem': poem["poem_text"].strip(),
      'form': poem["form"],
      #'author': poem["clean_author"],
      'author': poem["author"],
      'title': poem["poem_title"],
      'birth_death_dates': poem["birth_death_dates"],
      #'tags': poem["tags"],
      'form_tags': poem["form_tags"],
      'theme_tags': poem["theme_tags"],
      'occasion_tags': poem["occasion_tags"],
      'link': poem["poem_link"]})

# PROMPTS WITH LAST LINE
import re
line_pattern = re.compile(r'\b[A-Za-z]+\b')

def contains_word_longer_than_two_chars(line):
    # Regular expression to match words longer than 2 characters that are not numbers
    pattern = re.compile(r'\b[a-zA-Z]{3,}\b')
    return bool(pattern.search(line))

def is_valid_last_line(line):
    # Exclude lines containing specific phrases
    invalid_phrases = ["(excerpt)", "highlight actions", "(for"]
    if any(phrase in line.lower() for phrase in invalid_phrases):
        return False
    return contains_word_longer_than_two_chars(line)

def find_last_valid_line(poem_lines):
    for i in range(len(poem_lines) - 1, -1, -1):  # Loop backwards through the lines
        line = poem_lines[i]
        if is_valid_last_line(line):
            return line  # Return the first valid line from the end
    return None  # Return None if no valid line is found

for form_group in forms.keys():
    possible_forms = list(forms[form_group].keys())

    smaller_poem_df = poem_df[poem_df['form'].isin(possible_forms)]
    

    for index, poem in smaller_poem_df.iterrows():
      # to determine a good last line, create list of lines that have words -- exclude excerpt declaration, dedications, highlight actions
      poem_lines =  [line for line in poem["poem_text"].split("\n") if line_pattern.search(line)]
      last_line = find_last_valid_line(poem_lines)
      constructed_prompts.append({"form_group": form_group,
                                  "prompt_type": "last line",
                                      "prompt": f"""Read the last line of the following poem and then choose the form of the poem from one of these possible {form_group}: {possible_forms}. All of the poems have been tagged by experts as one of these forms. You must pick one of these options.
              Use your existing knowledge or guess of the poem based on this last line.
              Please also provide an elaborated rationale for why you think the poem is in this form, a one-word summary rationale, and a score ranking your confidence in your answer from 0 to 1.

      Please report the single poetic form, elaborated rationale, one-word rationale, and confidence score in the following format.

      1. Poetic Form: Ballad
      2. Elaborated Rationale: This poem is a ballad because...
      3. One-Word Summary: Meter
      4. Confidence Score : 0.91


      1. Poetic Form: Sonnet
      2. Elaborated Rationale: This poem is a sonnet because...
      3. One-Word Summary: Meter
      4. Confidence Score : 0.73

      Poem Text (last line): {last_line}

      Pick ONE of these possible {form_group}: {possible_forms}
      """,
      'poem': poem["poem_text"].strip(),
      'form': poem["form"],
      #'author': poem["clean_author"],
      'author': poem["author"],
      'title': poem["poem_title"],
      'birth_death_dates': poem["birth_death_dates"],
      #'tags': poem["tags"],
      'form_tags': poem["form_tags"],
      'theme_tags': poem["theme_tags"],
      'occasion_tags': poem["occasion_tags"],
      'link': poem["poem_link"]})


# -------------------------------------------------------------------------------------------------

# # CREATED PROMPTS WITH JUST TEXT

#constructed_prompts = []

# for form_group in forms.keys():
#     possible_forms = list(forms[form_group].keys())

#     smaller_poem_df = poem_df[poem_df['form'].isin(possible_forms)]

#     for index, poem in smaller_poem_df.iterrows():
#         constructed_prompts.append({"form_group": form_group,
#                                     "prompt_type": "text",
#                                         "prompt": f"""Read the following poem and then choose the form of the poem from one of these possible {form_group}: {possible_forms}. All of the poems have been tagged by experts as one of these forms. You must pick one of these options.
#                 Please also provide an elaborated rationale for why you think the poem is in this form, a one-word summary rationale, and a score ranking your confidence in your answer from 0 to 1.

#         Please report the single poetic form, elaborated rationale, and one-word rationale in the following format.

#         1. Poetic Form: Ballad
#         2. Elaborated Rationale: This poem is a ballad because...
#         3. One-Word Summary: Meter
#         4. Confidence Score : 0.91


#         1. Poetic Form: Sonnet
#         2. Elaborated Rationale: This poem is a sonnet because...
#         3. One-Word Summary: Meter
#         4. Confidence Score : 0.73


#         Poem Text (in full): {poem["poem_text"].strip()[:5000]}

#         Pick ONE of these possible {form_group}: {possible_forms}
#         """,
#         'poem': poem["poem_text"].strip(),
#         'form': poem["form"],
#         'author': poem["clean_author"],
#         'title': poem["poem_title"],
#         'birth_death_dates': poem["birth_death_dates"],
#       'tags': poem["tags"],
#         'link': poem["poem_link"]})


# # PROMPTS WITH TEXT + AUTHOR + TITLE

# for form_group in forms.keys():
#     possible_forms = list(forms[form_group].keys())

#     smaller_poem_df = poem_df[poem_df['form'].isin(possible_forms)]

#     for index, poem in smaller_poem_df.iterrows():
#         constructed_prompts.append({"form_group": form_group,
#                                     "prompt_type": "text+author+title",
#                                         "prompt": f"""Read the following poem and then choose the form of the poem from one of these possible {form_group}: {possible_forms}. All of the poems have been tagged by experts as one of these forms. You must pick one of these options.
#                 Please also provide an elaborated rationale for why you think the poem is in this form, a one-word summary rationale, and a score ranking your confidence in your answer from 0 to 1.

#         Please report the single poetic form, elaborated rationale, and one-word rationale in the following format.

#         1. Poetic Form: Ballad
#         2. Elaborated Rationale: This poem is a ballad because...
#         3. One-Word Summary: Meter
#         4. Confidence Score : 0.91


#         1. Poetic Form: Sonnet
#         2. Elaborated Rationale: This poem is a sonnet because...
#         3. One-Word Summary: Meter
#         4. Confidence Score : 0.73

#         Poem Title: {poem["poem_title"]}
#         Author: {poem["clean_author"]}
#         Poem Text (in full): {poem["poem_text"].strip()[:5000]}

#         Pick ONE of these possible {form_group}: {possible_forms}
#         """,
#         'poem': poem["poem_text"].strip(),
#         'form': poem["form"],
#         'author': poem["clean_author"],
#         'title': poem["poem_title"],
#         'birth_death_dates': poem["birth_death_dates"],
#       'tags': poem["tags"],
#         'link': poem["poem_link"]})

# # PROMPTS WITH TITLE + FIRST LINE
# import re
# pattern = re.compile(r'\b[A-Za-z]+\b')

# for form_group in forms.keys():
#     possible_forms = list(forms[form_group].keys())

#     smaller_poem_df = poem_df[poem_df['form'].isin(possible_forms)]
    

#     for index, poem in smaller_poem_df.iterrows():
#       # to determine a good first line, create list of lines that have words -- exclude excerpt declaration, dedications, highlight actions
#       poem_lines =  [line for line in poem["poem_text"].split("\n") if pattern.search(line)]
#       if "excerpt" in poem_lines[0] or "(for" in poem_lines[0].lower() or "highlight actions" in poem_lines[0].lower():
#         first_line = poem_lines[1]
#       else:
#         first_line = poem_lines[0]
#       constructed_prompts.append({"form_group": form_group,
#                                   "prompt_type": "title+first line",
#                                       "prompt": f"""Read the first line of the following poem and then choose the form of the poem from one of these possible {form_group}: {possible_forms}. All of the poems have been tagged by experts as one of these forms. You must pick one of these options.
#               Use your existing knowledge of the poem based on this information.
#               Please also provide an elaborated rationale for why you think the poem is in this form, a one-word summary rationale, and a score ranking your confidence in your answer from 0 to 1.

#       Please report the single poetic form, elaborated rationale, and one-word rationale in the following format.

#       1. Poetic Form: Ballad
#       2. Elaborated Rationale: This poem is a ballad because...
#       3. One-Word Summary: Meter
#       4. Confidence Score : 0.91


#       1. Poetic Form: Sonnet
#       2. Elaborated Rationale: This poem is a sonnet because...
#       3. One-Word Summary: Meter
#       4. Confidence Score : 0.73

#       Poem Title: {poem["poem_title"]}
#       Poem Text (first line): {first_line}

#     Pick ONE of these possible {form_group}: {possible_forms}
#       """,
#       'poem': poem["poem_text"].strip(),
#       'form': poem["form"],
#       'author': poem["clean_author"],
#       'title': poem["poem_title"],
#       'birth_death_dates': poem["birth_death_dates"],
#       'tags': poem["tags"],
#       'link': poem["poem_link"]})



# # PROMPTS WITH FIRST LINE
# import re
# line_pattern = re.compile(r'\b[A-Za-z]+\b')

# def contains_word_longer_than_two_chars(line):
#     # Regular expression to match words longer than 2 characters that are not numbers
#     pattern = re.compile(r'\b[a-zA-Z]{3,}\b')
#     return bool(pattern.search(line))

# def is_valid_first_line(line):
#     # Exclude lines containing specific phrases
#     invalid_phrases = ["(excerpt)", "highlight actions", "(for"]
#     if any(phrase in line.lower() for phrase in invalid_phrases):
#         return False
#     return contains_word_longer_than_two_chars(line)

# def find_first_valid_line(poem_lines):
#     for i in range(min(5, len(poem_lines))):  # Loop through the first 5 lines or the total number of lines if less than 5
#         line = poem_lines[i]
#         if is_valid_first_line(line):
#             return line  # Return the first valid line
#     # If no valid line is found in the first 4 lines, return the 5th line
#     return poem_lines[4] if len(poem_lines) >= 5 else poem_lines[-1] if poem_lines else None

# for form_group in forms.keys():
#     possible_forms = list(forms[form_group].keys())

#     smaller_poem_df = poem_df[poem_df['form'].isin(possible_forms)]
    

#     for index, poem in smaller_poem_df.iterrows():
#       # to determine a good first line, create list of lines that have words -- exclude excerpt declaration, dedications, highlight actions
#       poem_lines =  [line for line in poem["poem_text"].split("\n") if line_pattern.search(line)]
#       first_line = find_first_valid_line(poem_lines)
#       constructed_prompts.append({"form_group": form_group,
#                                   "prompt_type": "first line",
#                                       "prompt": f"""Read the first line of the following poem and then choose the form of the poem from one of these possible {form_group}: {possible_forms}. All of the poems have been tagged by experts as one of these forms. You must pick one of these options.
#               Use your existing knowledge or guess of the poem based on this first line.
#               Please also provide an elaborated rationale for why you think the poem is in this form, a one-word summary rationale, and a score ranking your confidence in your answer from 0 to 1.

#       Please report the single poetic form, elaborated rationale, and one-word rationale in the following format.

#       1. Poetic Form: Ballad
#       2. Elaborated Rationale: This poem is a ballad because...
#       3. One-Word Summary: Meter
#       4. Confidence Score : 0.91


#       1. Poetic Form: Sonnet
#       2. Elaborated Rationale: This poem is a sonnet because...
#       3. One-Word Summary: Meter
#       4. Confidence Score : 0.73

#       Poem Text (first line): {first_line}

#       Pick ONE of these possible {form_group}: {possible_forms}
#       """,
#       'poem': poem["poem_text"].strip(),
#       'form': poem["form"],
#       'author': poem["clean_author"],
#       'title': poem["poem_title"],
#       'birth_death_dates': poem["birth_death_dates"],
#       'tags': poem["tags"],
#       'link': poem["poem_link"]})

# # PROMPTS WITH LAST LINE
# import re
# line_pattern = re.compile(r'\b[A-Za-z]+\b')

# def contains_word_longer_than_two_chars(line):
#     # Regular expression to match words longer than 2 characters that are not numbers
#     pattern = re.compile(r'\b[a-zA-Z]{3,}\b')
#     return bool(pattern.search(line))

# def is_valid_last_line(line):
#     # Exclude lines containing specific phrases
#     invalid_phrases = ["(excerpt)", "highlight actions", "(for"]
#     if any(phrase in line.lower() for phrase in invalid_phrases):
#         return False
#     return contains_word_longer_than_two_chars(line)

# def find_last_valid_line(poem_lines):
#     for i in range(len(poem_lines) - 1, -1, -1):  # Loop backwards through the lines
#         line = poem_lines[i]
#         if is_valid_last_line(line):
#             return line  # Return the first valid line from the end
#     return None  # Return None if no valid line is found

# for form_group in forms.keys():
#     possible_forms = list(forms[form_group].keys())

#     smaller_poem_df = poem_df[poem_df['form'].isin(possible_forms)]

#     for index, poem in smaller_poem_df.iterrows():
#         # to determine a good last line, create list of lines that have words -- exclude excerpt declaration, dedications, highlight actions
#         poem_lines =  [line for line in poem["poem_text"].split("\n") if line_pattern.search(line)]
#         last_line = find_last_valid_line(poem_lines)
#         constructed_prompts.append({"form_group": form_group,
#                                     "prompt_type": "last line",
#                                         "prompt": f"""Read the last line of the following poem and then choose the form of the poem from one of these possible {form_group}: {possible_forms}. All of the poems have been tagged by experts as one of these forms. You must pick one of these options.
#                 Use your existing knowledge or guess of the poem based on this last line.
#                 Please also provide an elaborated rationale for why you think the poem is in this form, a one-word summary rationale, and a score ranking your confidence in your answer from 0 to 1.

#         Please report the single poetic form, elaborated rationale, and one-word rationale in the following format.

#         1. Poetic Form: Ballad
#         2. Elaborated Rationale: This poem is a ballad because...
#         3. One-Word Summary: Meter
#         4. Confidence Score : 0.91


#         1. Poetic Form: Sonnet
#         2. Elaborated Rationale: This poem is a sonnet because...
#         3. One-Word Summary: Meter
#         4. Confidence Score : 0.73

#         Poem Text (last line): {last_line}

#         Pick ONE of these possible {form_group}: {possible_forms}
#         """,
#         'poem': poem["poem_text"].strip(),
#         'form': poem["form"],
#         'author': poem["clean_author"],
#         'title': poem["poem_title"],
#         'birth_death_dates': poem["birth_death_dates"],
#         'tags': poem["tags"],
#         'link': poem["poem_link"]})



# sort by poem
constructed_prompts = sorted(constructed_prompts, key=lambda d: d['poem'])
#print(len(constructed_prompts))
#print(constructed_prompts[3590])

#print(constructed_prompts[2120])

#-------------------------------------------------------------------------------------------------------
# Feed Prompts to ChatGPT and Dump to Google Sheet

#Initialize OpenAI client

# client = OpenAI(
#     # defaults to os.environ.get("OPENAI_API_KEY")
#     api_key= openai_api_key,
# )

# # models = [ "gpt-4",
# #      "gpt-4o" ,
# #    "gpt-3.5-turbo"
# #      #comment out for now
# #    ]

import os

#Here, we loop through a list of dictionaries with our constructed prompts, and feed the LLM each prompt.

#Then, we get the LLM's answer, pull out specific parts of the answer, and dump all of this information into our Google spreadsheet (row by row).

# POETS DOT ORG

# add header rows if new file
if args.output_existing != "yes":
  output_worksheet.sheet1.append_row(["model",
                            "prompt_type",
                            "poem_text",
                             "title",
                            "author",
                            "birth_death_dates",
                            "form",
                            "model_form_guess",
                            "correctness",
                            "confidence",
                            "elab_rationale",
                            "one_word_summary",
                            "answer",
                            "prompt",
                            "date",
                            "full_date",
                            "link",
                            #"tags",
                            "form_tags",
                            "theme_tags",
                            "occasion_tags"
                            ])
  with open(f"{output_file}.csv", mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["model",
                          "prompt_type",
                          "poem_text",
                            "title",
                          "author",
                          "birth_death_dates",
                          "form",
                          "model_form_guess",
                          "correctness",
                          "confidence",
                          "elab_rationale",
                          "one_word_summary",
                          "answer",
                          "prompt",
                          "date",
                          "full_date",
                          "link",
                           #"tags",
                            "form_tags",
                            "theme_tags",
                            "occasion_tags"])
# # add header rows if new file
# if args.output_existing != "yes":
#   output_worksheet.sheet1.append_row(["model",
#                             "prompt_type",
#                             "poem_text",
#                              "title",
#                            #  "num_lines",
#                            #  "num_stanzas",
#                             "author",
#                             "birth_death_dates",
#                             "form",
#                             "model_form_guess",
#                             "correctness",
#                             "confidence",
#                            # "chatgpt_multi_forms",
#                             "elab_rationale",
#                             "one_word_summary",
#                             "answer",
#                             "prompt",
#                             "date",
#                             "full_date",
#                             "link",
#                             "tags"])
#   with open(f"{output_file}.csv", mode='a', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(["model",
#                           "prompt_type",
#                           "poem_text",
#                             "title",
#                           #  "num_lines",
#                           #  "num_stanzas",
#                           "author",
#                           "birth_death_dates",
#                           "form",
#                           "model_form_guess",
#                           "correctness",
#                           "confidence",
#                           # "chatgpt_multi_forms",
#                           "elab_rationale",
#                           "one_word_summary",
#                           "answer",
#                           "prompt",
#                           "date",
#                           "full_date",
#                           "link",
#                           "tags"])
    

llama_models = [ "meta/meta-llama-3-70b-instruct"]
import replicate 
import time

api = replicate.Client(api_token=my_secrets.replicate_api_key)

output = api.run(
                 "meta/meta-llama-3-70b-instruct",
                input={
                    "prompt": f"hello",
                    "prompt_template": "system\n\nYou are a helpful assistantuser\n\n{prompt}assistant\n\n"
                },
            )
answer = ''.join(output)
print(answer)
def prompt_model(model_choice, prompt_dict, max_retries=1):
    for attempt in range(max_retries + 1):
        try:
            output = api.run(
                model_choice,
                input={
                    "prompt": f"{prompt_dict['prompt'][:4090]}",
                    "prompt_template": "system\n\nYou are a helpful assistantuser\n\n{prompt}assistant\n\n"
                },
            )
            answer = ''.join(output)
            return answer, None
        except replicate.exceptions.ModelError as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries:
                print("Retrying...")
                time.sleep(1)  # wait a bit before retrying
            else:
                return None, e
    return None, "Max retries reached"

# Loop through models, loop through prompts
for model_choice in llama_models:
    for prompt_number, prompt_dict in enumerate(constructed_prompts):
        print(f"Prompting LLAMA3 {model_choice} with the prompt:\n✨{prompt_dict['prompt']}...✨\n\n")
        
        answer, error = prompt_model(model_choice, prompt_dict)
        if error:
            print(f"Failed to get response after retries: {error}")
            continue  # skip to the next prompt

        num_lines_answer = len(answer.split("\n"))
        model_form_guess = ""
        model_rationale = ""
        model_sum = ""
        confidence = ""

        if len(answer.split("\n")) >= 4:
            for num in range(num_lines_answer):
                if "Form" in answer.split("\n")[num] and ":" in answer.split("\n")[num]:
                    model_form_guess = answer.split("\n")[num].split(":")[1].strip()
                    break
            for num in range(num_lines_answer):
                if "Rationale" in answer.split("\n")[num] and ":" in answer.split("\n")[num]:
                    model_rationale = answer.split("\n")[num].split(":")[1].strip()
                    break
            for num in range(num_lines_answer):
                if "Summary" in answer.split("\n")[num] and ":" in answer.split("\n")[num]:
                    model_sum = answer.split("\n")[num].split(":")[1].strip()
                    break
            for num in range(num_lines_answer):
                if "Confidence" in answer.split("\n")[num] and ":" in answer.split("\n")[num]:
                    confidence = answer.split("\n")[num].split(":")[1].strip()
                    break
        
        correctness = 1 if model_form_guess.lower() == prompt_dict['form'] else 0
        
        date = datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d')
        full_date = datetime.now(pytz.timezone('US/Pacific')).strftime('%Y-%m-%d %H:%M:%S')

        with open(f"{output_file}.csv", mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                model_choice,
                prompt_dict['prompt_type'],
                prompt_dict['poem'],
                prompt_dict['title'],
                prompt_dict['author'],
                prompt_dict['birth_death_dates'],
                prompt_dict['form'],
                model_form_guess.lower(),
                correctness,
                confidence,
                model_rationale,
                model_sum,
                answer,
                prompt_dict['prompt'],
                date,
                full_date,
                prompt_dict['link'],
                prompt_dict['form_tags'],
                prompt_dict['theme_tags'],
                prompt_dict['occasion_tags'],
            ])

        try:
            output_worksheet.sheet1.append_row([
                model_choice,
                prompt_dict['prompt_type'],
                prompt_dict['poem'],
                prompt_dict['title'],
                prompt_dict['author'],
                prompt_dict['birth_death_dates'],
                prompt_dict['form'],
                model_form_guess.lower(),
                correctness,
                confidence,
                model_rationale,
                model_sum,
                answer,
                prompt_dict['prompt'],
                date,
                full_date,
                prompt_dict['link'],
                prompt_dict['form_tags'],
                prompt_dict['theme_tags'],
                prompt_dict['occasion_tags']
            ])
        except Exception as e:
            print(f"Failed to append to Google Sheet: {e}")
