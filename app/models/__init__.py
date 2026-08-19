"""
Importa todos os modelos num único lugar para que:
1. Base.metadata.create_all() (uso em dev) enxergue todas as tabelas.
2. Alembic (autogenerate) enxergue todas as tabelas via app.core.database.Base.
"""

from app.models.conversation import ConversationMessage, ConversationSession, ImmersionText
from app.models.flashcard import Flashcard, UserFlashcardProgress
from app.models.level import Lesson, LessonExample, Level
from app.models.quiz import Quiz, QuizAttempt, QuizQuestion
from app.models.user import User

__all__ = [
    "User",
    "Level",
    "Lesson",
    "LessonExample",
    "Flashcard",
    "UserFlashcardProgress",
    "Quiz",
    "QuizQuestion",
    "QuizAttempt",
    "ConversationSession",
    "ConversationMessage",
    "ImmersionText",
]
