import os
import logging
import inspect
import datetime
from functools import wraps
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 获取默认的logger
logger = logging.getLogger('stock_backtest')

def log_info(message):
    """
    记录INFO级别的日志，包含文件名和行号
    
    参数:
        message (str): 要记录的日志消息
    """
    caller_frame = inspect.currentframe().f_back
    filename = os.path.basename(caller_frame.f_code.co_filename)
    lineno = caller_frame.f_lineno
    logger.info(f"[{filename}:{lineno}] {message}")

def log_error(message):
    """
    记录ERROR级别的日志，包含文件名和行号
    
    参数:
        message (str): 要记录的日志消息
    """
    caller_frame = inspect.currentframe().f_back
    filename = os.path.basename(caller_frame.f_code.co_filename)
    lineno = caller_frame.f_lineno
    logger.error(f"[{filename}:{lineno}] {message}")

def log_warning(message):
    """
    记录WARNING级别的日志，包含文件名和行号
    
    参数:
        message (str): 要记录的日志消息
    """
    caller_frame = inspect.currentframe().f_back
    filename = os.path.basename(caller_frame.f_code.co_filename)
    lineno = caller_frame.f_lineno
    logger.warning(f"[{filename}:{lineno}] {message}")

def log_debug(message):
    """
    记录DEBUG级别的日志，包含文件名和行号
    
    参数:
        message (str): 要记录的日志消息
    """
    caller_frame = inspect.currentframe().f_back
    filename = os.path.basename(caller_frame.f_code.co_filename)
    lineno = caller_frame.f_lineno
    logger.debug(f"[{filename}:{lineno}] {message}")

def set_log_level(level):
    """
    设置日志级别
    
    参数:
        level: 日志级别，可以是logging模块的常量，例如logging.INFO, logging.DEBUG等
               也可以是字符串，例如'INFO', 'DEBUG'等
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    logger.setLevel(level)
    logging.getLogger().setLevel(level)
    log_info(f"日志级别已设置为: {logging.getLevelName(level)}")

def add_file_handler(log_file_path, level=logging.INFO):
    """
    添加一个文件处理器，将日志输出到指定文件
    
    参数:
        log_file_path (str): 日志文件路径
        level: 日志级别，默认为INFO
    """
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(level)
    file_formatter = logging.Formatter('%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s: %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # 添加到logger
    logger.addHandler(file_handler)
    logging.getLogger().addHandler(file_handler)
    log_info(f"已添加日志文件处理器: {log_file_path}")

def log_execution_time(func=None, level='info'):
    """
    一个装饰器，用于记录函数的执行时间
    
    参数:
        func: 要装饰的函数
        level: 日志级别，默认为'info'
    
    用法:
        @log_execution_time
        def my_function():
            # 函数代码
            
        @log_execution_time(level='debug')
        def my_function():
            # 函数代码
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = f(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            
            log_func = {
                'info': log_info,
                'debug': log_debug,
                'warning': log_warning,
                'error': log_error
            }.get(level.lower(), log_info)
            
            log_func(f"函数 {f.__name__} 执行时间: {execution_time:.4f} 秒")
            return result
        return wrapper
    
    if func:
        return decorator(func)
    return decorator

# 初始化日志
def init_logger(log_level='INFO', log_file=None):
    """
    初始化日志系统
    
    参数:
        log_level (str): 日志级别，默认为'INFO'
        log_file (str): 日志文件路径，默认为None（不输出到文件）
    """
    set_log_level(log_level)
    
    if log_file:
        add_file_handler(log_file)
    
    log_info(f"日志系统已初始化，级别: {log_level}")
    return logger 