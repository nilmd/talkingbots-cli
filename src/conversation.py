import ollama
from typing import List
import logging
from .models import Participant, Message, MessageLength, ConversationConfig

logger = logging.getLogger(__name__)


class ConversationManager:
    def __init__(self, config: ConversationConfig):
        self.config = config
        self.conversation_log: List[str] = []

    def _get_system_prompt(self, style: MessageLength) -> str:
        base_prompt = "You are participating in a multi-participant discussion. "
        style_prompts = {
            MessageLength.CONCISE: "Keep responses brief and to the point, around 2-3 sentences.",
            MessageLength.BALANCED: "Provide ba"
                                    "lanced responses of moderate length, around 4-5 sentences.",
            MessageLength.DETAILED: "Give detailed, thorough responses that deeply explore the topic."
        }
        return base_prompt + style_prompts[style]

    def _chat_with_model(self, participant: Participant) -> str:
        try:
            system_message = Message("system", self._get_system_prompt(self.config.message_style))
            messages = [{"role": msg.role, "content": msg.content}
                        for msg in [system_message] + participant.history]

            response = ollama.chat(model=participant.model, messages=messages)
            return response["message"]["content"]
        except Exception as e:
            logger.error(f"Error chatting with model {participant.model}: {str(e)}")
            return f"[Error generating response for {participant.name}]"

    def run_conversation(self) -> List[str]:
        # Initialize conversation with topic
        self.conversation_log = [f"Topic: {self.config.topic}\n"]

        # Add initial topic to all participants
        for participant in self.config.participants:
            participant.history.append(Message("user", self.config.topic))

        # Main conversation loop
        for turn in range(self.config.num_turns):
            logger.info(f"Starting turn {turn + 1}/{self.config.num_turns}")

            for participant in self.config.participants:
                # Get response from current participant
                response = self._chat_with_model(participant)

                # Log the response
                log_entry = f"{participant.name}: {response}\n"
                self.conversation_log.append(log_entry)
                logger.info(log_entry.strip())

                # Update histories
                participant.history.append(Message("assistant", response))

                # Share response with other participants
                for other in self.config.participants:
                    if other != participant:
                        other.history.append(
                            Message("user", f"{participant.name} said: {response}")
                        )

        return self.conversation_log
