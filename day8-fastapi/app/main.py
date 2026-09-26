from fastapi import FastAPI
import asyncio

app = FastAPI(title="Day 8 Async API")


# 1. Basic Async API
@app.get("/async-test")
async def async_test():
    await asyncio.sleep(2)

    return {
        "message": "Async operation completed"
    }


# 2. Parallel execution using asyncio.gather()
@app.get("/parallel")
async def parallel_tasks():

    async def task1():
        await asyncio.sleep(2)
        return "Task 1 completed"

    async def task2():
        await asyncio.sleep(2)
        return "Task 2 completed"

    results = await asyncio.gather(
        task1(),
        task2()
    )

    return {
        "results": results
    }


# 3. Cache demo
cache = {}


@app.get("/cache/{name}")
async def cache_data(name: str):

    if name in cache:
        return {
            "source": "cache",
            "data": cache[name]
        }

    await asyncio.sleep(2)

    data = f"Hello {name}"

    cache[name] = data

    return {
        "source": "database",
        "data": data
    }


# 4. Background task demo
@app.post("/background/{name}")
async def background_task(name: str):

    async def do_work():
        await asyncio.sleep(3)
        print(f"Background task completed for {name}")

    asyncio.create_task(do_work())

    return {
        "message": "Background task started",
        "name": name
    }


# 5. Root
@app.get("/")
def root():
    return {
        "message": "Day 8 Async API is running"
    }