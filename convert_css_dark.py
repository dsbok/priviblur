import os
import re

css_dir = "/root/hyperblur/assets/css"

# We want pure black bg, white text, grey tags, blue links.
# And we want to strip styling for inputs, buttons, select.

def apply_dark_brutalist(content):
    # Strip some button/input styles entirely
    # We will remove .button { ... } blocks
    content = re.sub(r'\.button\s*{[^}]*}', '', content)
    content = re.sub(r'\.button:hover\s*{[^}]*}', '', content)
    content = re.sub(r'\.primary\.button[^}]*{[^}]*}', '', content)
    content = re.sub(r'\.secondary\.button[^}]*{[^}]*}', '', content)
    content = re.sub(r'\.search-bar\s+input[^}]*{[^}]*}', '', content)
    content = re.sub(r'\.search-bar:focus-within[^}]*{[^}]*}', '', content)
    
    # Just to be safe, clean up inline background/borders that were added previously
    content = content.replace('background: #ffffff; border: 1px solid #000;', 'background: #000000; border: 1px solid #333;')
    content = content.replace('background: #f4f4f4;', 'background: #111111;')
    content = content.replace('background: #eeeeee;', 'background: #222222;')
    content = content.replace('background: #cccccc;', 'background: #333333;')
    content = content.replace('background: #dddddd;', 'background: #333333;')
    content = content.replace('color: #000000;', 'color: #ffffff;')
    
    # Also fix tags to be grey
    content = re.sub(r'\.post-tag\s*{[^}]*}', '.post-tag { display: inline-block; background: #333; color: #aaa; border: 1px solid #555; padding: 2px 4px; font-size: 12px; }', content)
    content = re.sub(r'\.post-tag:hover\s*{[^}]*}', '.post-tag:hover { background: #444; color: #fff; }', content)

    return content

for file in os.listdir(css_dir):
    if file.endswith(".css"):
        filepath = os.path.join(css_dir, file)
        with open(filepath, 'r') as f:
            content = f.read()
        
        content = apply_dark_brutalist(content)

        if file == 'base.css':
            var_block = """
body {
    --color-background: #000000;
    --color-top-level-card-bg: #000000;
    --color-text: #ffffff;
    --color-text-secondary: #aaaaaa;

    --color-nav-bar-icon: #ffffff;
    --color-nav-bar-icon-hover: #5555FF;
    --color-nav-bar-selected-tab-highlight: #ffffff;
    --color-search-icon-fill: #ffffff;
    --color-search-bar-bg: #000000;
    --color-logo: #ffffff;

    --color-footer-text: #aaaaaa;

    --color-community-label-text: #ffffff;
    --color-community-label-button-text: #ffffff;
    --color-community-label-button-bg: #333333;
    --color-community-label-button-highlight: #5555FF;
    --color-community-label-button-hover: #444444;
    --color-community-label-gradient-1: #000000;
    --color-community-label-gradient-2: #000000;

    --color-post-blog-name: #5555FF;
    --color-reblog-attribution: #aaaaaa;
    --color-post-link-block-subtitle: #aaaaaa;
    --color-post-header-date-separator: #ffffff;

    --color-ask-header: #ffffff;
    --color-ask-bg: #111111;

    --color-post-img-alt-text-widget-bg: #222222;
    --color-post-img-alt-text-widget-text: #ffffff;

    --color-poll-text-color: #ffffff;
    --color-poll-winner-bg: #333333;
    --color-poll-proportion-bar-bg: #222222;
    --color-poll-choice-bg: #000000;

    --color-post-reveal-truncated-content-button: #5555FF;
    --color-post-reveal-truncated-content-button-hover: #5555FF;

    --color-post-footer: #aaaaaa;
    --color-post-footer-post-interaction: #aaaaaa;
    --color-post-tag-bg: #333333;
    --color-post-tag-hover: #444444;

    --color-trail-post-separator: #ffffff;

    --color-post-notes-viewer-nav-bar-bg: #000000;
    --color-post-notes-viewer-nav-bar-item: #ffffff;
    --color-read-more-text: #5555FF;

    --color-audio-controls-bg: #222222;
    --color-audio-play-button-bg: #000000;
    --color-audio-play-button-icon-fill: #ffffff;

    --color-text-link: #5555FF;
    --color-text-link-hover: #5555FF;
    --color-text-hashtag: #5555FF;
    --color-text-hashtag-hover: #5555FF;

    --color-reblog-note-separator: #ffffff;

    --color-primary-button-bg: #000000;
    --color-primary-button-hover: #222222;
    --color-primary-button-text: #ffffff;

    --color-secondary-button-bg: #000000;
    --color-secondary-button-hover: #222222;
    --color-button-secondary-text: #ffffff;

    --color-tertiary-button-color: #ffffff;

    --color-dropdown-menu-bg: #000000;
    --color-dropdown-action-select: #000000;
    --color-dropdown-action-hover: #222222;
    --color-control-bar-action-text: #ffffff;
    --color-dropdown-menu-item-selected: #222222;
    --color-dropdown-menu-item-hover: #222222;

    --color-blog-header-blog-name: #ffffff;

    --tumblr-signpost-bg: #000000;
    --tumblr-signpost-border: #ffffff;

    --color-alert-show-error-details: #aaaaaa;
    --color-alert-show-error-details-hover: #5555FF;
}
"""
            content = re.sub(r'body\s*{[^}]+}', var_block, content, count=1)
            content = re.sub(r'color:\s*#0000EE;', 'color: #5555FF;', content)
            
            # Allow native inputs
            content = re.sub(r'\.search-bar\s*{[^}]*}', '.search-bar { display: flex; width: 100%; gap: 10px; }', content)
        
        elif file == 'post.css':
            content = re.sub(r'color:\s*#0000EE;', 'color: #5555FF;', content)
            
        with open(filepath, 'w') as f:
            f.write(content)

print("CSS transformed to dark theme brutalist.")
