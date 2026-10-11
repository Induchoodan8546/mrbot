from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.domain.models import Conversation
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.database.models import ConversationORM


class SQLAlchemyConversationRepository:
    def __init__(
        self,
        session_factory: sessionmaker[Session] = SessionLocal,
    ) -> None:
        self.session_factory = session_factory

    @staticmethod
    def _to_domain(record: ConversationORM) -> Conversation:
        return Conversation(
            id=record.id,
            user_id=record.user_id,
            title=record.title,
            model=record.model,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    def create(self, conversation: Conversation) -> Conversation:
        with self.session_factory() as session:
            record = ConversationORM(
                id=conversation.id,
                user_id=conversation.user_id,
                title=conversation.title,
                model=conversation.model,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
            )

            session.add(record)
            session.commit()
            session.refresh(record)

            return self._to_domain(record)

    def get_by_id(
        self,
        conversation_id: str,
    ) -> Conversation | None:
        with self.session_factory() as session:
            record = session.get(
                ConversationORM,
                conversation_id,
            )

            if record is None:
                return None

            return self._to_domain(record)

    def list(self) -> list[Conversation]:
        with self.session_factory() as session:
            statement = select(ConversationORM).order_by(
                ConversationORM.updated_at.desc()
            )

            records = session.scalars(statement).all()

            return [
                self._to_domain(record)
                for record in records
            ]

    def delete(self, conversation_id: str) -> None:
        with self.session_factory() as session:
            record = session.get(
                ConversationORM,
                conversation_id,
            )

            if record is not None:
                session.delete(record)
                session.commit()