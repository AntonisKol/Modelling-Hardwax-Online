from models import ReleaseModel
from db import get_connection, close_connection

class DatabaseLoader:
    """
    Load validated ReleaseModel objects into the SQLite database.
    """ 
    def __init__(self)-> None:
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def load(self, releases: list[ReleaseModel], record_store: str)-> int:
            """Insert releases into database - returns count loaded"""
            count = 0 
            
            for release in releases:
                try:
                    artist_id = self._insert_artist(release.artist)
                    label_id = self._insert_label(release)
                    release_id = self._insert_release(release, label_id, record_store)
                    self._insert_release_artist(release_id, artist_id)
                    self._insert_formats(release_id, release)
                    self._insert_tracks(release_id, release)
                    count += 1
                except Exception as e:
                    print(f"Error inserting release {release.title}: {e}")
                    self.conn.rollback()
                    continue
                
            self.conn.commit()
            return count
        
    def _insert_artist(self, artist_name: str) -> int:
        """Insert artist if not exists - return artist_id"""
        if not artist_name or artist_name.strip() == "":
            raise ValueError("artist_name cannot be empty")
        
        self.cursor.execute("SELECT artist_id FROM ARTISTS WHERE artist_name = ?", (artist_name,))
        result = self.cursor.fetchone()
        
        if result:
            return result[0]  
        else:
            self.cursor.execute("INSERT INTO ARTISTS (artist_name) VALUES (?)", (artist_name,))
            return self.cursor.lastrowid
        
    def _insert_label(self, release: ReleaseModel) -> int:
        """Insert label placeholder - return label_id"""
        label_name = f"{release.artist} - {release.title}"
        
        self.cursor.execute("SELECT label_id FROM LABELS WHERE label_name = ?", (label_name,))
        result = self.cursor.fetchone()
        
        if result:
            return result[0]
        
        self.cursor.execute("INSERT INTO LABELS (label_name) VALUES (?)", (label_name,))
        return self.cursor.lastrowid
    
    def _insert_release(self, release: ReleaseModel, label_id: int, record_store: str) -> int:
        """Insert release - return release_id"""
        self.cursor.execute("""
            INSERT INTO RELEASES (title, description, label_id, record_store)
            VALUES (?, ?, ?, ?)
        """, (release.title, release.artist, label_id, record_store))
        
        return self.cursor.lastrowid
    
    def _insert_release_artist(self, release_id: int, artist_id: int) -> None:
        """Link artist to release via junction table"""
        self.cursor.execute("""
            INSERT INTO RELEASE_ARTISTS (release_id, artist_id)
            VALUES (?, ?)
        """, (release_id, artist_id))
        
    def _insert_formats(self, release_id: int, release: ReleaseModel) -> None:
        """Link formats to release via junction table"""
        
        format_name = "Digital" 
        
        self.cursor.execute("SELECT format_id FROM FORMATS WHERE format_name = ?", (format_name,))
        result = self.cursor.fetchone()
        
        if result:
            format_id = result[0]
        else:
            self.cursor.execute("INSERT INTO FORMATS (format_name) VALUES (?)", (format_name,))
            format_id = self.cursor.lastrowid
        
        self.cursor.execute("""
            INSERT INTO RELEASE_FORMATS (release_id, format_id)
            VALUES (?, ?)
        """, (release_id, format_id))      

    def _insert_tracks(self, release_id: int, release: ReleaseModel) -> None:
        """Insert all tracks for release"""
        for track in release.tracks:
            self.cursor.execute("""
                INSERT INTO TRACKS (release_id, track_name)
                VALUES (?, ?)
            """, (release_id, track.name))
            
    def close(self) -> None:
        """Close database connection"""
        close_connection(self.conn)