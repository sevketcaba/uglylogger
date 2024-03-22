from .logger import (
    Logger,
    LogColor,
    LogLevel,
    LogOutput,
    LogMoveOption,
    LogColorMode,
)
from typing import Any


class LogBase:
    """Base class to safely use log functions by inheriting from it"""

    _logger: Logger | None = None

    def __init__(self, logger: Logger | None = None) -> None:
        self._logger = logger

    def set_logger(self, logger: Logger | None = None) -> None:
        self._logger = logger

    def init_logger(self, name: str, file: str | None = None) -> None:
        self._logger = Logger(name, file)

    def console_oneline(
        self,
        msg: Any,
        color: LogColor | None = None,
        console_width: int = 100,
        level: LogLevel = Logger.DEFAULT_CONSOLE_LOG_LEVEL,
    ) -> None:
        if self._logger is None:
            return
        self._logger.console_oneline(msg, color, console_width, level)

    def console(
        self,
        msg: Any,
        color: LogColor | None = None,
        level: LogLevel = Logger.DEFAULT_CONSOLE_LOG_LEVEL,
    ) -> None:
        if self._logger is None:
            return
        self._logger.console(msg, color, level)

    def file(
        self, msg: Any, level: LogLevel = Logger.DEFAULT_FILE_LOG_LEVEL
    ) -> None:
        if self._logger is None:
            return
        self._logger.file(msg, level)

    def log(
        self,
        msg: Any,
        color: LogColor | None = None,
        level: LogLevel = Logger.DEFAULT_LOG_LOG_LEVEL,
        output: LogOutput = LogOutput.ALL,
    ) -> None:
        if self._logger is None:
            return
        self._logger.log(msg, color, level, output)

    def debug(
        self,
        msg: Any,
        color: LogColor | None = None,
        output: LogOutput = LogOutput.ALL,
    ) -> None:
        if self._logger is None:
            return
        self._logger.debug(msg, color, output)

    def info(
        self,
        msg: Any,
        color: LogColor | None = None,
        output: LogOutput = LogOutput.ALL,
    ) -> None:
        if self._logger is None:
            return
        self._logger.info(msg, color, output)

    def warning(
        self,
        msg: Any,
        color: LogColor | None = None,
        output: LogOutput = LogOutput.ALL,
    ) -> None:
        if self._logger is None:
            return
        self._logger.warning(msg, color, output)

    def error(
        self,
        msg: Any,
        color: LogColor | None = None,
        output: LogOutput = LogOutput.ALL,
    ) -> None:
        if self._logger is None:
            return
        self._logger.error(msg, color, output)

    def critical(
        self,
        msg: Any,
        color: LogColor | None = None,
        output: LogOutput = LogOutput.ALL,
    ) -> None:
        if self._logger is None:
            return
        self._logger.critical(msg, color, output)

    def move_logger(
        self,
        new_file: str,
        option: LogMoveOption = LogMoveOption.MOVE_AND_APPEND,
    ) -> None:
        if self._logger is None:
            return
        self._logger.move(new_file, option)

    def set_format(self, fmt: list = []) -> None:
        if self._logger is None:
            return
        self._logger.set_format(fmt)

    def set_color_mode(self, mode: LogColorMode) -> None:
        if self._logger is None:
            return
        self._logger.set_color_mode(mode)

    def set_log_level(self, level: LogLevel) -> None:
        if self._logger is None:
            return
        self._logger.set_log_level(level)

    def release_logger(self) -> None:
        if self._logger is None:
            return
        self._logger.release()
