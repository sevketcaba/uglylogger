import unittest
import unittest.mock
from uglylogger import LogBase, Logger, LogFormatBlock, LogColorMode, LogLevel
import io


class TestLogBase(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        Logger._format_arr = [LogFormatBlock.MESSAGE]

    def _test_log_base(self, logbase: LogBase, mock, expect_log: bool) -> None:
        logbase.console_oneline(1)
        received_val = mock.getvalue().strip()
        expected_val = ("\r1" + " " * 99).strip()
        if expect_log:
            self.assertEqual(expected_val, received_val)
        else:
            self.assertNotEqual(expected_val, received_val)

        logbase.console(1)
        received_val = mock.getvalue().strip()
        expected_val = ("\r1").strip()
        if expect_log:
            self.assertEqual(expected_val, received_val)
        else:
            self.assertNotEqual(expected_val, received_val)

        logbase.log(1)
        received_val = mock.getvalue().strip()
        expected_val = ("\r1").strip()
        if expect_log:
            self.assertEqual(expected_val, received_val)
        else:
            self.assertNotEqual(expected_val, received_val)

        logbase.debug(1)
        received_val = mock.getvalue().strip()
        expected_val = ("\r1").strip()
        if expect_log:
            self.assertEqual(expected_val, received_val)
        else:
            self.assertNotEqual(expected_val, received_val)

        logbase.info(1)
        received_val = mock.getvalue().strip()
        expected_val = ("\r1").strip()
        if expect_log:
            self.assertEqual(expected_val, received_val)
        else:
            self.assertNotEqual(expected_val, received_val)

        logbase.warning(1)
        received_val = mock.getvalue().strip()
        expected_val = ("\r1").strip()
        if expect_log:
            self.assertEqual(expected_val, received_val)
        else:
            self.assertNotEqual(expected_val, received_val)

        logbase.error(1)
        received_val = mock.getvalue().strip()
        expected_val = ("\r1").strip()
        if expect_log:
            self.assertEqual(expected_val, received_val)
        else:
            self.assertNotEqual(expected_val, received_val)

        logbase.critical(1)
        received_val = mock.getvalue().strip()
        expected_val = ("\r1").strip()
        if expect_log:
            self.assertEqual(expected_val, received_val)
        else:
            self.assertNotEqual(expected_val, received_val)

        # not crash counts as pass :)
        logbase.file(1)

        # not crash counts as pass :)
        logbase.move_logger("no_file_will_be_created_hopefully.log")

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_constructor_with_logger(self, mock) -> None:
        logger = Logger("set_logger")
        logger.set_color_mode(LogColorMode.MONO)
        logbase = LogBase(logger)

        self._test_log_base(logbase, mock, True)

        logbase.release_logger()

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_constructor_without_logger(self, mock) -> None:
        logbase = LogBase()

        self._test_log_base(logbase, mock, False)

        logbase.release_logger()

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_set_logger(self, mock) -> None:
        logger = Logger("set_logger")
        logger.set_color_mode(LogColorMode.MONO)
        logbase = LogBase()
        logbase.set_logger(logger)

        self._test_log_base(logbase, mock, True)

        logbase.release_logger()

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_set_logger_none(self, mock) -> None:
        logger = Logger("set_logger")
        logger.set_color_mode(LogColorMode.MONO)
        logbase = LogBase(logger)
        logbase.set_logger(None)

        self._test_log_base(logbase, mock, False)

        logger.release()

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_init_logger(self, mock) -> None:
        logbase = LogBase()
        logbase.init_logger("init_logger")
        logbase.set_format([LogFormatBlock.MESSAGE])
        logbase.set_color_mode(LogColorMode.MONO)
        logbase.set_log_level(LogLevel.DEBUG)
        self._test_log_base(logbase, mock, True)
        logbase.release_logger()

    @unittest.mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_none_logger(self, mock) -> None:
        logbase = LogBase()
        logbase.set_format([LogFormatBlock.MESSAGE])
        logbase.set_color_mode(LogColorMode.MONO)
        logbase.set_log_level(LogLevel.DEBUG)
        self._test_log_base(logbase, mock, False)


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
