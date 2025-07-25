import asyncio
from config import *
from typing import Dict

class Service:
    def __init__(self,name,service_type):
        self.__name = name
        self.__service_type = service_type
        self.__status = "NONE"
        self.__retry_count = RETRY_COUNT 
        self.__lock = asyncio.Lock()
        self.__action_lock = asyncio.Lock() #for start and stop

    def get_name(self):
        return self.__name

    def get_service_name(self):
        if self.__service_type == "TIMER":
            return self.__name + ".timer"
        else:
            return self.__name
    
    def get_service_type(self):
        return self.__service_type

    async def run_exclusive(self,coro):
        if self.__action_lock.locked():
            return False
        async with self.__action_lock:
            return await coro()

    def can_run_action(self):
        return not self.__action_lock.locked()

    async def set_status_to_alive(self):
        async with self.__lock:
            self.__status = "ALIVE"

    async def set_status_to_dead(self):
        async with self.__lock:
            self.__status = "DEAD"

    async def set_status_to_failed(self):
        async with self.__lock:
            self.__status = "FAILED"

    async def get_status(self):
        async with self.__lock:
            return self.__status
        
    async def get_retry_count(self):
        async with self.__lock:
            return self.__retry_count    
        
    async def reset_retry_counter(self):
        async with self.__lock:    
            self.__retry_count = RETRY_COUNT    
            
    async def decrease_retry_counter(self):
        async with self.__lock:
            self.__retry_count -= 1
    
    
SERVICES_TO_CARE: Dict[str,Service] = {}
