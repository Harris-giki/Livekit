from dataclasses import dataclass, field
from typing import Optional
import yaml
from livekit.agents.voice import Agent


@dataclass
class UserData:
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    reservation_time: Optional[str] = None
    agents: dict[str, Agent] = field(default_factory=dict)

    def summarize(self) -> str:
        data = {
            "customer_name": self.customer_name or "unknown",
            "customer_phone": self.customer_phone or "unknown",
            "reservation_time": self.reservation_time or "unknown",
            }
        # summarize in yaml performs better than json
        return yaml.dump(data)