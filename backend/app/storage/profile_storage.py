from pathlib import Path
from uuid import uuid4

from app.config import get_settings
from app.schemas.profile import CreateProfileRequest, UserProfile
from app.utils.json_utils import read_json, write_json


class ProfileStorage:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.base_dir = self.settings.profiles_path
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def list_profiles(self) -> list[UserProfile]:
        return [UserProfile(**read_json(path)) for path in sorted(self.base_dir.glob("*.json"))]

    def get_profile(self, profile_id: str) -> UserProfile:
        path = self.base_dir / f"{profile_id}.json"
        return UserProfile(**read_json(path))

    def create_profile(self, payload: CreateProfileRequest) -> UserProfile:
        profile = UserProfile(id=f"profile_{uuid4().hex[:10]}", **payload.model_dump())
        self.save_profile(profile)
        return profile

    def save_profile(self, profile: UserProfile) -> UserProfile:
        write_json(self.base_dir / f"{profile.id}.json", profile.model_dump())
        return profile

    def delete_profile(self, profile_id: str) -> None:
        path = self.base_dir / f"{profile_id}.json"
        if path.exists():
            path.unlink()
