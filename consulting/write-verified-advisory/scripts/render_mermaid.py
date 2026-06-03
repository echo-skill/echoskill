#!/usr/bin/env python3
"""
Mermaid PNG Renderer
Usage:
    python3 render_mermaid.py <input_file.mmd> [output_file.png]

Description:
    Reads a plain-text Mermaid diagram markup file (.mmd), deflates/compresses the content
    using zlib, and programmatically downloads the rendered high-resolution PNG from 
    Kroki.io (with a fallback to mermaid.ink).
"""

import os
import sys
import zlib
import base64
import urllib.request

def kroki_encode(text):
    # Compress the text using zlib deflate
    compressed = zlib.compress(text.encode('utf-8'), 9)
    # Base64url encode (strip padding characters)
    encoded = base64.urlsafe_b64encode(compressed).decode('utf-8').replace('=', '')
    return encoded

def render_mermaid(mmd_path, png_path):
    if not os.path.exists(mmd_path):
        print(f"Error: Input file '{mmd_path}' does not exist.")
        sys.exit(1)
        
    print(f"Reading {mmd_path}...")
    with open(mmd_path, 'r', encoding='utf-8') as f:
        mmd_content = f.read()
        
    print("Compressing and encoding Mermaid source...")
    encoded_markup = kroki_encode(mmd_content)
    
    kroki_url = f"https://kroki.io/mermaid/png/{encoded_markup}"
    print("Requesting diagram from Kroki.io...")
    
    try:
        req = urllib.request.Request(
            kroki_url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response:
            png_bytes = response.read()
            
        print(f"Saving rendered diagram to {png_path}...")
        with open(png_path, 'wb') as f:
            f.write(png_bytes)
            
        print(f"Successfully rendered: {png_path}")
        return True
        
    except Exception as e:
        print(f"Kroki.io rendering failed: {e}")
        print("Attempting fallback to mermaid.ink...")
        try:
            # mermaid.ink uses standard base64 encoding of the raw string
            raw_b64 = base64.b64encode(mmd_content.encode('utf-8')).decode('utf-8')
            ink_url = f"https://mermaid.ink/png/{raw_b64}"
            
            req = urllib.request.Request(ink_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                png_bytes = response.read()
                
            with open(png_path, 'wb') as f:
                f.write(png_bytes)
            print(f"Successfully rendered via mermaid.ink: {png_path}")
            return True
        except Exception as ink_err:
            print(f"Failed mermaid.ink fallback: {ink_err}")
            return False

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 render_mermaid.py <input_file.mmd> [output_file.png]")
        sys.exit(1)
        
    mmd_path = sys.argv[1]
    if len(sys.argv) == 3:
        png_path = sys.argv[2]
    else:
        png_path = os.path.splitext(mmd_path)[0] + '.png'
        
    success = render_mermaid(mmd_path, png_path)
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
