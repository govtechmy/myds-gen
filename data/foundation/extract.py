from collections import defaultdict
import re
import os

def get_sections(filename,css):
    data = re.findall(r"{([\S\s]+)}", css)[0]
    
    if filename == "light.css":
        colour_block = "### Light Theme"
    elif filename == "dark.css":
        colour_block = "\n### Dark Theme"
    elif filename == "color.css":
        colour_block = "### Primitive Colours\n\n"
    
    if filename == "color.css":
        data_fix = re.findall(r"--_([\S-]*):", data) 
        for c in data_fix:
            colour_block = colour_block + f"- {c}\n"
        return colour_block
    else:
        data = re.sub(r"\/\*\s+?--[\S\s]+?\*\/", "", data)
        data_split = data.strip().split("/*")
        data_split = {
            i.split("*/")[0].strip(): i.split("*/")[1].strip() for i in data_split[1:]
        }
        data_fix = {i: re.findall(r"--([\S-]*):", x) for i, x in data_split.items()}

        color = defaultdict(dict)
        for i, x in data_fix.items():
            color[i.split("-")[0].strip().replace("bg","Background")][i.split("-")[1].strip()] = x
        for i,x in color.items():
            colour_block = colour_block + f"\n\n#### {i}\n"
            for j,k in x.items():
                colour_block = colour_block + f"\n**{j}**:\n"
                for kk in k:
                    colour_block = colour_block + f"- `{kk}`\n"
        return colour_block

def extract_colour_dict(filename):
    with open(f"data/myds/packages/style/styles/theme/{filename}") as f:
        data = f.readlines()
    full_text = "".join(data)
    
    return get_sections(filename, full_text)

def generate_md():
    full_design_block = """## Colour
MYDS divides the colour palettes into two (2) categories:

**Primitive colour**: Base colours that remain consistent across both light and dark modes.
**Colour tokens**: Dynamic colours that adjust according to the mode / theme (light or dark).

"""
    theme_files = os.listdir("data/myds/packages/style/styles/theme")
    theme_files.sort()
    for filename in theme_files:
        print(filename)
        full_design_block = full_design_block + extract_colour_dict(filename)
       
    with open("data/foundation/colour.md", "w+") as f:
        f.write(full_design_block)
    

if __name__ == "__main__":
    generate_md()