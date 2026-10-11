from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.domain.models import Message, MessageRole
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.database.models import (
    ConversationORM,
    MessageORM,
)


class SQLAlchemyMessageRepository:
    def __init__(
        self,
        session_factory: sessionmaker[Session] = SessionLocal,
    ) -> None:
        self.session_factory = session_factory

    @staticmethod
    def _to_domain(record: MessageORM) -> Message:
        return Message(
            id=record.id,
            conversation_id=record.conversation_id,
            role=MessageRole(record.role),
            content=record.content,
            created_at=record.created_at,
            token_count=record.token_count,
        )

    def add(self, message: Message) -> Message:
        with self.session_factory() as session:
            conversation = session.get(
                ConversationORM,
                message.conversation_id,
            )

            if conversation is None:
                raise ValueError(
                    "Cannot save a message for a nonexistent conversation."
                )

            record = MessageORM(
                id=message.id,
                conversation_id=message.conversation_id,
                role=message.role.value,
                content=message.content,
                created_at=message.created_at,
                token_count=message.token_count,
            )

            conversation.updated_at = message.created_at

            session.add(record)
            session.commit()
            session.refresh(record)

            return self._to_domain(record)

    def get_by_conversation_id(
        self,
        conversation_id: str,
    ) -> list[Message]:
        with self.session_factory() as session:
            statement = (
                select(MessageORM)
                .where(
                    MessageORM.conversation_id == conversation_id
                )
                .order_by(MessageORM.row_id.asc())
            )

            records = session.scalars(statement).all()

            return [
                self._to_domain(record)
                for record in records
            ]