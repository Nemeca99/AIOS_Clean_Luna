#!/usr/bin/env python3
"""
Convert Word documents to text for analysis
"""

import docx
import os
from pathlib import Path

def convert_docx_to_text(file_path):
    """Convert a Word document to plain text"""
    try:
        doc = docx.Document(file_path)
        content = []
        for para in doc.paragraphs:
            if para.text.strip():
                content.append(para.text)
        return '\n'.join(content)
    except Exception as e:
        return f'Error reading {file_path}: {e}'

def main():
    # Directory with the Word documents
    aios_root = Path(__file__).parent.parent.parent.parent.resolve()
    docs_dir = aios_root / "Onboarding AI"
    
    # List of documents to convert (in order of preference)
    docs_to_convert = [
        "v1_5 – AI Onboarding System.docx",
        "v1_4 – AI Onboarding System (✅ Non-technical friendly – auto-start enabled, Google Drive tested & confirmed) 🧠 INSTRUCTIONS FOR THE MASTER AI (You - e.g., Gemini, ChatGPT):.docx",
        "v1_3 – AI Onboarding System.docx",
        "v1_2 – AI Onboarding System.docx",
        "v1_1 – AI Onboarding System.docx"
    ]
    
    for doc_name in docs_to_convert:
        file_path = docs_dir / doc_name
        if file_path.exists():
            print(f"\n{'='*80}")
            print(f"CONVERTING: {doc_name}")
            print(f"{'='*80}")
            
            content = convert_docx_to_text(file_path)
            # Handle Unicode characters properly
            try:
                print(content)
            except UnicodeEncodeError:
                # Write to file instead
                output_file = f"converted_{doc_name.replace('.docx', '.txt')}"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Content written to {output_file}")
                print("First 1000 characters:")
                print(content[:1000])
            break
    else:
        print("No documents found to convert")

if __name__ == "__main__":
    main()
