import os
from logger import get_logger
import subprocess
from sendmessage import sendMessage 
from service import *
from config import *

logger = get_logger()

async def do_action(data):
    global SERVICES_TO_CARE
    
    if MODE == "MASTER":
        return
    if MODE == "SLAVE":
        for name in data["services"].keys():
            service = SERVICES_TO_CARE[name]
            
            #Fail-over 
            if data["services"][name] != "ALIVE":
                if await service.get_status() != "ALIVE":
                    logger.info(f"[{name}] - Detected master node's service is dead. failover to local service ")
                    sendMessage(f"[{name}] 중단 감지. 페일오버 시도 합니다. ")
                    retry_count = await service.get_retry_count()
                    if retry_count > 0:
                        restart_success = await start_service(service)
                        if restart_success:
                            await service.reset_retry_counter()
                            sendMessage(f"[{name}] 페일오버 완료.")
                            await service.set_status_to_alive()
                        else:
                            await service.decrease_retry_counter()
                    elif retry_count == 0:
                        sendMessage(f"[{name}] 페일오버 불가능. 확인 부탁드립니다")
                continue
            
            #Fail-back
            if data["services"][name] == "ALIVE":
                if await service.get_status() == "ALIVE":
                    logger.info(f"[{name}] - Detected master node's service become active. stopping local timer.")
                    sendMessage(f"[{name}] 마스터 재기동 감지. 페일백 합니다.")
                    retry_count = await service.get_retry_count()
                    if await retry_count > 0:
                        stop_success = await stop_service(service)
                        if stop_success:
                            await service.reset_retry_counter()
                            sendMessage(f"[{name}] 페일백 완료")
                            await service.set_status_to_dead()
                        else:
                            await service.decrease_retry_counter()
                    elif retry_count == 0:
                        sendMessage(f"[{name}] 페일백 불가능. 확인 부탁드립니다")
                continue                        


async def command_async(service: Service ,command : str) -> bool:

    service_name = service.get_service_name()
    try:
        process = await asyncio.create_subprocess_exec(
            "sudo", "systemctl", command, service_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            return True
        else:
            logger.error(f"[{service_name}] failed to {command}: {stderr.decode().strip()}")
            return False
    except Exception as e:
        logger.error(f"systemctl {command} failed: {e}")
        return False

async def start(service : Service):
    return await command_async(service, "start")

async def start_service(service :Service ):
    return await start(service)

async def stop(service : Service):
    return await command_async(service,"stop")

async def stop_service(service: Service):
    return await stop(service)

async def check_alive_async(service : Service) -> bool:
    loop = asyncio.get_running_loop()
    def _check():
        result=subprocess.run(
            ["sudo", "systemctl", "is-active", service.get_service_name()],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.stdout.strip() =="active"
    return await loop.run_in_executor(None,_check)

async def check_service_alive(service:str):
    return await check_alive_async(service)
        