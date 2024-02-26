import io
import unittest
import unittest.mock
import os
from inspect import currentframe, getframeinfo, Traceback
from uglylogger import (
    Logger,
    LogFormatBlock,
    LogColorMode,
    LogMoveOption,
    LogLevel,
    LogColor,
)
from parameterized import parameterized  # type: ignore
from types import FrameType


class TestMain(unittest.TestCase):
    _files: list = []
    _loggers: list = []

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        if not os.path.exists("test_logs"):
            os.mkdir("test_logs")

    def __del__(self) -> None:
        if os.path.exists("test_logs"):
            os.rmdir("test_logs")

    def _create_logger(
        self,
        name: str,
        file: str | None = None,
        permanent: bool = False,
        append: bool = True,
        color_mode: LogColorMode = LogColorMode.COLORED,
    ) -> Logger:
        logger = Logger(name, file, permanent, append, color_mode)
        self._loggers.append(logger)
        if file is not None:
            self._files.append(file)
        return logger

    def _delete_logger(
        self, logger: Logger | None, delete_file: bool = True
    ) -> None:
        if logger is None:
            return  # pragma: no cover
        file = logger._file
        if logger in self._loggers:
            self._loggers.remove(logger)
        logger.release()  # don't care about permanent state
        if delete_file:
            self._delete_file(file)
        del logger

    def _delete_file(self, file: str | None) -> None:
        if file is None:
            return  # pragma: no cover
        if file in self._files:
            self._files.remove(file)
        if os.path.exists(file):
            os.remove(file)

    def _read_line_of_log_file(
        self, file: str | None, line_idx: int = -1
    ) -> str | None:
        if file is None:
            return None
        lines: list[str] = []
        with open(file, "r") as f:
            for line in f:
                lines.append(line)
        if line_idx < 0:
            line_idx = len(lines) + line_idx
        if line_idx >= 0 and line_idx < len(lines):
            return lines[line_idx].rstrip("\n")
        return None  # pragma: no cover

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_console_oneline(self, mock) -> None:
        logger = self._create_logger("log", color_mode=LogColorMode.MONO)

        logger.console_oneline(1)

        received_val = mock.getvalue().strip()
        expected_val = ("\r1" + " " * 99).strip()
        self.assertEqual(expected_val, received_val)

        self._delete_logger(logger)

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_console_oneline_negative_width(self, mock) -> None:
        logger = self._create_logger("log", color_mode=LogColorMode.MONO)

        logger.console_oneline(1, console_width=-1)

        received_val = mock.getvalue().strip()
        expected_val = ""
        self.assertEqual(expected_val, received_val)

        self._delete_logger(logger)

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_console_oneline_empty_msg(self, mock) -> None:
        logger = self._create_logger("log", color_mode=LogColorMode.MONO)

        logger.console_oneline("")

        received_val = mock.getvalue().strip()
        expected_val = ""
        self.assertEqual(expected_val, received_val)

        self._delete_logger(logger)

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_console_oneline_msg_longer_than_console_width(self, mock) -> None:
        logger = self._create_logger("log", color_mode=LogColorMode.MONO)

        logger.console_oneline("1234567890", console_width=5)

        received_val = mock.getvalue().strip()
        expected_val = "12..."
        self.assertEqual(expected_val, received_val)

        self._delete_logger(logger)

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_console_oneline_msg_longer_equal_console_width(
        self, mock
    ) -> None:
        logger = self._create_logger("log", color_mode=LogColorMode.MONO)

        logger.console_oneline("12345", console_width=5)

        received_val = mock.getvalue().strip()
        expected_val = "12345"
        self.assertEqual(expected_val, received_val)

        self._delete_logger(logger)

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_console_oneline_msg_longer_equal_console_width_colored(
        self, mock
    ) -> None:
        logger = self._create_logger("log")

        logger.console_oneline("12345", console_width=5)

        received_val = mock.getvalue().strip()
        expected_val = "\x1b[1;30m12345\x1b[0m"
        self.assertEqual(expected_val, received_val)

        self._delete_logger(logger)

    def test_log_file_creation(self) -> None:
        file_name = "test_log_file_creation.log"
        logger = self._create_logger("test_log_file_creation", file_name)
        logger.set_format([LogFormatBlock.MESSAGE])
        logger.debug("DEBUG LOG HERE")
        self.assertEqual(
            True, os.path.exists(file_name), f"{file_name} file not found"
        )
        self._delete_logger(logger, True)

    def test_log_file_contains_content(self) -> None:
        file_name = "test_log_file_contains_content.log"
        logger = self._create_logger("debug_logger", file_name)
        logger.set_format([LogFormatBlock.MESSAGE])
        log_line = "DEBUG LOG HERE"
        logger.debug(log_line)
        last_line_in_file = self._read_line_of_log_file(file_name, -1)
        self.assertIsNotNone(
            last_line_in_file, f"{file_name} does not contain anything"
        )
        self.assertEqual(last_line_in_file, log_line, last_line_in_file)
        self._delete_logger(logger, True)

    def test_logger_reinstantiate_permanent(self) -> None:
        logger_first = self._create_logger(
            "debug_logger", "test_logger_reinstantiate_permanent.log", True
        )
        console_handler_first = logger_first._console_handler

        logger_second = self._create_logger("debug_logger")
        console_handler_second = logger_second._console_handler

        self.assertEqual(console_handler_first, console_handler_second)

        self._delete_logger(logger_first, False)
        self._delete_logger(logger_second, True)

    def test_level_default(self) -> None:
        file = "test_levels.log"
        logger = self._create_logger("test_levels", file)
        logger.set_format([LogFormatBlock.MESSAGE])
        # debug
        logger.debug("DEBUG")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("DEBUG", line)
        # info
        logger.info("INFO")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("INFO", line)
        # warning
        logger.warning("WARNING")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("WARNING", line)
        # error
        logger.error("ERROR")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("ERROR", line)
        # critical
        logger.critical("CRITICAL")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("CRITICAL", line)

        self._delete_logger(logger, True)

    def test_level_debug(self) -> None:
        file = "test_level_debug.log"
        logger = self._create_logger("test_level_debug", file)
        logger.set_format([LogFormatBlock.MESSAGE])
        logger.set_log_level(LogLevel.DEBUG)

        # debug
        logger.debug("DEBUG")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("DEBUG", line)
        # info
        logger.info("INFO")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("INFO", line)
        # warning
        logger.warning("WARNING")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("WARNING", line)
        # error
        logger.error("ERROR")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("ERROR", line)
        # critical
        logger.critical("CRITICAL")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("CRITICAL", line)

        self._delete_logger(logger, True)

    def test_level_info(self) -> None:
        file = "test_level_info.log"
        logger = self._create_logger("test_level_info", file)
        logger.set_format([LogFormatBlock.MESSAGE])
        logger.set_log_level(LogLevel.INFO)

        # debug
        logger.debug("DEBUG")
        line = self._read_line_of_log_file(logger._file)
        self.assertNotEqual("DEBUG", line)
        # info
        logger.info("INFO")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("INFO", line)
        # warning
        logger.warning("WARNING")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("WARNING", line)
        # error
        logger.error("ERROR")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("ERROR", line)
        # critical
        logger.critical("CRITICAL")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("CRITICAL", line)

        self._delete_logger(logger, True)

    def test_level_warning(self) -> None:
        file = "test_level_warning.log"
        logger = self._create_logger("test_level_warning", file)
        logger.set_format([LogFormatBlock.MESSAGE])
        logger.set_log_level(LogLevel.WARNING)

        # debug
        logger.debug("DEBUG")
        line = self._read_line_of_log_file(logger._file)
        self.assertNotEqual("DEBUG", line)
        # info
        logger.info("INFO")
        line = self._read_line_of_log_file(logger._file)
        self.assertNotEqual("INFO", line)
        # warning
        logger.warning("WARNING")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("WARNING", line)
        # error
        logger.error("ERROR")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("ERROR", line)
        # critical
        logger.critical("CRITICAL")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("CRITICAL", line)

        self._delete_logger(logger, True)

    def test_level_error(self) -> None:
        file = "test_level_error.log"
        logger = self._create_logger("test_level_error", file)
        logger.set_format([LogFormatBlock.MESSAGE])
        logger.set_log_level(LogLevel.ERROR)

        # debug
        logger.debug("DEBUG")
        line = self._read_line_of_log_file(logger._file)
        self.assertNotEqual("DEBUG", line)
        # info
        logger.info("INFO")
        line = self._read_line_of_log_file(logger._file)
        self.assertNotEqual("INFO", line)
        # warning
        logger.warning("WARNING")
        line = self._read_line_of_log_file(logger._file)
        self.assertNotEqual("WARNING", line)
        # error
        logger.error("ERROR")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("ERROR", line)
        # critical
        logger.critical("CRITICAL")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("CRITICAL", line)

        self._delete_logger(logger, True)

    def test_level_critical(self) -> None:
        file = "test_level_critical.log"
        logger = self._create_logger("test_level_critical", file)
        logger.set_format([LogFormatBlock.MESSAGE])
        logger.set_log_level(LogLevel.CRITICAL)

        # debug
        logger.debug("DEBUG")
        line = self._read_line_of_log_file(logger._file)
        self.assertNotEqual("DEBUG", line)
        # info
        logger.info("INFO")
        line = self._read_line_of_log_file(logger._file)
        self.assertNotEqual("INFO", line)
        # warning
        logger.warning("WARNING")
        line = self._read_line_of_log_file(logger._file)
        self.assertNotEqual("WARNING", line)
        # error
        logger.error("ERROR")
        line = self._read_line_of_log_file(logger._file)
        self.assertNotEqual("ERROR", line)
        # critical
        logger.critical("CRITICAL")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual("CRITICAL", line)

        self._delete_logger(logger, True)

    def test_log_level_color(self) -> None:
        color: LogColor = Logger.LogLevelToColor(LogLevel.DEBUG)
        self.assertEqual(color, Logger.DEFAULT_DEBUG_COLOR)

        color = Logger.LogLevelToColor(LogLevel.INFO)
        self.assertEqual(color, Logger.DEFAULT_INFO_COLOR)

        color = Logger.LogLevelToColor(LogLevel.WARNING)
        self.assertEqual(color, Logger.DEFAULT_WARNING_COLOR)

        color = Logger.LogLevelToColor(LogLevel.ERROR)
        self.assertEqual(color, Logger.DEFAULT_ERROR_COLOR)

        color = Logger.LogLevelToColor(LogLevel.CRITICAL)
        self.assertEqual(color, Logger.DEFAULT_CRITICAL_COLOR)

    def _create_test_format_logger(self, name) -> Logger:
        logger_name = name
        file_name = name + ".log"
        return self._create_logger(logger_name, file_name)

    def test_testfile_readline_from_none(self) -> None:
        line = self._read_line_of_log_file(None)
        self.assertIsNone(line)

    def test_format_name(self) -> None:
        logger = self._create_test_format_logger("test_format_name")

        logger.set_format([LogFormatBlock.NAME])
        logger.debug("FORMAT: NAME")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, "test_format_name")

        self._delete_logger(logger)

    def test_format_level(self) -> None:
        logger = self._create_test_format_logger("test_format_level")

        logger.set_format([LogFormatBlock.LEVEL])

        logger.debug("FORMAT: LEVEL")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, "DEBUG")

        logger.info("FORMAT: LEVEL")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, "INFO")

        logger.warning("FORMAT: LEVEL")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, "WARNING")

        logger.error("FORMAT: LEVEL")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, "ERROR")

        logger.critical("FORMAT: LEVEL")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, "CRITICAL")

        self._delete_logger(logger)

    def test_format_datetime(self) -> None:
        logger = self._create_test_format_logger("test_format_datetime")

        logger.set_format([LogFormatBlock.DATETIME])
        logger.debug("FORMAT: DATETIME")
        line = self._read_line_of_log_file(logger._file)
        self.assertIsNotNone(line)
        if line is not None:
            expected_format_pattern = (
                r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}"
            )
            self.assertRegex(line, expected_format_pattern)

        self._delete_logger(logger)

    def test_format_message(self) -> None:
        logger = self._create_test_format_logger("test_format_message")

        logger.set_format([LogFormatBlock.MESSAGE])
        msg = "FORMAT: MESSAGE"
        logger.debug(msg)
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, msg)

        self._delete_logger(logger)

    def test_format_file(self) -> None:
        logger = self._create_test_format_logger("test_format_file")

        logger.set_format([LogFormatBlock.FILE])
        logger.debug("FORMAT: FILE")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, os.path.basename(__file__))

        self._delete_logger(logger)

    def test_format_line(self) -> None:
        logger = self._create_test_format_logger("test_format_line")

        logger.set_format([LogFormatBlock.LINE])

        c_frame: FrameType | None = currentframe()
        self.assertIsNotNone(c_frame)
        if c_frame is not None:
            frameinfo: Traceback = getframeinfo(c_frame)
            line_number = frameinfo.lineno
            logger.debug("FORMAT: LINE")
            line = self._read_line_of_log_file(logger._file)
            self.assertEqual(line, str(line_number + 2))

        self._delete_logger(logger)

    def test_format_func(self) -> None:
        logger = self._create_test_format_logger("test_format_func")

        logger.set_format([LogFormatBlock.FUNCTION])
        logger.debug("FORMAT: FUNCTION")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, "test_format_func")

        self._delete_logger(logger)

    def test_format_all(self) -> None:
        logger = self._create_test_format_logger("test_format_all")

        logger.set_format(
            [
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
        )
        logger.debug("FORMAT: [NAME] [DATETIME] (FILE:LINE:FUNC) MSG")
        line = self._read_line_of_log_file(logger._file)
        self.assertIsNotNone(line)
        if line is not None:
            expected_pattern = r"\[([^\]]+)\] \[([^\]]+)\] \[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}\] \(([^:]+\.py):(\d+):([^)]+)\) ([^$]+)"  # noqa: E501
            self.assertRegex(line, expected_pattern)

        self._delete_logger(logger)

    def test_log(self) -> None:
        logger = self._create_logger("log", "log.log")
        logger.set_format([LogFormatBlock.MESSAGE])
        logger.log("LOG")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, "LOG")

        self._delete_logger(logger)

    def test_noncolor(self) -> None:
        logger = self._create_logger(
            "log", "log.log", color_mode=LogColorMode.MONO
        )
        logger.set_format([LogFormatBlock.MESSAGE])
        logger.log("MONOLOG")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, "MONOLOG")

        self._delete_logger(logger)

    @parameterized.expand([(True), (False)])
    def test_release_and_recreate(self, append: bool) -> None:
        logger_first = self._create_logger("log_first", "log_first.log")
        logger_first.set_format([LogFormatBlock.MESSAGE])
        logger_first.log("First")
        logger_first.release()

        logger_second = self._create_logger(
            "log_second", "log_first.log", append=append
        )
        logger_second.set_format([LogFormatBlock.MESSAGE])
        logger_second.log("Second")

        line = self._read_line_of_log_file(logger_second._file, 0)

        if append:
            self.assertEqual(line, "First")
            line = self._read_line_of_log_file(logger_second._file, 1)
            self.assertEqual(line, "Second")

        self.assertEqual(line, "Second")

        self._delete_logger(logger_first)
        self._delete_logger(logger_second)

    @parameterized.expand(
        [
            (LogMoveOption.MOVE_AND_APPEND, True),
            (LogMoveOption.MOVE_AND_APPEND, False),
            (LogMoveOption.COPY_AND_APPEND, True),
            (LogMoveOption.COPY_AND_APPEND, False),
            (LogMoveOption.KEEP_AND_APPEND, True),
            (LogMoveOption.KEEP_AND_APPEND, False),
            (LogMoveOption.KEEP_AND_INIT, True),
            (LogMoveOption.KEEP_AND_INIT, False),
            (LogMoveOption.DELETE_AND_INIT, True),
            (LogMoveOption.DELETE_AND_INIT, False),
        ]
    )
    def test_move_file(
        self, option: LogMoveOption, target_has_file: bool
    ) -> None:
        old_file = "log_to_move.log"
        new_file = "log_moved.log"

        if target_has_file:
            # create a file at the destination
            tmp_logger = self._create_logger("tmp", new_file)
            tmp_logger.set_format([LogFormatBlock.MESSAGE])
            tmp_logger.log("Already There")
            # delete logger but don't delete file
            self._delete_logger(tmp_logger, False)

        logger = self._create_logger("logger", old_file)
        logger.set_format([LogFormatBlock.MESSAGE])
        logger.log("Before Move")
        self.assertTrue(os.path.exists(old_file))

        line = self._read_line_of_log_file(logger._file, 0)
        self.assertEqual(line, "Before Move")

        logger.move(new_file, option)

        match option:
            case LogMoveOption.MOVE_AND_APPEND:
                # moves the file and append to it
                # old file should be deleted
                self.assertFalse(os.path.exists(old_file))
                # new file should be created
                self.assertTrue(os.path.exists(new_file))
                # insert a new line
                logger.log("After Move")
                # both lines should exist in the new file
                line = self._read_line_of_log_file(logger._file, 0)
                self.assertEqual(line, "Before Move")
                line = self._read_line_of_log_file(logger._file, 1)
                self.assertEqual(line, "After Move")
            case LogMoveOption.COPY_AND_APPEND:
                # copies the file and append to it
                # old file should exist
                self.assertTrue(os.path.exists(old_file))
                # new file should be created
                self.assertTrue(os.path.exists(new_file))
                # insert a new line
                logger.log("After Move")
                # both lines should exist in the new file
                line = self._read_line_of_log_file(logger._file, 0)
                self.assertEqual(line, "Before Move")
                line = self._read_line_of_log_file(logger._file, 1)
                self.assertEqual(line, "After Move")
            case LogMoveOption.KEEP_AND_APPEND:
                # keeps the file but append to
                #   whatever exists in the new location
                # new file should exist even before creation
                self.assertTrue(os.path.exists(new_file))
                # old file should exist
                self.assertTrue(os.path.exists(old_file))
                # new file should still exist
                self.assertTrue(os.path.exists(new_file))
                # insert a new line
                logger.log("After Move")

                line = self._read_line_of_log_file(logger._file, 0)
                if target_has_file:
                    self.assertEqual(line, "Already There")
                    line = self._read_line_of_log_file(logger._file, 1)
                    self.assertEqual(line, "After Move")
                else:
                    self.assertEqual(line, "After Move")
            case LogMoveOption.KEEP_AND_INIT:
                # keeps the file and create a new file in the new location
                self.assertTrue(os.path.exists(old_file))
                self.assertTrue(os.path.exists(new_file))
                logger.log("After Move")
                line = self._read_line_of_log_file(logger._file, 0)
                self.assertEqual(line, "After Move")
            case LogMoveOption.DELETE_AND_INIT:
                # deletes the file and create a new file in the new location
                self.assertFalse(os.path.exists(old_file))
                self.assertTrue(os.path.exists(new_file))
                logger.log("After Move")
                line = self._read_line_of_log_file(logger._file, 0)
                self.assertEqual(line, "After Move")

        self._delete_logger(logger)
        self._delete_file(old_file)
        self._delete_file(new_file)

    def test_move_none_file(self) -> None:
        logger = self._create_logger("logger", None)
        logger.set_format([LogFormatBlock.MESSAGE])
        logger.log("Before Move")

        logger.move("new_log_file.log")
        self.assertFalse(os.path.exists("new_log_file.log"))


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
