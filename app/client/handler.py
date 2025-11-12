from __future__ import annotations

import atexit
import threading
from dataclasses import dataclass
from queue import Empty, Queue
from typing import Callable, Optional, Tuple

from blessed import Terminal

REFRESH_INTERVAL = 0.05
Location = Tuple[int, int]


@dataclass(slots=True)
class OutputMessage:
    text: str = ""
    end: str = "\n"
    flush: bool = True
    location: Optional[Location] = None
    formatter: Optional[Callable[[Terminal, str], str]] = None
    clear: bool = False
    shutdown: bool = False


class IOHandler:
    def __init__(self) -> None:
        self.term = Terminal()
        self._queue: Queue[OutputMessage] = Queue()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        self.running = True
        atexit.register(self.stop)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="IOHandlerThread",
            daemon=True,
        )
        self._thread.start()

    def enqueue(
        self,
        message: OutputMessage,
    ) -> None:
        self.start()
        self._queue.put(message)

    def enqueue_text(
        self,
        text: str,
        *,
        end: str = "\n",
        flush: bool = True,
        location: Optional[Location] = None,
        formatter: Optional[Callable[[Terminal, str], str]] = None,
        clear: bool = False,
    ) -> None:
        self.enqueue(
            OutputMessage(
                text=text,
                end=end,
                flush=flush,
                location=location,
                formatter=formatter,
                clear=clear,
            )
        )

    def stop(self, wait: bool = True) -> None:
        if self._stop_event.is_set():
            return
        self._stop_event.set()
        self._queue.put(OutputMessage(shutdown=True))
        if wait and self._thread and self._thread.is_alive():
            self._thread.join()
        self._thread = None

    def _run(self) -> None:
        while self.running and not self._stop_event.is_set():
            with self.term.fullscreen(), self.term.hidden_cursor():
                print(self.term.home + self.term.clear)
                while True:
                    try:
                        message = self._queue.get(timeout=REFRESH_INTERVAL)
                    except Empty:
                        if self._stop_event.is_set():
                            break
                        continue

                    if message.shutdown:
                        self._queue.task_done()
                        break

                    self._render(message)
                    self._queue.task_done()

            while not self._queue.empty():
                self._queue.get_nowait()
                self._queue.task_done()

    def _render(self, message: OutputMessage) -> None:
        if message.clear:
            print(self.term.home + self.term.clear, end="", flush=True)

        rendered = (
            message.formatter(self.term, message.text)
            if message.formatter
            else message.text
        )

        if message.location:
            x, y = message.location
            with self.term.location(x, y):
                print(rendered, end=message.end, flush=message.flush)
        else:
            print(rendered, end=message.end, flush=message.flush)


_default_handler = IOHandler()


def queue_output(
    text: str,
    *,
    end: str = "\n",
    flush: bool = True,
    location: Optional[Location] = None,
    formatter: Optional[Callable[[Terminal, str], str]] = None,
    clear: bool = False,
) -> None:
    _default_handler.enqueue_text(
        text,
        end=end,
        flush=flush,
        location=location,
        formatter=formatter,
        clear=clear,
    )


__all__ = ["OutputMessage", "IOHandler", "queue_output"]