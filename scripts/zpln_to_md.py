import json
import sys

def convert():
    # Tenet: Total Function - input/output handled safely
    if len(sys.argv) < 3:
        print("Usage: python3 zpln_to_md.py <input_zpln> <output_md>")
        return

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Tenet: Immutable Transformation
    # We map the paragraphs list to markdown strings
    paragraphs = data.get('paragraphs', [])
    
    def process_paragraph(p):
        text = p.get('text', '')
        title = p.get('title', '')
        header = f"## {title}\n" if title else ""
        
        # Determine language for syntax highlighting
        if text.startswith('%md'):
            return f"{header}{text.replace('%md', '').strip()}\n\n"
        elif text.startswith('%spark'):
            return f"{header}```scala\n{text.replace('%spark', '').strip()}\n```\n\n"
        elif text.startswith('%pyspark'):
            return f"{header}```python\n{text.replace('%pyspark', '').strip()}\n```\n\n"
        else:
            return f"{header}```text\n{text.strip()}\n```\n\n"

    # Build the final content string $O(n)$
    md_body = "\n".join([process_paragraph(p) for p in paragraphs])
    final_output = f"# {data.get('name', 'Notebook Export')}\n\n{md_body}"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_output)
    print(f"Successfully converted {input_file} to {output_file}")

if __name__ == "__main__":
    convert()
