import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
import httpx
import subprocess
from config import *
from logger import get_logger
from service_manager import *
from sendmessage import sendMessage
from service import *

logger = get_logger()

TARGET_STATUS="NONE"


def init():
    global SERVICES
    global TIMERS
    global SERVICES_TO_CARE
    
    for name in SERVICES:
        SERVICES_TO_CARE[name] =Service(name,"SERVICE")
    for name in TIMERS:
        SERVICES_TO_CARE[name] = Service(name,"TIMER")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init()
    tasks = []
    tasks.append(asyncio.create_task(monitoring_node(INTERVAL)))
    for service in SERVICES_TO_CARE.values():
        tasks.append(asyncio.create_task(monitoring_service(service,INTERVAL)))
    tasks.append(asyncio.create_task(monitoring_target_service(INTERVAL)))
    yield
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
        

#REFACTOR
async def monitoring_node(interval):
    global TARGET_STATUS
    while True:
        prev_target_status = TARGET_STATUS # call by value
        health_uri = "health"
        URL = f"http://{TARGET_NODE}/{health_uri}"
        healthy= await health_check(URL)
        if not healthy:
            if TARGET_STATUS != "DEAD":
                if prev_target_status == "ALIVE":
                    sendMessage(f"{TARGET_NODE} 감지 불가")
                    TARGET_STATUS="DEAD"
                    # ping 쏴보고 서버 없으면 전체 서비스 재시작
        else:
            TARGET_STATUS="ALIVE"
        await asyncio.sleep(interval)

async def health_check(url: str) -> bool:
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            response = await client.get(url)
            return response.status_code == 200
    except Exception:
        return False
        
async def monitoring_service(service: Service, interval):
    while True:
        try:
            service_alive = await check_service_alive(service)
            if service_alive :
                await service.set_status_to_alive()
            else:
                await service.set_status_to_dead()
        except Exception as e:
            logger.error(f"[{service.get_name()}] systemctl check failed  : {e}")
            await service.set_status_to_failed()
        await asyncio.sleep(interval)
         
async def monitoring_target_service(interval):
    global TARGET_STATUS
    status_uri= "status"
    URL = f"http://{TARGET_NODE}/{status_uri}" 
    while True:
        if TARGET_STATUS == "DEAD":
            await asyncio.sleep(interval)
            continue
        try:
            async with httpx.AsyncClient(timeout=3) as client:
                response = await client.get(URL)
                if response.status_code == 200:
                    data = response.json()
                    await do_action(data)
        except httpx.TimeoutException:
            logger.warning(f"Timeout Request to {URL} timed out")
        except Exception as e:
            logger.error(f"monitoring failed : {e}")
        await asyncio.sleep(interval)

app = FastAPI(lifespan=lifespan)
    
@app.get("/health")
def health():
    return {
        "status":"ok"
    }
    
@app.get("/status")
async def status():
    result = {}
    for name, svc in SERVICES_TO_CARE.items():
        result[name] = await svc.get_status()
    return {
        "mode":MODE,
        "target_status":TARGET_STATUS,
        "services": result
    }
    
    
if __name__ == "__main__":
    uvicorn.run("master:app", host="0.0.0.0", port=PORT, reload=False, log_level="warning")