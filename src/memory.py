from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any


@dataclass
class StudentProfile:
    """Represents what GradPath knows about the student so far."""
    gpa: Optional[str] = None
    gre: Optional[str] = None
    ielts: Optional[str] = None
    toefl: Optional[str] = None
    field_of_study: Optional[str] = None
    degree_level: Optional[str] = None  # "MS", "MSc", "PhD", etc.
    preferred_countries: Optional[str] = None  # e.g. "US, Canada"
    preferred_cities: Optional[str] = None
    funding_needs: Optional[str] = None  # e.g. "RA/TA required"
    intake_term: Optional[str] = None  # e.g. "Fall 2026"
    budget_notes: Optional[str] = None
    extra_notes: Optional[str] = None


class InMemoryProfileStore:
    """
    Very simple memory store for student profiles
    """

    def __init__(self) -> None:
        self._profiles: Dict[str, StudentProfile] = {}

    def get_profile(self, session_id: str) -> StudentProfile:
        if session_id not in self._profiles:
            self._profiles[session_id] = StudentProfile()
        return self._profiles[session_id]

    def update_profile(self, session_id: str, **updates: Any) -> StudentProfile:
        profile = self.get_profile(session_id)
        for key, value in updates.items():
            if value is not None and hasattr(profile, key):
                setattr(profile, key, value)
        return profile

    def as_dict(self, session_id: str) -> Dict[str, Any]:
        return asdict(self.get_profile(session_id))


# Global store for simplicity (one process)
profile_store = InMemoryProfileStore()
