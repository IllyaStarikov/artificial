"""Simple timer utility."""

from __future__ import annotations

import datetime
import typing


class Timer:
    """A stopwatch-style timer."""

    def __init__(self) -> None:
        """Initialize timer."""
        self._start_time: typing.Optional[datetime.datetime] = None
        self._stop_time: typing.Optional[datetime.datetime] = None

    def start(self) -> None:
        """Start the timer."""
        self._start_time = datetime.datetime.now()

    def stop(self) -> None:
        """Stop the timer."""
        self._stop_time = datetime.datetime.now()

    @property
    def elapsed_seconds(self) -> float:
        """Returns elapsed time in seconds.

        Returns:
            Seconds between start and stop.

        Raises:
            ValueError: If timer wasn't started and stopped.
        """
        if self._start_time is None or self._stop_time is None:
            raise ValueError("Timer must be started and stopped first")
        delta = self._stop_time - self._start_time
        return delta.total_seconds()
