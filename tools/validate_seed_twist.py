import json
import re
import os

FILE = os.path.join(os.path.dirname(__file__), '..', 'gameplay', 'kreative-generatoren.md')

def load_generator_data(path=FILE):
    with open(path, 'r', encoding='utf-8') as f:
        md = f.read()
    # find first json block that contains "generator"
    blocks = re.findall(r"```json\n(\{[^`]*\})\n```", md)
    for b in blocks:
        try:
            data = json.loads(b)
            if 'generator' in data:
                return data['generator']
        except json.JSONDecodeError:
            continue
    return None

def main():
    gen = load_generator_data()
    if not gen:
        print('Keine Generator-Daten gefunden.')
        return
    objectives = [o.strip() for o in gen.get('objective', [])]
    twists = [t['text'].strip() if isinstance(t, dict) else str(t).strip() for t in gen.get('twist', [])]
    duplicates = set(obj for obj in objectives if obj in twists)
    if duplicates:
        print('Warnung: Dopplungen zwischen Objective und Twist gefunden:')
        for d in duplicates:
            print(f' - {d}')
    else:
        print('Keine Dopplungen entdeckt.')

if __name__ == '__main__':
    main()
