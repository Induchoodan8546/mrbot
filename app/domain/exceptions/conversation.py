class ConversationNotFoundError(Exception):
    """Raised when the requested conversation does not exist."""

    def __init__(self, conversation_id: str) -> None:
        self.conversation_id = conversation_id

        super().__init__(
            f"Conversation '{conversation_id}' was not found."
        )