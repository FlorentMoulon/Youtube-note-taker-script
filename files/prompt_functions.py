# Here you can create functions linked to prompts to perform automated task on the LLM completions.
# If you add a function in PROMPT_FUNCITONS with the key equal to a prompt name, it will be automatcly executed on the completion content before inserting it.
# The function should take the content of the prompt (string) as input and return the modified content (string).

# example : 

# def function_for_prompt_name(content):
#     return f"Do your stuff with the content : {content}"

# PROMPT_FUNCITONS = {
#     "prompt_name": function_for_prompt_name,
#     ...
# }
    
# ---

import json

def extract_JSON(content, delimiter):
    start = content.find(delimiter[0])
    end = content.rfind(delimiter[1])
    
    if start == -1 or end == -1 or start >= end:
        return None
    
    return content[start:end+len(delimiter[1])]





def function_for_prompt_summary(content):
    # add the missing "]" at the end of the content
    if "]" not in content:
        c = content.split("}")
        content = '}'.join(c[:-1]) + "}]" + c[-1]
        
    data = extract_JSON(content, ("[", "]"))
    
    try:
        json_data = json.loads(data)
        return json_data[4]["Denser_Summary"]
    except:
        print("Error in parsing JSON data for : prompt_summary \n Data : \n", content)
        return content

def function_for_keyword_extraction(content):
    keywords = ""
    
    content = content.split("\n")
    for line in content:
        if len(line) < 2:
            continue
        if line[0]=='-' or line[0]=='*':
            keywords += "- " + line[1:].strip() + "\n"
    
    return keywords
    

PROMPT_FUNCITONS = {
    "prompt_summary": function_for_prompt_summary,
    "keyword_extraction": function_for_keyword_extraction
}
