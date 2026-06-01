import asyncio
import time

class TokenBucket:
    def __init__(self, rate: float, capacity: float):
        """
        Args:
            rate: Tokens per second.
            capacity: Maximum tokens in the bucket.
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()

    async def acquire(self, tokens: float = 1.0):
        async with self.lock:
            while True:
                now = time.monotonic()
                elapsed = now - self.last_update
                self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
                self.last_update = now

                if self.tokens >= tokens:
                    self.tokens -= tokens
                    return
                
                wait_time = (tokens - self.tokens) / self.rate
                await asyncio.sleep(wait_time)

class AdMobRateLimiter:
    def __init__(self):
        # Default limits - can be tuned based on Google Cloud Console quotas
        self.read_limiter = TokenBucket(rate=5.0, capacity=10.0)  # 5 requests/sec
        self.write_limiter = TokenBucket(rate=1.0, capacity=5.0)   # 1 request/sec
        self.report_limiter = TokenBucket(rate=0.5, capacity=2.0)  # 1 request/2sec

    async def acquire_read(self):
        await self.read_limiter.acquire()

    async def acquire_write(self):
        await self.write_limiter.acquire()

    async def acquire_report(self):
        await self.report_limiter.acquire()
