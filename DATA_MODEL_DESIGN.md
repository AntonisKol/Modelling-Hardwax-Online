## Data Model Design

Design the relational database that can be used to populate releases from multiple record stores (Hardwax, Juno, SpaceHall, etc.) on the homepage.

### Database Schema

#### ARTISTS
- `artist_id` (PK, AUTOINCREMENT)
- `artist_name` (TEXT, UNIQUE, NOT NULL)

#### LABELS
- `label_id` (PK, AUTOINCREMENT)
- `label_name` (TEXT, UNIQUE, NOT NULL)

#### FORMATS
- `format_id` (PK, AUTOINCREMENT)
- `format_name` (TEXT, UNIQUE, NOT NULL)

#### RELEASES
- `release_id` (PK, AUTOINCREMENT)
- `title` (TEXT, NOT NULL)
- `description` (TEXT)
- `catalog_number` (TEXT)
- `price` (TEXT)
- `image_url` (TEXT)
- `label_id` (FK → LABELS.label_id, NOT NULL)
- `record_store` (TEXT, NOT NULL, DEFAULT 'hardwax')
- **Purpose:** Stores release metadata; `record_store` tracks which store each release came from

#### RELEASE_ARTISTS (Junction Table)
- `release_artist_join_id` (PK, AUTOINCREMENT)
- `release_id` (FK → RELEASES.release_id, NOT NULL)
- `artist_id` (FK → ARTISTS.artist_id, NOT NULL)
- **Purpose:** Links artists to releases (supports multiple artists per release for collaborations)

#### RELEASE_FORMATS (Junction Table)
- `release_id` (FK → RELEASES.release_id, PK)
- `format_id` (FK → FORMATS.format_id, PK)
- **Purpose:** Links releases to multiple formats (e.g., vinyl, digital, CD)

#### TRACKS
- `track_id` (PK, AUTOINCREMENT)
- `release_id` (FK → RELEASES.release_id, NOT NULL)
- `track_name` (TEXT, NOT NULL)
- **Purpose:** Individual tracks for each release

### Key Design Changes

**Multi-Store Support:**
- `RELEASES.record_store` column tracks which store (hardwax, juno, spacehall) each release came from
- Enables deduplication and comparison across stores

**Artist Relationships:**
- `RELEASE_ARTISTS` junction table enables:
  - Multiple artists per release (collaborations)
  - Multiple releases per artist (discographies)
  - Separation of artist data from release data

**Data Flow:**