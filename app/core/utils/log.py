from logging import Logger, getLogger, INFO, WARN, ERROR, CRITICAL, Formatter, StreamHandler
from typing import Literal, Final

LogLevel = Literal['INFO','WARN','ERROR','CRITICAL']
LogLevelMap: Final[dict[LogLevel,int]] = {'INFO': INFO, 'WARN': WARN, 'ERROR': ERROR, 'CRITICAL': CRITICAL}
logger = getLogger()

def configure_logger() -> None:
    handler = StreamHandler()
    formatter = Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )


    # push config
    handler.setFormatter(formatter)
    logger.addHandler(handler)

class Logged:
    def __init_subclass__(cls) -> None:
        cls.logger = getLogger(cls.__name__)
        pass

    @classmethod
    def _log(cls, level: LogLevel, fmt_str: str, *args):
        logger = getattr(cls, 'logger', None)
        if logger and isinstance(logger, Logger):
            logger.log(LogLevelMap.get(level, 0),fmt_str, *args)