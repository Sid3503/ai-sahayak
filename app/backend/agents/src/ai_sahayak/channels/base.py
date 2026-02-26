from abc import ABC, abstractmethod
from ai_sahayak.channels.models import AgentRequest, AgentResponse

class BaseChannelAdapter(ABC):
    @abstractmethod
    async def map_request(self, payload: dict) -> AgentRequest:
        pass

    @abstractmethod
    async def format_response(self, response: AgentResponse) -> dict:
        pass

    @abstractmethod
    async def send_message(self, recipient_id: str, message: dict) -> bool:
        pass
