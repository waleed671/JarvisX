from abc import ABC, abstractmethod


class Tool(ABC):

    name = ""

    description = ""

    @abstractmethod
    def execute(self, parameters: dict):
        pass
