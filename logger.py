from logging.handlers import RotatingFileHandler
import logging

def get_logger(name: str = "agent"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers: #  중복 핸들러 방지
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        )
        
        file_handler = RotatingFileHandler(
            "/agent.log",
            maxbytes= 10 * 1024 *  1024,
            )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
    return logger