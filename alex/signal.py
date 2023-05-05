import logging
import signal
import sys

log = logging.getLogger(__name__)


class CatchSigInt:
    def __init__(self):
        self.old_handler = signal.getsignal(signal.SIGINT)
        self.triggered = False

    def _handle_interrupt(self, *_):
        if not self.triggered:
            log.warning(
                "SIGINT received! Waiting for current work to finish. "
                "Interrupt again to exit immediately."
            )
            self.triggered = True
        else:
            log.fatal("Second SIGINT received! Exiting immediately.")
            sys.exit(15)

    def __enter__(self):
        log.debug("Enabling SIGINT handler")
        signal.signal(signal.SIGINT, self._handle_interrupt)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        log.debug("Disabling SIGINT handler")
        signal.signal(signal.SIGINT, self.old_handler)

    def valid(self):
        return not self.triggered
