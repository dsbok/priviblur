import os
import re

css_dir = "/root/hyperblur/assets/css"

def soften_dark_bg(content):
    if 'base.css' in file:
        # Replace pure black with slightly lighter dark gray for better contrast
        content = content.replace('--color-background: #000000;', '--color-background: #121212;')
        content = content.replace('--color-top-level-card-bg: #000000;', '--color-top-level-card-bg: #1e1e1e;')
        content = content.replace('--color-search-bar-bg: #000000;', '--color-search-bar-bg: #2a2a2a;')
        content = content.replace('--color-ask-bg: #111111;', '--color-ask-bg: #222222;')
        
        # Add universal sharp edges for all native components to guarantee sharp corners
        sharp_edges = """
/* Guarantee sharp edges on all native components */
button, input, select, textarea {
    border-radius: 0 !important;
}
"""
        if "border-radius: 0 !important;" not in content:
            content = content + "\n" + sharp_edges
            
    return content

for file in os.listdir(css_dir):
    if file.endswith(".css"):
        filepath = os.path.join(css_dir, file)
        with open(filepath, 'r') as f:
            content = f.read()
        
        content = soften_dark_bg(content)

        with open(filepath, 'w') as f:
            f.write(content)

print("Adjusted CSS for softer dark background and strict sharp edges.")
