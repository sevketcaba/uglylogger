import logging
from logging import LogRecord
from enum import IntEnum, Flag, auto
import locale
from datetime import datetime
import inspect
import os
import typing
import shutil
from typing import Tuple, Callable


class LogColorMode(IntEnum):
    """Enumerate LogColorMode"""

    """Colored output if possible"""
    COLORED = (1,)

    """Non-colored output"""
    MONO = 2


class LogColor(IntEnum):
    """LogColor"""

    BLACK = (0,)
    RED = (1,)
    GREEN = (2,)
    YELLOW = (3,)
    BLUE = (4,)
    MAGENTA = (5,)
    CYAN = (6,)
    WHITE = 7


class LogOutput(Flag):
    """Log Output Target"""

    """No output will be generated"""
    NONE = 0

    """Log will be displayed in terminal"""
    CONSOLE = auto()

    """Log will be written into the file"""
    FILE = auto()

    """Log will be displayed in terminal and
        also will be written into the file"""
    ALL = CONSOLE | FILE


class LogLevel(IntEnum):
    """LogLevel"""

    CRITICAL = (50,)
    ERROR = (40,)
    WARNING = (30,)
    INFO = (20,)
    DEBUG = 10

    def __str__(self) -> str:
        """String representation of the LogLevel

        Returns:
            str: String representation of the LogLevel
        """
        match self.value:
            case LogLevel.CRITICAL:
                return "CRITICAL"
            case LogLevel.ERROR:
                return "ERROR"
            case LogLevel.WARNING:
                return "WARNING"
            case LogLevel.INFO:
                return "INFO"
            case LogLevel.DEBUG:
                return "DEBUG"
        return ""  # pragma: no cover


class LogFormatBlock(Flag):
    """Element of the log format"""

    """Prints Logger name"""
    NAME = auto()

    """Prints LogLevel"""
    LEVEL = auto()

    """Prints DateTime"""
    DATETIME = auto()

    """Prints the messae"""
    MESSAGE = auto()

    """Prints the sender file name"""
    FILE = auto()

    """Prints the line number of the log call"""
    LINE = auto()

    """Prints the sender function nam"""
    FUNCTION = auto()


class LogMoveOption(IntEnum):
    """LogMoveOption"""

    """Moves the log file to the destination
       Deletes if there's already a file in the destination
       Appends to the moved file
       Old file is obviously deleted
    """
    MOVE_AND_APPEND = (1,)

    """Copies the log file to the destination
       Deletes if there's already a file in the destination
       Appends to the moved file
       Old file is obviously remains
    """
    COPY_AND_APPEND = (2,)

    """Keeps the old log file
       Appends if there's already a file in the destination
       Creates a new file if not
    """
    KEEP_AND_APPEND = (3,)

    """Keeps the old log file
       Creates a new file in the destination
    """
    KEEP_AND_INIT = (4,)

    """Deletes the old log file
       Creates a new file in the destination
    """
    DELETE_AND_INIT = (5,)


class Logger:
    """The infamous ugly logger class"""

    # static definitions
    DEFAULT_CONSOLE_LOG_LEVEL: LogLevel = LogLevel.DEBUG
    DEFAULT_FILE_LOG_LEVEL: LogLevel = LogLevel.DEBUG
    DEFAULT_LOG_LOG_LEVEL: LogLevel = LogLevel.DEBUG

    DEFAULT_DEBUG_COLOR: LogColor = LogColor.BLACK
    DEFAULT_INFO_COLOR: LogColor = LogColor.BLUE
    DEFAULT_WARNING_COLOR: LogColor = LogColor.YELLOW
    DEFAULT_ERROR_COLOR: LogColor = LogColor.RED
    DEFAULT_CRITICAL_COLOR: LogColor = LogColor.MAGENTA

    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

    # variables
    _logger: logging.Logger | None = None
    _console_handler: logging.StreamHandler | None = None
    _file_handler: logging.FileHandler | None = None
    _format_arr: list = [
        "[",
        LogFormatBlock.NAME,
        "] [",
        LogFormatBlock.LEVEL,
        "] [",
        LogFormatBlock.DATETIME,
        "] (",
        LogFormatBlock.FILE,
        ":",
        LogFormatBlock.LINE,
        ":",
        LogFormatBlock.FUNCTION,
        ") ",
        LogFormatBlock.MESSAGE,
    ]

    _name: str = ""
    _file: str | None = None
    _permanent: bool = True
    _color_mode: LogColorMode = LogColorMode.COLORED

    DEFAULT_LOG_LEVEL: LogLevel = LogLevel.DEBUG
    _log_level: LogLevel = DEFAULT_LOG_LOG_LEVEL

    def __init__(
        self,
        name: str,
        file: str | None = None,
        permanent: bool = False,
        append: bool = True,
        color_mode: LogColorMode = LogColorMode.COLORED,
    ) -> None:
        """The Ugly Logger Constructor

        Args:
            name (str): Name of the logger
            file (str | None, optional): Path to the log file.
                Defaults to None.
            permanent (bool, optional): Do not delete handlers
                after deletion of the instance. Defaults to False.
            append (bool, optional): Do not recreate the files,
                but append to the files. Defaults to True.
            color_mode (LogColorMode, optional): Color mode to use
                for console output. Defaults to LogColorMode.COLORED.
        """

        if locale.getpreferredencoding().upper() != "UTF-8":
            locale.setlocale(locale.LC_ALL, "un_US.UTF-8")
        Logger.DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

        self._name = name
        self._log_level = Logger.DEFAULT_LOG_LOG_LEVEL
        self._init(file, permanent, append, color_mode)

    def __del__(self) -> None:
        """Destructor

        Releases the resources like handlers if logger is not permanent
        """
        if not self._permanent:
            self.release()

    def _init(
        self,
        file: str | None = None,
        permanent: bool = False,
        append: bool = True,
        color_mode: LogColorMode = LogColorMode.COLORED,
    ) -> None:
        self._logger = logging.getLogger(self._name)
        handlers = self._logger.handlers
        if len(handlers) > 0:
            # Load attributes from logger
            self._file = self._logger._file  # type: ignore[attr-defined]
            self._permanent = self._logger._permanent  # type: ignore[attr-defined] # noqa: E501
            self.set_color_mode(self._logger._color_mode)  # type: ignore[attr-defined] # noqa: E501

            for handler in self._logger.handlers:
                if type(handler) is logging.StreamHandler:
                    self._console_handler = handler
                elif type(handler) is logging.FileHandler:
                    self._file_handler = handler
                handler.setLevel(
                    Logger.LogLevelToLoggingLevel(self._log_level)
                )
            return

        self._file = file
        self._logger._file = file  # type: ignore[attr-defined]

        self._permanent = permanent
        self._logger._permanent = permanent  # type: ignore[attr-defined]

        self._logger._color_mode = color_mode  # type: ignore[attr-defined]
        self.set_color_mode(color_mode)

        self._logger.setLevel(Logger.LogLevelToLoggingLevel(self._log_level))

        self._console_handler = logging.StreamHandler()
        self._console_handler.addFilter(self._build_handler_filter("console"))
        self._console_handler.setLevel(
            Logger.LogLevelToLoggingLevel(self._log_level)
        )
        self._logger.addHandler(self._console_handler)

        if not (file is None or file == ""):
            file_mode: str = "a" if append else "w"
            self._file_handler = logging.FileHandler(file, file_mode, "utf-8")
            self._file_handler.addFilter(self._build_handler_filter("file"))
            self._file_handler.setLevel(
                Logger.LogLevelToLoggingLevel(self._log_level)
            )
            self._logger.addHandler(self._file_handler)

    def release(self) -> None:
        """Releases the resources of the logger, like handlers etc."""
        if self._console_handler is not None:
            self._console_handler.close()
            if self._logger is not None:
                self._logger.removeHandler(self._console_handler)
            # del self._console_handler
            self._console_handler = None
        if self._file_handler is not None:
            self._file_handler.close()
            if self._logger is not None:
                self._logger.removeHandler(self._file_handler)
            # del self._file_handler
            self._file_handler = None
        del self._logger
        self._logger = None

        self._file = None
        self._color_mode = LogColorMode.COLORED
        self._permanent = False

        if self._name in logging.Logger.manager.loggerDict:
            del logging.Logger.manager.loggerDict[self._name]

    def set_log_level(self, level: LogLevel) -> None:
        self._log_level = level
        if self._logger is not None:
            for handler in self._logger.handlers:
                handler.setLevel(Logger.LogLevelToLoggingLevel(level))

    @staticmethod
    def LogLevelToColor(level: LogLevel) -> LogColor:
        match level:
            case LogLevel.DEBUG:
                return Logger.DEFAULT_DEBUG_COLOR
            case LogLevel.INFO:
                return Logger.DEFAULT_INFO_COLOR
            case LogLevel.WARNING:
                return Logger.DEFAULT_WARNING_COLOR
            case LogLevel.ERROR:
                return Logger.DEFAULT_ERROR_COLOR
            case LogLevel.CRITICAL:
                return Logger.DEFAULT_CRITICAL_COLOR

    @staticmethod
    def LogLevelToLoggingLevel(level: LogLevel) -> int:
        match level:
            case LogLevel.DEBUG:
                return logging.DEBUG
            case LogLevel.INFO:
                return logging.INFO
            case LogLevel.WARNING:
                return logging.WARN
            case LogLevel.ERROR:
                return logging.ERROR
            case LogLevel.CRITICAL:
                return logging.CRITICAL

    @staticmethod
    def DateTimeToStr(dt) -> str:
        """Converts DateTime object to String

        Args:
            dt (DateTime): DateTime object

        Returns:
            str: Datetime as string in format YYYY-MM-dd HH:mm:ss.zzz
        """
        return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def set_color_mode(self, mode: LogColorMode) -> None:
        """Sets the color mode

        Args:
            mode (LogColorMode): Color Mode
        """
        self._colored = mode == LogColorMode.COLORED

    def _build_handler_filter(
        self, handler: str
    ) -> Callable[[LogRecord], bool]:
        def handler_filter(record: LogRecord) -> bool:
            if hasattr(record, "block"):
                if record.block == handler:
                    return False
            return True

        return handler_filter

    def _color_str(self, color: LogColor) -> str:
        color_seq = "\033[1;%dm"
        return color_seq % (30 + int(color))

    def _msg_to_str(self, msg: typing.Any) -> str:
        return str(msg, "utf-8") if type(msg) is bytes else str(msg)

    def _get_file_line_func(self) -> Tuple[str | None, str | None, int | None]:
        stack = inspect.stack()
        this_fil = str(stack[1][1])
        fil = None
        lin = None
        fun = None
        index = 0
        while True:
            if index < len(stack):
                fil = stack[index][1]
                lin = stack[index][2]
                fun = stack[index][3]

                if fil == this_fil:
                    index += 1
                else:
                    return (fil, fun, lin)
            else:  # pragma: no cover
                break  # pragma: no cover

        return (None, None, None)  # pragma: no cover

    def _format(self, msg: typing.Any, level: LogLevel) -> str:
        formatted = ""
        fil = None
        fun = None
        lin = None
        for item in self._format_arr:
            if type(item) is LogFormatBlock:
                match item:
                    case LogFormatBlock.NAME:
                        formatted += self._name
                    case LogFormatBlock.LEVEL:
                        formatted += str(level)
                    case LogFormatBlock.DATETIME:
                        formatted += Logger.DateTimeToStr(datetime.now())
                    case LogFormatBlock.MESSAGE:
                        formatted += self._msg_to_str(msg)
                    case LogFormatBlock.FILE:
                        if fil is None:  # Lazy init
                            fil, fun, lin = self._get_file_line_func()
                            # formatted += str(fil)
                            if fil is not None:
                                formatted += os.path.basename(fil)
                    case LogFormatBlock.LINE:
                        if fil is None:  # Lazy init
                            fil, fun, lin = self._get_file_line_func()
                        if lin is not None:
                            formatted += str(lin)
                    case LogFormatBlock.FUNCTION:
                        if fil is None:  # Lazy init
                            fil, fun, lin = self._get_file_line_func()
                        if fun is not None:
                            formatted += str(fun)
            else:
                formatted += str(item)

        return formatted

    def _colored_format(
        self, msg: typing.Any, color: LogColor, level: LogLevel
    ) -> str:
        if self._colored:
            return (
                self._color_str(color) + self._format(msg, level) + "\033[0m"
            )
        return self._format(msg, level)

    def set_format(self, fmt: list = []) -> None:
        self._format_arr = fmt

    def console_oneline(
        self,
        msg: typing.Any,
        color: LogColor | None = None,
        console_width: int = 100,
        level: LogLevel = DEFAULT_CONSOLE_LOG_LEVEL,
    ) -> None:
        if console_width <= 0:
            return
        msg_str = self._msg_to_str(msg)
        if msg_str == "":
            print("\r" + " " * console_width, end="\r", flush=True)
            return

        msg_len = len(msg_str)
        msg_to_print = ""
        if msg_len > console_width:
            msg_to_print = msg_str[: console_width - 3] + "..."
        else:
            msg_to_print = msg_str + " " * (console_width - msg_len)

        if self._colored == LogColorMode.COLORED:
            c: LogColor = color
            if c is None:
                c = Logger.LogLevelToColor(level)
            print(
                f"\r{self._color_str(c)}{msg_to_print}\033[0m",
                end="",
                flush=True,
            )
        else:
            print(
                f"\r{msg_to_print}",
                end="",
                flush=True,
            )

    def console(
        self,
        msg: typing.Any,
        color: LogColor | None = None,
        level: LogLevel = DEFAULT_CONSOLE_LOG_LEVEL,
    ) -> None:
        if self._logger is None:
            return  # pragma: no cover
        match level:
            case LogLevel.DEBUG:
                d_color = (
                    color if color is not None else Logger.DEFAULT_DEBUG_COLOR
                )
                self._logger.debug(
                    self._colored_format(msg, d_color, LogLevel.DEBUG),
                    extra={"block": "file"},
                )
            case LogLevel.INFO:
                d_color = (
                    color if color is not None else Logger.DEFAULT_INFO_COLOR
                )
                self._logger.info(
                    self._colored_format(msg, d_color, LogLevel.INFO),
                    extra={"block": "file"},
                )
            case LogLevel.WARNING:
                d_color = (
                    color
                    if color is not None
                    else Logger.DEFAULT_WARNING_COLOR
                )
                self._logger.warning(
                    self._colored_format(msg, d_color, LogLevel.WARNING),
                    extra={"block": "file"},
                )
            case LogLevel.ERROR:
                d_color = (
                    color if color is not None else Logger.DEFAULT_ERROR_COLOR
                )
                self._logger.error(
                    self._colored_format(msg, d_color, LogLevel.ERROR),
                    extra={"block": "file"},
                )
            case LogLevel.CRITICAL:
                d_color = (
                    color
                    if color is not None
                    else Logger.DEFAULT_CRITICAL_COLOR
                )
                self._logger.critical(
                    self._colored_format(msg, d_color, LogLevel.CRITICAL),
                    extra={"block": "file"},
                )

    def file(
        self, msg: typing.Any, level: LogLevel = DEFAULT_FILE_LOG_LEVEL
    ) -> None:
        """Logs to file, but does not log to the console

        Args:
            msg (typing.Any): Message to log
            level (LogLevel, optional): Defaults to LogLevel.DEBUG.
        """
        if self._logger is None:
            return  # pragma: no cover
        match level:
            case LogLevel.DEBUG:
                self._logger.debug(
                    self._format(msg, LogLevel.DEBUG),
                    extra={"block": "console"},
                )
            case LogLevel.INFO:
                self._logger.info(
                    self._format(msg, LogLevel.INFO),
                    extra={"block": "console"},
                )
            case LogLevel.WARNING:
                self._logger.warning(
                    self._format(msg, LogLevel.WARNING),
                    extra={"block": "console"},
                )
            case LogLevel.ERROR:
                self._logger.error(
                    self._format(msg, LogLevel.ERROR),
                    extra={"block": "console"},
                )
            case LogLevel.CRITICAL:
                self._logger.critical(
                    self._format(msg, LogLevel.CRITICAL),
                    extra={"block": "console"},
                )

    def log(
        self,
        msg: typing.Any,
        color: LogColor | None = None,
        level: LogLevel = DEFAULT_LOG_LOG_LEVEL,
        output: LogOutput = LogOutput.ALL,
    ) -> None:
        """Logs both to the file and to the console

        Args:
            msg (typing.Any): Message to log
            color (LogColor | None, optional): Color to overwrite,
                otherwise uses color by the LogLevel. Defaults to None.
            level (LogLevel, optional): Defaults to LogLevel.DEBUG.
            output (LogOutput, optional): Defaults to LogOutput.ALL.
        """
        if LogOutput.CONSOLE in output:
            self.console(msg, color, level)
        if LogOutput.FILE in output:
            self.file(msg, level)

    def debug(
        self,
        msg: typing.Any,
        color: LogColor | None = None,
        output: LogOutput = LogOutput.ALL,
    ) -> None:
        """Logs as debug

        Args:
            msg (typing.Any): Message to log
            color (LogColor, optional): Color to overwrite,
                otherwise uses color by the LogLevel. Defaults to None.
            output (LogOutput, optional): Log to console, file or both.
                Defaults to LogOutput.ALL.
        """
        if LogOutput.CONSOLE in output:
            self.console(msg, color, LogLevel.DEBUG)
        if self._file_handler is not None and LogOutput.FILE in output:
            self.file(msg, LogLevel.DEBUG)

    def info(
        self,
        msg: typing.Any,
        color: LogColor | None = None,
        output: LogOutput = LogOutput.ALL,
    ) -> None:
        """Logs as info

        Args:
            msg (typing.Any): Message to log
            color (LogColor, optional): Color to overwrite,
                otherwise uses color by the LogLevel. Defaults to None.
            output (LogOutput, optional): Log to console, file or both.
                Defaults to LogOutput.ALL.
        """
        if LogOutput.CONSOLE in output:
            self.console(msg, color, LogLevel.INFO)
        if self._file_handler is not None and LogOutput.FILE in output:
            self.file(msg, LogLevel.INFO)

    def warning(
        self,
        msg: typing.Any,
        color: LogColor | None = None,
        output: LogOutput = LogOutput.ALL,
    ) -> None:
        """Logs as warning

        Args:
            msg (typing.Any): Message to log
            color (LogColor, optional): Color to overwrite,
                otherwise uses color by the LogLevel. Defaults to None.
            output (LogOutput, optional): Log to console, file or both.
                Defaults to LogOutput.ALL.
        """
        if LogOutput.CONSOLE in output:
            self.console(msg, color, LogLevel.WARNING)
        if self._file_handler is not None and LogOutput.FILE in output:
            self.file(msg, LogLevel.WARNING)

    def error(
        self,
        msg: typing.Any,
        color: LogColor | None = None,
        output: LogOutput = LogOutput.ALL,
    ) -> None:
        """Logs as error

        Args:
            msg (typing.Any): Message to log
            color (LogColor, optional): Color to overwrite,
                otherwise uses color by the LogLevel. Defaults to None.
            output (LogOutput, optional): Log to console, file or both.
                Defaults to LogOutput.ALL.
        """
        if LogOutput.CONSOLE in output:
            self.console(msg, color, LogLevel.ERROR)
        if self._file_handler is not None and LogOutput.FILE in output:
            self.file(msg, LogLevel.ERROR)

    def critical(
        self,
        msg: typing.Any,
        color: LogColor | None = None,
        output: LogOutput = LogOutput.ALL,
    ) -> None:
        """Logs as critical

        Args:
            msg (typing.Any): Message to log
            color (LogColor, optional): Color to overwrite,
                otherwise uses color by the LogLevel. Defaults to None.
            output (LogOutput, optional): Log to console, file or both.
                Defaults to LogOutput.ALL.
        """
        if LogOutput.CONSOLE in output:
            self.console(msg, color, LogLevel.CRITICAL)
        if self._file_handler is not None and LogOutput.FILE in output:
            self.file(msg, LogLevel.CRITICAL)

    def move(
        self,
        new_file: str,
        option: LogMoveOption = LogMoveOption.MOVE_AND_APPEND,
    ) -> None:
        """Moves the log file to a new destination

        Args:
            new_file (str): New Log File
            option (LogMoveOption): how to behave, Defaults to MOVE_AND_APPEND
                otherwise uses color by the LogLevel. Defaults to None.
        """

        if self._file is None:
            return

        permanent = self._permanent
        color_mode = self._color_mode
        old_file = self._file
        self.release()

        new_file_abs = os.path.abspath(new_file)
        # new_dir = os.path.dirname(new_file_abs)
        # if not os.path.exists(new_dir):
        #     os.makedirs(new_dir)

        append: bool = False
        match option:
            case LogMoveOption.MOVE_AND_APPEND:
                # delete if there's a file in the destionation
                if os.path.exists(new_file_abs):
                    os.remove(new_file_abs)
                # move the file to the destination
                shutil.move(old_file, new_file_abs)
                # append to the new file
                append = True
            case LogMoveOption.COPY_AND_APPEND:
                # delete if there's a file in the destionation
                if os.path.exists(new_file_abs):
                    os.remove(new_file_abs)
                # copy the file to the destination
                shutil.copy(old_file, new_file_abs)
                # append to the new file
                append = True
            case LogMoveOption.KEEP_AND_APPEND:
                # don't delete the old file
                # don't delete if there's a file in the destionation
                # append to the new/existing file
                append = True
            case LogMoveOption.DELETE_AND_INIT:
                # delete the old file
                os.remove(old_file)
                # delete if there's a file in the destionation
                if os.path.exists(new_file_abs):
                    os.remove(new_file_abs)
                # don't append to the new file
                append = False
            case LogMoveOption.KEEP_AND_INIT:
                # don't delete the old file
                # delete if there's a file in the destionation
                if os.path.exists(new_file_abs):
                    os.remove(new_file_abs)
                # don't append to the new file
                append = False

        self._init(new_file_abs, permanent, append, color_mode)
