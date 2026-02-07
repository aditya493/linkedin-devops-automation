#!/usr/bin/env python3
import re

# Read the file
with open('post_devops_news.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove cta_templates, subscribe_templates, playbook_templates blocks
# Pattern to match the template definitions - more flexible with whitespace
pattern = r'        cta_templates = \[[\s\S]*?\]\n        subscribe_templates = \[[\s\S]*?\]\n        playbook_templates = \[[\s\S]*?\]\n'
replacement = ''
content = re.sub(pattern, replacement, content)

# Now replace the get_subscription_cta function with a stub
subscription_pattern = r'def get_subscription_cta\(\) -> str:[\s\S]*?return cta'
subscription_replacement = '''def get_subscription_cta() -> str:
    """Get subscription call-to-action (disabled).
    
    Subscription and promotion CTAs have been removed.
    """
    return ""'''

content = re.sub(subscription_pattern, subscription_replacement, content)

# Write back
with open('post_devops_news.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Templates and subscription function have been cleaned up successfully!")

