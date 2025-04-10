from abc import abstractmethod
from typing import List
from components import BaseComponent
from core import ComponentResultObject


'''
Extends BaseComponent with streaming functionality.
'''
class BaseStreamingComponent(BaseComponent):
    @abstractmethod
    def stream(self, input:List[ComponentResultObject]):
        pass
