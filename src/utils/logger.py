"""
日誌工具模組
提供統一的日誌記錄功能
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class Logger:
    """日誌管理器"""

    _instance = None
    _logger = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._logger is None:
            self._setup_logger()

    def _setup_logger(self):
        """設置日誌記錄器"""
        # 確保輸出目錄存在
        log_dir = Path("./output")
        log_dir.mkdir(parents=True, exist_ok=True)

        # 創建日誌記錄器
        self._logger = logging.getLogger("IdiomAnimation")
        self._logger.setLevel(logging.DEBUG)

        # 清除現有的處理器
        self._logger.handlers.clear()

        # 日誌格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

        # 文件處理器
        log_file = log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

    def debug(self, message: str):
        """調試日誌"""
        self._logger.debug(message)

    def info(self, message: str):
        """信息日誌"""
        self._logger.info(message)

    def warning(self, message: str):
        """警告日誌"""
        self._logger.warning(message)

    def error(self, message: str):
        """錯誤日誌"""
        self._logger.error(message)

    def critical(self, message: str):
        """嚴重錯誤日誌"""
        self._logger.critical(message)


# 創建全局日誌實例
logger = Logger()
