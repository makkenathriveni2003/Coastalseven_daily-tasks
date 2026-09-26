import asyncio


async def task1():
    await asyncio.sleep(2)
    return "Task 1 completed"


async def task2():
    await asyncio.sleep(2)
    return "Task 2 completed"


async def run_parallel_tasks():
    results = await asyncio.gather(
        task1(),
        task2()
    )

    return results


async def async_operation():
    await asyncio.sleep(2)
    return "Async operation completed"