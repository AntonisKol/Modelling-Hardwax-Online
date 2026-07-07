import hashlib
import pydantic
from pydantic import computed_field, field_validator, ValidationInfo


def _hash_id(*parts: str) -> str:
    """Generate deterministic SHA256 hash from parts"""
    payload = "\0".join(parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class TrackModel(pydantic.BaseModel):
    """Represents a single track"""
    name: str
    id: str = ""


class ReleaseModel(pydantic.BaseModel):
    """Represents a single release"""
    artist: str
    title: str
    tracks: list[TrackModel]
    
    @computed_field
    @property
    def id(self) -> str:
        """Auto-compute release ID from title"""
        return _hash_id(self.title)
    
    @field_validator("tracks")
    @classmethod
    def validate_tracks_not_empty(cls, tracks: list[TrackModel]) -> list[TrackModel]:
        if len(tracks) == 0:
            raise ValueError("release must have at least one track")
        return tracks
    
    @field_validator("tracks", mode="after")
    @classmethod
    def compute_track_ids(cls, tracks: list[TrackModel], info: ValidationInfo) -> list[TrackModel]:
        """Assign track IDs from release title + track name"""
        title = info.data.get("title")
        if not isinstance(title, str):
            return tracks
        
        return [
            track.model_copy(update={"id": _hash_id(title, track.name)})
            for track in tracks
        ]
