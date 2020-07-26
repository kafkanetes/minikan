import logging


class ConsoleLog(object):
    """Console logging that can be configured by verbosity levels."""

    def __init__(self, root=None, root_level=logging.INFO):
        self.root = logging.getLogger() if root is None else root
        self.root.setLevel(root_level)
        self.__file_handler = None
        self.__console_handler = None

    @property
    def console_handler(self):
        if self.__console_handler is None:
            self.__console_handler = logging.StreamHandler()
        return self.__console_handler

    def map_verbosity_to_level(self, value):
        """Verbosity value is just an integer count of v-char in `-vvvv`."""
        return logging.CRITICAL - (value * 10) % logging.CRITICAL

    def set_console_handler(self, verbosity):
        self.console_handler.setLevel(self.map_verbosity_to_level(verbosity))
        # if self.root.level < self.console_handler.level:
        #     self.root.level = self.console_handler.level
        self.root.level = self.console_handler.level
        format_str = '%(asctime)s %(name)-30s %(levelname)-8s %(message)s'
        datefmt_str = '%m-%d %H:%M:%S'
        self.console_handler.setFormatter(
            logging.Formatter(format_str, datefmt_str))
        self.root.addHandler(self.console_handler)
