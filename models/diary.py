from datetime import datetime
from typing import List, Optional

class Diary:
    def __init__(
        self,
        user_id: str,
        content: str,
        emotions: List[dict],
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        is_temporary: bool = False
    ):
        self.user_id = user_id
        self.content = content
        self.emotions = emotions  # [{"label": "happy", "score": 0.8}, ...]
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.is_temporary = is_temporary

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "content": self.content,
            "emotions": self.emotions,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_temporary": self.is_temporary
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Diary':
        return cls(
            user_id=data["user_id"],
            content=data["content"],
            emotions=data["emotions"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            is_temporary=data.get("is_temporary", False)
        ) 