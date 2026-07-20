from fastapi import FastAPI
from typing import Optional
from db import get_connection, close_connection

app = FastAPI(title="Record Store API", description="API for accessing releases from multiple record stores")

@app.get("/")
def root():
    return {
        "name": "Record Store API",
        "description": "API for accessing releases from multiple record stores",
        "endpoints": {
            "GET /stores": "Get list of available stores",
            "GET /releases": "Get all releases (optional: ?store=hardwax)",
            "GET /release/{release_id}": "Get specific release with tracks",
            "GET /artist/{artist_name}": "Get all releases by artist (optional: ?store=hardwax)",
            "GET /label/{label_name}": "Get all releases from label (optional: ?store=hardwax)",
            "GET /format/{format_name}": "Get all releases in format (optional: ?store=hardwax)",
            "GET /search?q=query": "Search releases by description (optional: ?store=hardwax)",
            "GET /stats": "Get database statistics by store"
        }
    }

@app.get("/stores")
def get_available_stores():
    """List all record stores in database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = 'SELECT DISTINCT record_store FROM RELEASES ORDER BY record_store'
    cursor.execute(query)
    stores = [row[0] for row in cursor.fetchall()]
    close_connection(conn)
    
    return {"stores": stores, "count": len(stores)}

@app.get("/releases")
def get_all_releases(store: Optional[str] = None):
    """Get all releases, optionally filtered by store"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if store:
        query = '''
            SELECT DISTINCT
                r.release_id,
                r.record_store,
                a.artist_name,
                r.title,
                r.description,
                l.label_name,
                r.catalog_number,
                r.price,
                GROUP_CONCAT(f.format_name, ', ') as formats
            FROM RELEASES r
            JOIN RELEASE_ARTISTS ra ON r.release_id = ra.release_id
            JOIN ARTISTS a ON ra.artist_id = a.artist_id
            JOIN LABELS l ON r.label_id = l.label_id
            LEFT JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
            LEFT JOIN FORMATS f ON rf.format_id = f.format_id
            WHERE r.record_store = ?
            GROUP BY r.release_id
            ORDER BY r.release_id DESC
        '''
        cursor.execute(query, (store,))
    else:
        query = '''
            SELECT DISTINCT
                r.release_id,
                r.record_store,
                a.artist_name,
                r.title,
                r.description,
                l.label_name,
                r.catalog_number,
                r.price,
                GROUP_CONCAT(f.format_name, ', ') as formats
            FROM RELEASES r
            JOIN RELEASE_ARTISTS ra ON r.release_id = ra.release_id
            JOIN ARTISTS a ON ra.artist_id = a.artist_id
            JOIN LABELS l ON r.label_id = l.label_id
            LEFT JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
            LEFT JOIN FORMATS f ON rf.format_id = f.format_id
            GROUP BY r.release_id
            ORDER BY r.record_store, r.release_id DESC
        '''
        cursor.execute(query)
    
    releases = [dict(row) for row in cursor.fetchall()]
    close_connection(conn)
    
    return {"count": len(releases), "store_filter": store, "releases": releases}

@app.get("/label/{label_name}")
def get_releases_by_label(label_name: str, store: Optional[str] = None):
    """Get releases by label, optionally filtered by store"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if store:
        query = '''
            SELECT 
                r.release_id,
                r.record_store,
                a.artist_name,
                r.title,
                r.price,
                GROUP_CONCAT(f.format_name, ', ') as formats
            FROM RELEASES r
            JOIN RELEASE_ARTISTS ra ON r.release_id = ra.release_id
            JOIN ARTISTS a ON ra.artist_id = a.artist_id
            JOIN LABELS l ON r.label_id = l.label_id
            LEFT JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
            LEFT JOIN FORMATS f ON rf.format_id = f.format_id
            WHERE l.label_name = ? AND r.record_store = ?
            GROUP BY r.release_id
            ORDER BY r.release_id DESC
        '''
        cursor.execute(query, (label_name, store))
    else:
        query = '''
            SELECT 
                r.release_id,
                r.record_store,
                a.artist_name,
                r.title,
                r.price,
                GROUP_CONCAT(f.format_name, ', ') as formats
            FROM RELEASES r
            JOIN RELEASE_ARTISTS ra ON r.release_id = ra.release_id
            JOIN ARTISTS a ON ra.artist_id = a.artist_id
            JOIN LABELS l ON r.label_id = l.label_id
            LEFT JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
            LEFT JOIN FORMATS f ON rf.format_id = f.format_id
            WHERE l.label_name = ?
            GROUP BY r.release_id
            ORDER BY r.record_store, r.release_id DESC
        '''
        cursor.execute(query, (label_name,))
    
    releases = [dict(row) for row in cursor.fetchall()]
    close_connection(conn)
    
    return {"label": label_name, "store_filter": store, "count": len(releases), "releases": releases}

@app.get("/format/{format_name}")
def get_releases_by_format(format_name: str, store: Optional[str] = None):
    """Get releases by format, optionally filtered by store"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if store:
        query = '''
            SELECT 
                r.release_id,
                r.record_store,
                a.artist_name,
                r.title,
                r.price
            FROM RELEASES r
            JOIN RELEASE_ARTISTS ra ON r.release_id = ra.release_id
            JOIN ARTISTS a ON ra.artist_id = a.artist_id
            JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
            JOIN FORMATS f ON rf.format_id = f.format_id
            WHERE f.format_name = ? AND r.record_store = ?
            ORDER BY r.release_id DESC
        '''
        cursor.execute(query, (format_name, store))
    else:
        query = '''
            SELECT 
                r.release_id,
                r.record_store,
                a.artist_name,
                r.title,
                r.price
            FROM RELEASES r
            JOIN RELEASE_ARTISTS ra ON r.release_id = ra.release_id
            JOIN ARTISTS a ON ra.artist_id = a.artist_id
            JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
            JOIN FORMATS f ON rf.format_id = f.format_id
            WHERE f.format_name = ?
            ORDER BY r.record_store, r.release_id DESC
        '''
        cursor.execute(query, (format_name,))
    
    releases = [dict(row) for row in cursor.fetchall()]
    close_connection(conn)
    
    return {"format": format_name, "store_filter": store, "count": len(releases), "releases": releases}

@app.get("/release/{release_id}")
def get_release_with_tracks(release_id: int):
    """Get specific release with tracks"""
    conn = get_connection()
    cursor = conn.cursor()
    
    release_query = '''
        SELECT 
            r.release_id,
            r.record_store,
            a.artist_name,
            r.title,
            r.description,
            l.label_name,
            r.catalog_number,
            r.price,
            GROUP_CONCAT(f.format_name, ', ') as formats
        FROM RELEASES r
        JOIN RELEASE_ARTISTS ra ON r.release_id = ra.release_id
        JOIN ARTISTS a ON ra.artist_id = a.artist_id
        JOIN LABELS l ON r.label_id = l.label_id
        LEFT JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
        LEFT JOIN FORMATS f ON rf.format_id = f.format_id
        WHERE r.release_id = ?
        GROUP BY r.release_id
    '''
    
    cursor.execute(release_query, (release_id,))
    release_row = cursor.fetchone()
    
    if not release_row:
        close_connection(conn)
        return {"error": "Release not found"}, 404
    
    release = dict(release_row)
    
    tracks_query = '''
        SELECT track_name FROM TRACKS
        WHERE release_id = ?
        ORDER BY track_id
    '''
    
    cursor.execute(tracks_query, (release_id,))
    tracks = [row[0] for row in cursor.fetchall()]
    
    release["tracks"] = tracks
    close_connection(conn)
    
    return release

@app.get("/artist/{artist_name}")
def get_artist_discography(artist_name: str, store: Optional[str] = None):
    """Get artist discography, optionally filtered by store"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if store:
        query = '''
            SELECT 
                r.release_id,
                r.record_store,
                r.title,
                l.label_name,
                r.price,
                GROUP_CONCAT(f.format_name, ', ') as formats
            FROM RELEASES r
            JOIN RELEASE_ARTISTS ra ON r.release_id = ra.release_id
            JOIN ARTISTS a ON ra.artist_id = a.artist_id
            JOIN LABELS l ON r.label_id = l.label_id
            LEFT JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
            LEFT JOIN FORMATS f ON rf.format_id = f.format_id
            WHERE a.artist_name = ? AND r.record_store = ?
            GROUP BY r.release_id
            ORDER BY r.release_id DESC
        '''
        cursor.execute(query, (artist_name, store))
    else:
        query = '''
            SELECT 
                r.release_id,
                r.record_store,
                r.title,
                l.label_name,
                r.price,
                GROUP_CONCAT(f.format_name, ', ') as formats
            FROM RELEASES r
            JOIN RELEASE_ARTISTS ra ON r.release_id = ra.release_id
            JOIN ARTISTS a ON ra.artist_id = a.artist_id
            JOIN LABELS l ON r.label_id = l.label_id
            LEFT JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
            LEFT JOIN FORMATS f ON rf.format_id = f.format_id
            WHERE a.artist_name = ?
            GROUP BY r.release_id
            ORDER BY r.record_store, r.release_id DESC
        '''
        cursor.execute(query, (artist_name,))
    
    releases = [dict(row) for row in cursor.fetchall()]
    close_connection(conn)
    
    return {"artist": artist_name, "store_filter": store, "count": len(releases), "releases": releases}

@app.get("/search")
def search_releases(q: str, store: Optional[str] = None):
    """Search releases by description, optionally filtered by store"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if store:
        query = '''
            SELECT 
                r.release_id,
                r.record_store,
                a.artist_name,
                r.title,
                l.label_name,
                r.price,
                GROUP_CONCAT(f.format_name, ', ') as formats
            FROM RELEASES r
            JOIN RELEASE_ARTISTS ra ON r.release_id = ra.release_id
            JOIN ARTISTS a ON ra.artist_id = a.artist_id
            JOIN LABELS l ON r.label_id = l.label_id
            LEFT JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
            LEFT JOIN FORMATS f ON rf.format_id = f.format_id
            WHERE r.description LIKE ? AND r.record_store = ?
            GROUP BY r.release_id
            ORDER BY r.release_id DESC
        '''
        cursor.execute(query, (f'%{q}%', store))
    else:
        query = '''
            SELECT 
                r.release_id,
                r.record_store,
                a.artist_name,
                r.title,
                l.label_name,
                r.price,
                GROUP_CONCAT(f.format_name, ', ') as formats
            FROM RELEASES r
            JOIN RELEASE_ARTISTS ra ON r.release_id = ra.release_id
            JOIN ARTISTS a ON ra.artist_id = a.artist_id
            JOIN LABELS l ON r.label_id = l.label_id
            LEFT JOIN RELEASE_FORMATS rf ON r.release_id = rf.release_id
            LEFT JOIN FORMATS f ON rf.format_id = f.format_id
            WHERE r.description LIKE ?
            GROUP BY r.release_id
            ORDER BY r.record_store, r.release_id DESC
        '''
        cursor.execute(query, (f'%{q}%',))
    
    releases = [dict(row) for row in cursor.fetchall()]
    close_connection(conn)
    
    return {"search_term": q, "store_filter": store, "count": len(releases), "releases": releases}

@app.get("/stats")
def get_stats():
    """Get database statistics by store"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Overall stats
    cursor.execute('SELECT COUNT(*) FROM RELEASES')
    releases_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM ARTISTS')
    artists_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM LABELS')
    labels_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM FORMATS')
    formats_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM TRACKS')
    tracks_count = cursor.fetchone()[0]
    
    # Per-store stats
    cursor.execute('''
        SELECT record_store, COUNT(*) as count
        FROM RELEASES
        GROUP BY record_store
        ORDER BY record_store
    ''')
    
    store_stats = {row[0]: row[1] for row in cursor.fetchall()}
    close_connection(conn)
    
    return {
        "total": {
            "releases": releases_count,
            "artists": artists_count,
            "labels": labels_count,
            "formats": formats_count,
            "tracks": tracks_count
        },
        "by_store": store_stats
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)