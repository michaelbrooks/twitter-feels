import time
import Queue

class TweetQueue(Queue.Queue):
    """
    Simply extends the Queue class with get_all methods.
    """

    def get_all(self, block=True, timeout=None):
        """Remove and return all the items from the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until an item is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Empty exception if no item was available within that time.
        Otherwise ('block' is false), return an item if one is immediately
        available, else raise the Empty exception ('timeout' is ignored
        in that case).
        """
        self.not_empty.acquire()
        try:
            if not block:
                if not self._qsize():
                    raise Queue.Empty
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time() + timeout
                while not self._qsize():
                    remaining = endtime - time()
                    if remaining <= 0.0:
                        raise Queue.Empty
                    self.not_empty.wait(remaining)
            items = self._get_all()
            self.not_full.notify()
            return items
        finally:
            self.not_empty.release()

    def get_all_nowait(self):
        """Remove and return all the items from the queue without blocking.

        Only get items if immediately available. Otherwise
        raise the Empty exception.
        """
        return self.get_all(False)

    def _get_all(self):
        """
        Get all the items from the queue.
        """
        result = []
        while len(self.queue):
            result.append(self.queue.popleft())
        return result
