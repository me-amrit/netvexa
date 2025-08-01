#!/usr/bin/env python3
"""
Simple script to view embeddings and documents in the database
"""

import asyncio
import asyncpg
import json
import numpy as np
from tabulate import tabulate
from datetime import datetime

async def view_data():
    # Connect to database
    conn = await asyncpg.connect(
        host='localhost',
        port=5432,
        user='postgres',
        password='netvexa_password',
        database='netvexa_db'
    )
    
    print("\n=== NETVEXA Knowledge Documents ===\n")
    
    # Get documents
    rows = await conn.fetch("""
        SELECT 
            id,
            agent_id,
            title,
            content,
            url,
            meta_data,
            created_at,
            octet_length(embedding::text) as embedding_size,
            array_length(string_to_array(trim(both '[]' from embedding::text), ','), 1) as dimensions
        FROM knowledge_documents
        ORDER BY created_at DESC
    """)
    
    if not rows:
        print("No documents found in database.")
        return
    
    # Format for display
    table_data = []
    for row in rows:
        table_data.append([
            str(row['id'])[:8] + "...",  # Shortened ID
            row['agent_id'],
            row['title'] or "N/A",
            row['content'][:60] + "..." if len(row['content']) > 60 else row['content'],
            row['url'] or "N/A",
            json.dumps(row['meta_data'], indent=2)[:50] + "..." if row['meta_data'] else "{}",
            row['created_at'].strftime("%Y-%m-%d %H:%M"),
            f"{row['embedding_size']} bytes",
            row['dimensions']
        ])
    
    headers = ["ID", "Agent", "Title", "Content Preview", "URL", "Metadata", "Created", "Embedding Size", "Dimensions"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    print(f"\nTotal documents: {len(rows)}")
    
    # Show sample embedding values
    print("\n=== Sample Embedding Values (first document) ===\n")
    
    first_doc = await conn.fetchrow("""
        SELECT 
            id,
            substring(embedding::text from 2 for 100) as embedding_sample
        FROM knowledge_documents
        LIMIT 1
    """)
    
    if first_doc:
        print(f"Document ID: {first_doc['id']}")
        print(f"First few embedding values: {first_doc['embedding_sample']}...")
    
    # Show similarity search example
    print("\n=== Example: Finding Similar Documents ===\n")
    
    # Get a document's embedding to use as query
    query_doc = await conn.fetchrow("""
        SELECT embedding 
        FROM knowledge_documents 
        LIMIT 1
    """)
    
    if query_doc:
        similar_docs = await conn.fetch("""
            SELECT 
                id,
                content,
                1 - (embedding <=> $1) as similarity
            FROM knowledge_documents
            ORDER BY embedding <=> $1
            LIMIT 3
        """, query_doc['embedding'])
        
        print("Similar documents (using first document as query):")
        for doc in similar_docs:
            print(f"- Similarity: {doc['similarity']:.4f}")
            print(f"  Content: {doc['content'][:80]}...")
            print()
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(view_data())