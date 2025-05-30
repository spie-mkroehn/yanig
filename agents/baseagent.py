from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Dict


'''
this is somehow the "contract" for each agent
users should be able to communicate with agents in an easy way
i.e. by providing a dict with keys and receiving another one
ComponentResultObject is for internal communication
'''
class BaseAgent(ABC,BaseModel):
    @abstractmethod
    def run(self, context:Dict[str, str])->Dict[str, str]:
        pass
