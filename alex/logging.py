import datetime
import logging
import typing

import rich._log_render
import rich.console
import rich.highlighter
import rich.logging
import rich.text
import rich.traceback


class LogHandler(logging.Handler):
    def __init__(
        self,
        level: typing.Union[int, str] = logging.NOTSET,
    ) -> None:
        super().__init__(level=level)
        self.console = rich.console.Console(width=1000000000)

    def emit(self, record: logging.LogRecord) -> None:
        message_text = rich.text.Text.from_markup(
            self.format(record), style="log.message"
        )

        level = rich.text.Text.styled(
            record.levelname.ljust(8), f"logging.level.{record.levelname.lower()}"
        )

        log_time = datetime.datetime.fromtimestamp(record.created)
        log_time_display = rich.text.Text.styled(
            log_time.strftime("[%x %X]"), style="log.time"
        )

        log_renderable = log_time_display + " " + level + " " + message_text

        try:
            self.console.print(log_renderable)
        except Exception:
            self.handleError(record)
