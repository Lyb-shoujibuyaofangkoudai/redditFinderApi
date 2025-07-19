import logging
import datetime
import colorama
from colorama import Fore, Style
import inspect
import traceback

from src.config.env import LOG_LEVEL

# 初始化colorama，在Windows平台上自动将ANSI转义序列转换为Win32 API调用
colorama.init(autoreset=True)

LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# 全局默认配置
DEFAULT_PROJECT_NAME = "Reddit Finder"
DEFAULT_LOG_LEVEL = LOG_LEVEL_MAP[LOG_LEVEL]


def create_logger(project_name=DEFAULT_PROJECT_NAME, log_level=DEFAULT_LOG_LEVEL):
    """
    创建并配置logger
    
    Args:
        project_name (str): 项目名称，默认为generateArticleFromHotNews
        log_level (int): 日志级别，默认为INFO
        
    Returns:
        tuple: (logger实例, project_name) - 用于后续日志函数调用
    """
    # 创建logger
    logger = logging.getLogger(project_name)
    logger.setLevel(log_level)
    
    # 如果没有处理器，则添加一个控制台处理器
    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        logger.addHandler(console_handler)
    
    return logger, project_name


def format_message(project_name, level, message):
    """
    格式化日志消息
    
    Args:
        project_name (str): 项目名称
        level (str): 日志级别
        message: 日志消息内容
        
    Returns:
        str: 格式化后的日志消息
    """
    # 动态获取调用者模块名
    caller_module = None
    for frame_info in inspect.stack():
        if frame_info.filename != __file__:  # 找到非当前文件的调用帧
            caller_module = inspect.getmodulename(frame_info.filename)
            break
    if not caller_module:
        caller_module = "unknown"
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"【{current_time}】【{project_name}】【{caller_module}】【{level}】：{message}"


def info(message, logger_config=None):
    """
    输出INFO级别的日志，使用绿色(前部分)和白色(后部分)
    
    Args:
        message: 日志消息内容
        logger_config: (logger, project_name)元组，如果为None则创建默认logger
    """
    if logger_config is None:
        logger, project_name = create_logger()
    else:
        logger, project_name = logger_config
        
    formatted_message = format_message(project_name, "INFO", message)
    # 分割消息，前部分（时间和级别）为绿色，后部分（实际消息）为白色
    parts = formatted_message.split("：", 1)
    if len(parts) == 2:
        logger.info(f"{Fore.GREEN}{parts[0]}：{Fore.LIGHTWHITE_EX}{parts[1]}{Style.RESET_ALL}")
    else:
        logger.info(f"{Fore.GREEN}{formatted_message}{Style.RESET_ALL}")


def debug(message, logger_config=None):
    """
    输出DEBUG级别的日志，使用红色
    
    Args:
        message: 日志消息内容
        logger_config: (logger, project_name)元组，如果为None则创建默认logger
    """
    if logger_config is None:
        logger, project_name = create_logger()
    else:
        logger, project_name = logger_config
        
    formatted_message = format_message(project_name, "DEBUG", message)
    logger.debug(f"{Fore.RED}{formatted_message}{Style.RESET_ALL}")


def warning(message, logger_config=None):
    """
    输出WARNING级别的日志，使用黄色(前部分)和白色(后部分)
    
    Args:
        message: 日志消息内容
        logger_config: (logger, project_name)元组，如果为None则创建默认logger
    """
    if logger_config is None:
        logger, project_name = create_logger()
    else:
        logger, project_name = logger_config
        
    formatted_message = format_message(project_name, "WARNING", message)
    # 分割消息，前部分（时间和级别）为黄色，后部分（实际消息）为白色
    parts = formatted_message.split("：", 1)
    if len(parts) == 2:
        logger.warning(f"{Fore.YELLOW}{parts[0]}：{Fore.LIGHTBLUE_EX}{parts[1]}{Style.RESET_ALL}")
    else:
        logger.warning(f"{Fore.YELLOW}{formatted_message}{Style.RESET_ALL}")


def error(message, logger_config=None):
    """
    输出ERROR级别的日志，使用红色，并显示调用栈
    
    Args:
        message: 日志消息内容
        logger_config: (logger, project_name)元组，如果为None则创建默认logger
    """
    if logger_config is None:
        logger, project_name = create_logger()
    else:
        logger, project_name = logger_config
        
    formatted_message = format_message(project_name, "ERROR", message)
    stack_trace = traceback.format_exc()
    if stack_trace != "None\n":  # 避免显示无意义的"None"调用栈
        logger.error(f"{Fore.RED}{formatted_message}\n{Fore.LIGHTRED_EX}调用栈:\n{stack_trace}{Style.RESET_ALL}")
    else:
        logger.error(f"{Fore.RED}{formatted_message}{Style.RESET_ALL}")


def critical(message, logger_config=None):
    """
    输出CRITICAL级别的日志，使用红色加粗，并显示调用栈
    
    Args:
        message: 日志消息内容
        logger_config: (logger, project_name)元组，如果为None则创建默认logger
    """
    if logger_config is None:
        logger, project_name = create_logger()
    else:
        logger, project_name = logger_config
        
    formatted_message = format_message(project_name, "CRITICAL", message)
    stack_trace = traceback.format_exc()
    if stack_trace != "None\n":  # 避免显示无意义的"None"调用栈
        logger.critical(f"{Fore.RED}{Style.BRIGHT}{formatted_message}\n{Fore.LIGHTRED_EX}调用栈:\n{stack_trace}{Style.RESET_ALL}")
    else:
        logger.critical(f"{Fore.RED}{Style.BRIGHT}{formatted_message}{Style.RESET_ALL}")


def u_log(message, logger_config=None):
    """
    输出用户交互日志，使用全橙色文字
    
    Args:
        message: 日志消息内容
        logger_config: (logger, project_name)元组，如果为None则创建默认logger
    """
    if logger_config is None:
        logger, project_name = create_logger()
    else:
        logger, project_name = logger_config
        
    logger.info(f"{Fore.LIGHTMAGENTA_EX}{message}{Style.RESET_ALL}")


# 使用示例
if __name__ == "__main__":
    # 方式1：每次调用时创建新的logger
    info("这是一条信息日志")
    debug("这是一条调试日志")
    warning("这是一条警告日志")
    error("这是一条错误日志")
    critical("这是一条严重错误日志")
    u_log("这是一条用户交互日志")
    
    # 方式2：创建一个logger配置并重复使用
    logger_config = create_logger("测试项目", logging.DEBUG)
    info("这是一条复用logger的信息日志", logger_config)
    debug("这是一条复用logger的调试日志", logger_config)
    u_log("这是一条复用logger的用户交互日志", logger_config)