from typing import AsyncIterator
from typing import List, TypeVar

T = TypeVar("T")


async def sync_list(async_list: AsyncIterator[T]) -> List[T]:
    return [item async for item in async_list]
