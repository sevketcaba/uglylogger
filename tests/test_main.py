import io
import unittest
import unittest.mock
import os
from inspect import currentframe, getframeinfo
from uglylogger import Logger, LogFormatBlock, LogColorMode


class TestMain(unittest.TestCase):
    _files: list = []
    _loggers: list = []

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    def __del__(self):
        pass

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

    def _delete_logger(self, logger: Logger | None, delete_file: bool = True):
        if logger is None:
            return  # pragma: no cover
        file = logger._file
        self._loggers.remove(logger)
        logger.release()  # don't care about permanent state
        if delete_file:
            self._delete_file(file)
        del logger

    def _delete_file(self, file: str | None) -> None:
        if file is None:
            return  # pragma: no cover
        self._files.remove(file)
        if os.path.exists(file):
            os.remove(file)

    def _read_line_of_log_file(
        self, file: str, line_idx: int = -1
    ) -> str | None:
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
    def test_console_oneline(self, mock):
        logger = self._create_logger("log", color_mode=LogColorMode.MONO)

        logger.console_oneline(1)

        received_val = mock.getvalue().strip()
        expected_val = ("\r1" + " " * 99).strip()
        self.assertEqual(expected_val, received_val)

        self._delete_logger(logger)

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_console_oneline_negative_width(self, mock):
        logger = self._create_logger("log", color_mode=LogColorMode.MONO)

        logger.console_oneline(1, console_width=-1)

        received_val = mock.getvalue().strip()
        expected_val = ""
        self.assertEqual(expected_val, received_val)

        self._delete_logger(logger)

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_console_oneline_empty_msg(self, mock):
        logger = self._create_logger("log", color_mode=LogColorMode.MONO)

        logger.console_oneline("")

        received_val = mock.getvalue().strip()
        expected_val = ""
        self.assertEqual(expected_val, received_val)

        self._delete_logger(logger)

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_console_oneline_msg_longer_than_console_width(self, mock):
        logger = self._create_logger("log", color_mode=LogColorMode.MONO)

        logger.console_oneline("1234567890", console_width=5)

        received_val = mock.getvalue().strip()
        expected_val = "12..."
        self.assertEqual(expected_val, received_val)

        self._delete_logger(logger)

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_console_oneline_msg_longer_equal_console_width(self, mock):
        logger = self._create_logger("log", color_mode=LogColorMode.MONO)

        logger.console_oneline("12345", console_width=5)

        received_val = mock.getvalue().strip()
        expected_val = "12345"
        self.assertEqual(expected_val, received_val)

        self._delete_logger(logger)

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_console_oneline_msg_longer_equal_console_width_colored(
        self, mock
    ):
        logger = self._create_logger("log")

        logger.console_oneline("12345", console_width=5)

        received_val = mock.getvalue().strip()
        expected_val = "\x1b[1;30m12345\x1b[0m"
        self.assertEqual(expected_val, received_val)

        self._delete_logger(logger)

    def test_log_file_creation(self):
        file_name = "test_log_file_creation.log"
        logger = self._create_logger("test_log_file_creation", file_name)
        logger.set_format([LogFormatBlock.MESSAGE])
        logger.debug("DEBUG LOG HERE")
        self.assertEqual(
            True, os.path.exists(file_name), f"{file_name} file not found"
        )
        self._delete_logger(logger, True)

    def test_log_file_contains_content(self):
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

    def test_logger_reinstantiate_permanent(self):
        logger_first = self._create_logger(
            "debug_logger", "test_logger_reinstantiate_permanent.log", True
        )
        console_handler_first = logger_first._console_handler

        logger_second = self._create_logger("debug_logger")
        console_handler_second = logger_second._console_handler

        self.assertEqual(console_handler_first, console_handler_second)

        self._delete_logger(logger_first, False)
        self._delete_logger(logger_second, True)

    def test_levels(self):
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

    def _create_test_format_logger(self, name):
        logger_name = name
        file_name = name + ".log"
        return self._create_logger(logger_name, file_name)

    def test_format_name(self):
        logger = self._create_test_format_logger("test_format_name")

        logger.set_format([LogFormatBlock.NAME])
        logger.debug("FORMAT: NAME")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, "test_format_name")

        self._delete_logger(logger)

    def test_format_level(self):
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

    def test_format_datetime(self):
        logger = self._create_test_format_logger("test_format_datetime")

        logger.set_format([LogFormatBlock.DATETIME])
        logger.debug("FORMAT: DATETIME")
        line = self._read_line_of_log_file(logger._file)
        expected_format_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}"
        self.assertRegex(line, expected_format_pattern)

        self._delete_logger(logger)

    def test_format_message(self):
        logger = self._create_test_format_logger("test_format_message")

        logger.set_format([LogFormatBlock.MESSAGE])
        msg = "FORMAT: MESSAGE"
        logger.debug(msg)
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, msg)

        self._delete_logger(logger)

    def test_format_file(self):
        logger = self._create_test_format_logger("test_format_file")

        logger.set_format([LogFormatBlock.FILE])
        logger.debug("FORMAT: FILE")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, os.path.basename(__file__))

        self._delete_logger(logger)

    def test_format_line(self):
        logger = self._create_test_format_logger("test_format_line")

        logger.set_format([LogFormatBlock.LINE])

        frameinfo = getframeinfo(currentframe())
        line_number = frameinfo.lineno
        logger.debug("FORMAT: LINE")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, str(line_number + 2))

        self._delete_logger(logger)

    def test_format_func(self):
        logger = self._create_test_format_logger("test_format_func")

        logger.set_format([LogFormatBlock.FUNCTION])
        logger.debug("FORMAT: FUNCTION")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, "test_format_func")

        self._delete_logger(logger)

    def test_format_all(self):
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
        expected_pattern = r"\[([^\]]+)\] \[([^\]]+)\] \[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{3}\] \(([^:]+\.py):(\d+):([^)]+)\) ([^$]+)"  # noqa: E501

        self.assertRegex(line, expected_pattern)

        self._delete_logger(logger)

    def test_log(self):
        logger = self._create_logger("log", "log.log")
        logger.set_format([LogFormatBlock.MESSAGE])
        logger.log("LOG")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, "LOG")

        self._delete_logger(logger)

    def test_noncolor(self):
        logger = self._create_logger(
            "log", "log.log", color_mode=LogColorMode.MONO
        )
        logger.set_format([LogFormatBlock.MESSAGE])
        logger.log("MONOLOG")
        line = self._read_line_of_log_file(logger._file)
        self.assertEqual(line, "MONOLOG")

        self._delete_logger(logger)


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
