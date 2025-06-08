class Diary:
    def __init__(
        self,
        user_id: str,
        content: str,
        emotions: List[dict],
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        is_temporary: bool = False,
        main_emotion: Optional[str] = None,   # ✅ 추가
        score: Optional[float] = None         # ✅ 추가
    ):
        self.user_id = user_id
        self.content = content
        self.emotions = emotions
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.is_temporary = is_temporary
        self.main_emotion = main_emotion      # ✅ 저장
        self.score = score                    # ✅ 저장

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "content": self.content,
            "emotions": self.emotions,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_temporary": self.is_temporary,
            "main_emotion": self.main_emotion,   # ✅ 포함
            "score": self.score                  # ✅ 포함
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Diary':
        return cls(
            user_id=data["user_id"],
            content=data["content"],
            emotions=data["emotions"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            is_temporary=data.get("is_temporary", False),
            main_emotion=data.get("main_emotion"),   # ✅ 포함
            score=data.get("score")                  # ✅ 포함
        )
