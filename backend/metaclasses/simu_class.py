from backend.metaclasses.string_convertable  import StringConvertible
from abc import ABC,abstractmethod

class SIMU(ABC,StringConvertible):
    
    @abstractmethod
    def __init__(self,name:str):
        self.name = name