import logging
import threading
from concurrent.futures import ThreadPoolExecutor

from django import db

logger = logging.getLogger(__name__)


class DBSafeThreadPoolExecutor(ThreadPoolExecutor):
    """
    A ThreadPoolExecutor that safely manages Django database connections.

    This executor ensures that database connections are properly initialized
    for each worker thread and safely closed during shutdown, preventing
    connection leaks when using Django's ORM in multithreaded environments.
    """

    def generate_initializer(self, initializer):
        def new_initializer(*args, **kwargs):
            self, *args = args
            try:
                if initializer != None:
                    initializer(*args, **kwargs)
            finally:
                self.on_thread_init()

        return new_initializer

    def on_thread_init(self):
        for curr_conn in db.connections.all():
            curr_conn.connection = None
            self.threads_db_conns.append(curr_conn)

    def on_executor_shutdown(self):
        [t.join() for t in self._threads if t != threading.current_thread()]
        for curr_conn in self.threads_db_conns:
            try:
                curr_conn.inc_thread_sharing()
                curr_conn.close()
            except Exception:
                logger.error(
                    f"error while closing connection {curr_conn.alias}", exc_info=True
                )

    def __init__(self, *args, **kwargs):
        kwargs["initializer"] = self.generate_initializer(kwargs.get("initializer"))
        kwargs["initargs"] = (self,) + (kwargs.get("initargs") or ())
        self.threads_db_conns = []
        super().__init__(*args, **kwargs)

    def shutdown(self, *args, **kwargs):
        self.submit(self.on_executor_shutdown)
        super().shutdown(*args, **kwargs)
