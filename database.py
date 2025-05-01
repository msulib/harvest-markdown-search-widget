import sqlite3
import pathlib
from datetime import datetime
import frontmatter  # python-frontmatter package
from typing import List, Dict
import re

class MarkdownDatabase:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        """Create the necessary database tables"""
        
        # Drop existing tables if they exist
        self.conn.executescript('''
            DROP TABLE IF EXISTS keywords;
            DROP TABLE IF EXISTS documents_fts;
            DROP TABLE IF EXISTS documents;
        ''')

        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT,
                body TEXT NOT NULL,
                created_date TIMESTAMP,
                modified_date TIMESTAMP,
                file_path TEXT
            );
            
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER,
                keyword TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents (id),
                UNIQUE(document_id, keyword)
            );
            
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts 
            USING FTS5(title, body, content=documents);
        ''')
        
        # Trigger to populate the FTS table
        self.conn.executescript('''
            CREATE TRIGGER documents_fts_trigger
            AFTER INSERT ON documents
            BEGIN
                INSERT INTO documents_fts (rowid, title, body) 
                VALUES (new.id, new.title, new.body);
            END;
        ''')

        self.conn.commit()
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from markdown headers and content"""
        # Get words from headers
        headers = re.findall(r'^#{1,6}\s*(.+)$', text, re.MULTILINE)
        keywords = set()
        
        # Add important words from headers
        for header in headers:
            words = re.findall(r'\w+', header.lower())
            keywords.update([w for w in words if len(w) > 3])
        
        return list(keywords)
    
    def add_markdown_file(self, file_path: str):
        """Process and add a single markdown file to the database"""
        path = pathlib.Path(file_path)
        
        try:
            # Parse front matter and content
            post = frontmatter.load(path)
            
            # Get metadata
            title = post.get('title', path.stem)
            url = post.get('url', '')
            
            # File stats
            stats = path.stat()
            created = datetime.fromtimestamp(stats.st_ctime)
            modified = datetime.fromtimestamp(stats.st_mtime)
            
            # Insert document
            cursor = self.conn.execute('''
                INSERT INTO documents (title, url, body, created_date, 
                                     modified_date, file_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (title, url, str(post.content), created, modified, str(path)))
            
            doc_id = cursor.lastrowid
            
            # Extract and insert keywords
            keywords = post.get('keywords', [])
            if not keywords:
                keywords = self.extract_keywords(post.content)
            
            for keyword in set(keywords):
                self.conn.execute('''
                    INSERT OR IGNORE INTO keywords (document_id, keyword)
                    VALUES (?, ?)
                ''', (doc_id, keyword.lower()))
            
            self.conn.commit()
            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    def close(self):
        """Close the database connection"""
        self.conn.close()

# Example usage
if __name__ == "__main__":
    print("Starting database creation...")
    db = MarkdownDatabase("docs.db")

    content_path = pathlib.Path("content")
    print(f"Looking for .md files in: {content_path.absolute()}")
    
    md_files = list(content_path.glob("**/*.md"))
    print(f"Found {len(md_files)} markdown files")
    
    for md_file in md_files:
        print(f"Processing file: {md_file}")
        db.add_markdown_file(str(md_file))

    print("Database processing complete")
    db.close()
