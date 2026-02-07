#!/usr/bin/env python3
import re

p = 'post_devops_news.py'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

# Remove standalone get_subscription_cta() when used inside list.extend([...])
# Patterns to replace:
# 1) , get_subscription_cta(),
# 2) get_subscription_cta(),
# 3) , get_subscription_cta()
s = re.sub(r"\,\s*get_subscription_cta\(\)\,", ", ", s)
s = re.sub(r"get_subscription_cta\(\)\,\s*", "", s)
s = re.sub(r"\,\s*get_subscription_cta\(\)", "", s)

# Remove occurrences where get_subscription_cta() is concatenated into strings
s = s.replace('\n\n{get_subscription_cta()}\n\n', '\n\n')

# Clean up accidental double commas or extra spaces created
s = re.sub(r",\s*,", ",", s)
s = re.sub(r"\[\s*\]", "[]", s)

# Additional removals for list elements and inline uses
s = re.sub(r"\n\s*get_subscription_cta\(\),", "\n", s)
s = re.sub(r"get_subscription_cta\(\),", "", s)
s = re.sub(r",\s*get_subscription_cta\(\)", "", s)
s = re.sub(r"\n\s*get_subscription_cta\(\)\n", "\n", s)
s = s.replace(f"\n\n{{get_subscription_cta()}}\n\n", "\n\n")

# Replace any remaining literal occurrences
s = s.replace('get_subscription_cta()', '')

# Clean up extra commas/spaces introduced by removals
s = re.sub(r",\s*,", ",", s)
s = re.sub(r"\[\s*\]", "[]", s)

with open(p, 'w', encoding='utf-8') as f:
    f.write(s)

print('Cleaned get_subscription_cta() calls')
