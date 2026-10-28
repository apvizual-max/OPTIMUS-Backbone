import os
import httpx
import sys
import datetime
import hashlib

ES_URL = "http://localhost:9200"
INDEX_NAME = "sentinel-reality"

# Extensions to index (text-based configs, source code, documentation)
TEXT_EXTENSIONS = {
    '.txt', '.md', '.json', '.yaml', '.yml', '.py', '.js', '.ts', '.html', '.css',
    '.ini', '.conf', '.toml', '.csv', '.xml', '.bat', '.sh', '.ps1', '.cfg', '.properties'
}

# Directories to strictly ignore
IGNORED_DIRS = {
    'windows', 'program files', 'program files (x86)', 'appdata/local/temp',
    'node_modules', 'venv', '.venv', '__pycache__', '.git', '.idea', '.gradle',
    'cache', 'temp', 'tmp', 'recycle.bin', 'system volume information'
}

def init_index():
    mapping = {
        "mappings": {
            "properties": {
                "path": {"type": "keyword"},
                "content": {"type": "text", "analyzer": "standard"},
                "size_bytes": {"type": "integer"},
                "modified_at": {"type": "date"},
                "zone": {"type": "keyword"}
            }
        }
    }
    try:
        resp = httpx.put(f"{ES_URL}/{INDEX_NAME}", json=mapping)
        if resp.status_code in (200, 400): # 400 means index already exists
            print(f"Index '{INDEX_NAME}' initialized.")
        else:
            print(f"Unexpected status: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Failed to connect to Elasticsearch at {ES_URL}: {e}")
        sys.exit(1)

def should_index(file_path):
    # Check extension
    _, ext = os.path.splitext(file_path.lower())
    if ext not in TEXT_EXTENSIONS:
        return False
    
    # Check if path contains ignored folder names
    normalized_path = file_path.lower().replace('\\', '/')
    for d in IGNORED_DIRS:
        if f"/{d}/" in normalized_path or normalized_path.startswith(d + "/"):
            return False
            
    # Check size (skip files > 500KB to prevent indexing huge logs/databases)
    try:
        if os.path.getsize(file_path) > 500 * 1024:
            return False
    except Exception:
        return False
        
    return True

def index_file(file_path, zone):
    try:
        size = os.path.getsize(file_path)
        mtime = os.path.getmtime(file_path)
        modified_date = datetime.datetime.fromtimestamp(mtime).isoformat()
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        doc = {
            "path": file_path,
            "content": content,
            "size_bytes": size,
            "modified_at": modified_date,
            "zone": zone
        }
        
        # ID is path hash for idempotency and updating
        doc_id = hashlib.sha256(file_path.encode('utf-8')).hexdigest()
        resp = httpx.put(f"{ES_URL}/{INDEX_NAME}/_doc/{doc_id}", json=doc)
        return resp.status_code in (200, 201)
    except Exception as e:
        print(f"Error indexing {file_path}: {e}")
        return False

def crawl_zone(root_dir, zone):
    print(f"Crawling zone '{zone}' at path: {root_dir}")
    if not os.path.exists(root_dir):
        print(f"Path does not exist: {root_dir}")
        return
        
    indexed_count = 0
    scanned_count = 0
    
    for root, dirs, files in os.walk(root_dir):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d.lower() not in IGNORED_DIRS]
        
        for f in files:
            scanned_count += 1
            file_path = os.path.join(root, f)
            if should_index(file_path):
                if index_file(file_path, zone):
                    indexed_count += 1
                    if indexed_count % 100 == 0:
                        print(f"Indexed {indexed_count} files...")
                        
    print(f"Zone '{zone}' finished. Scanned: {scanned_count}, Indexed: {indexed_count}")

def main():
    init_index()
    # Define actual folder paths for Zone C, E, D to avoid scanning the entire drives!
    zones = {
        "C": [
            r"C:\Users\apviz\.gemini\config",
            r"C:\Users\apviz\AppData\Local\hermes"
        ],
        "D": [
            r"D:\Alex_Knowlege_Vault",
            r"D:\Alex_GDrive_Folder"
        ],
        "E": [
            r"E:\CLAUDE",
            r"E:\Ai_GDrive_Folder",
            r"E:\Ai_System_Access"
        ]
    }
    
    for zone, paths in zones.items():
        for p in paths:
            if os.path.exists(p):
                crawl_zone(p, zone)

if __name__ == "__main__":
    main()
