import ast
import json
import os

account = "apvizual-max"
project = "OPTIMUS-Backbone"
hash_val = "59f7db5bf9f31e1825843b7c5cf41260eeaedffb"

def get_context(filepath, line_number):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    start = max(0, line_number - 10)
    end = min(len(lines), line_number + 10)
    return "".join(lines[start:end])

report = []
for root, _, files in os.walk('.'):
    if '.git' in root or 'node_modules' in root:
        continue
