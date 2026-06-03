#!/usr/bin/env python3
"""
Google Doc Builder & Word Exporter
Usage:
    python3 build_native_google_doc.py --input <advisory.md> --folder <drive_folder_id> --name "Document Name" [--out-docx <output.docx>]

Description:
    Parses a local markdown file to semantic HTML, authenticates with Google APIs via
    Application Default Credentials (ADC), uploads the HTML to convert it to a native 
    collaborative Google Doc, exports a high-fidelity Word Document (.docx) from it, 
    and uploads the Word Document to the same Google Drive folder.
"""

import re
import os
import io
import sys
import argparse
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

def parse_markdown_to_html(md_content):
    lines = md_content.split('\n')
    html = []
    
    # HTML Boilerplate with modern styling
    html.append('<!DOCTYPE html>')
    html.append('<html><head><meta charset="utf-8"><style>')
    html.append('body { font-family: "Arial", sans-serif; color: #333333; line-height: 1.6; margin: 40px; }')
    html.append('h1 { font-size: 20pt; color: #1a73e8; margin-top: 24px; margin-bottom: 12px; border-bottom: 1px solid #e0e0e0; padding-bottom: 6px; }')
    html.append('h2 { font-size: 15pt; color: #202124; margin-top: 20px; margin-bottom: 10px; }')
    html.append('h3 { font-size: 12pt; color: #5f6368; margin-top: 16px; margin-bottom: 8px; }')
    html.append('p { font-size: 11pt; margin-top: 0; margin-bottom: 12px; text-align: left; }')
    html.append('ul { margin-top: 0; margin-bottom: 12px; padding-left: 24px; }')
    html.append('li { font-size: 11pt; margin-bottom: 6px; }')
    html.append('pre { background-color: #f8f9fa; border-left: 4px solid #1a73e8; padding: 12px; font-family: "Courier New", monospace; font-size: 9.5pt; margin: 12px 0; overflow-x: auto; }')
    html.append('code { font-family: "Courier New", monospace; font-size: 9.5pt; background-color: #f1f3f4; padding: 2px 4px; border-radius: 3px; }')
    html.append('a { color: #1a73e8; text-decoration: none; }')
    html.append('hr { border: 0; border-top: 1px solid #e0e0e0; margin: 24px 0; }')
    html.append('strong { color: #111111; }')
    html.append('</style></head><body>')
    
    in_code_block = False
    code_lines = []
    list_stack = []
    
    for line in lines:
        # Handle Code Blocks
            if in_code_block:
                in_code_block = False
                escaped_code = '\n'.join(code_lines).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html.append('<pre><code>' + escaped_code + '</code></pre>')
                code_lines = []
            else:
                in_code_block = True
            continue
            
        if in_code_block:
            code_lines.append(line)
            continue
            
        # Handle Horizontal Rule
        if line.strip() == '---':
            while list_stack:
                html.append('</ul>')
                list_stack.pop()
            html.append('<hr>')
            continue
            
        # Handle Headers
        header_match = re.match(r'^(#{1,6})\s+(.*)', line)
        if header_match:
            while list_stack:
                html.append('</ul>')
                list_stack.pop()
            level = len(header_match.group(1))
            content = format_inline(header_match.group(2).strip())
            html.append(f'<h{level}>{content}</h{level}>')
            continue
            
        # Handle List Items (Bullet lists with indentation)
        list_match = re.match(r'^(\s*)[\-\*\+]\s+(.*)', line)
        if list_match:
            indent = len(list_match.group(1))
            content = format_inline(list_match.group(2).strip())
            
            if not list_stack:
                html.append('<ul>')
                list_stack.append(indent)
            elif indent > list_stack[-1]:
                html.append('<ul>')
                list_stack.append(indent)
            elif indent < list_stack[-1]:
                while list_stack and indent < list_stack[-1]:
                    html.append('</ul>')
                    list_stack.pop()
                if not list_stack or indent != list_stack[-1]:
                    html.append('<ul>')
                    list_stack.append(indent)
            
            html.append(f'<li>{content}</li>')
            continue
            
        # Handle Empty Lines
        if line.strip() == '':
            continue
            
        # Handle Regular Paragraphs
        while list_stack:
            html.append('</ul>')
            list_stack.pop()
            
        content = format_inline(line.strip())
        html.append(f'<p>{content}</p>')
        
    while list_stack:
        html.append('</ul>')
        list_stack.pop()
        
    html.append('</body></html>')
    return '\n'.join(html)

def format_inline(text):
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', text)
    text = text.replace('&amp;nbsp;', '&nbsp;')
    return text

def main():
    parser = argparse.ArgumentParser(description="Build a native Google Doc and export to DOCX programmatically.")
    parser.add_argument("--input", required=True, help="Path to the input Markdown file")
    parser.add_argument("--folder", required=True, help="Target Google Drive folder ID")
    parser.add_argument("--name", required=True, help="Name of the generated Google Doc")
    parser.add_argument("--out-docx", help="Optional local output path for the DOCX file")
    
    args = parser.parse_args()
    
    md_path = args.input
    folder_id = args.folder
    doc_name = args.name
    
    if not os.path.exists(md_path):
        print(f"Error: Input file '{md_path}' does not exist.")
        sys.exit(1)
        
    docx_path = args.out_docx if args.out_docx else os.path.splitext(md_path)[0] + '.docx'
    
    # 1. Parse markdown to HTML
    print(f"Parsing Markdown file '{md_path}' to HTML...")
    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    html_content = parse_markdown_to_html(md_content)
    
    # 2. Authenticate with Google APIs via ADC
    print("Authenticating with Google Cloud Application Default Credentials (ADC)...")
    try:
        creds, project = google.auth.default()
        drive_service = build('drive', 'v3', credentials=creds)
    except Exception as e:
        print(f"Authentication failed: {e}")
        print("Please ensure 'gcloud auth application-default login' has been executed successfully.")
        sys.exit(1)
        
    # 3. Upload HTML and convert to Google Doc format
    print("Uploading to Google Drive and converting to native Google Doc...")
    file_metadata = {
        'name': doc_name,
        'mimeType': 'application/vnd.google-apps.document',
        'parents': [folder_id]
    }
    
    media = MediaIoBaseUpload(
        io.BytesIO(html_content.encode('utf-8')),
        mimetype='text/html',
        resumable=True
    )
    
    try:
        uploaded_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
        
        doc_id = uploaded_file.get('id')
        doc_url = uploaded_file.get('webViewLink')
        print(f"Successfully created native Google Doc!")
        print(f"Google Doc ID: {doc_id}")
        print(f"Google Doc URL: {doc_url}")
    except Exception as e:
        print(f"Failed to create Google Doc: {e}")
        sys.exit(1)
        
    # 4. Export the native Google Doc as a DOCX file
    print("Exporting Google Doc back as high-fidelity Microsoft Word (.docx)...")
    try:
        request = drive_service.files().export_media(
            fileId=doc_id,
            mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            
        print(f"Saving exported DOCX locally to '{docx_path}'...")
        with open(docx_path, 'wb') as f:
            f.write(fh.getvalue())
        print("Successfully saved local DOCX file.")
    except Exception as e:
        print(f"Failed to export DOCX: {e}")
        sys.exit(1)
        
    # 5. Upload the DOCX file to the same Google Drive folder
    print("Uploading high-fidelity Word Document (.docx) to Drive...")
    try:
        word_metadata = {
            'name': f"{doc_name}.docx",
            'parents': [folder_id]
        }
        media_word = MediaIoBaseUpload(
            io.BytesIO(fh.getvalue()),
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            resumable=True
        )
        uploaded_word = drive_service.files().create(
            body=word_metadata,
            media_body=media_word,
            fields='id, webViewLink'
        ).execute()
        word_url = uploaded_word.get('webViewLink')
        print(f"Word Doc uploaded to Drive: {word_url}")
    except Exception as e:
        print(f"Failed to upload DOCX: {e}")
        sys.exit(1)
        
    print("\n--- PROCESS COMPLETED SUCCESSFULLY ---")
    print(f"Google Doc Link: {doc_url}")
    print(f"Word Doc Link:   {word_url}")
    print(f"Local DOCX Path: {docx_path}")

if __name__ == '__main__':
    main()
