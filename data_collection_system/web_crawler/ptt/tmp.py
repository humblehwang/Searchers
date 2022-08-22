import aiohttp
import asyncio
from concurrent.futures import CancelledError

data = []
T = 9
def cancel_tasks():
    for task in asyncio.all_tasks():
        task.cancel()  

async def do_requests(i):
    if i == T:
        cancel_tasks()
        return
    data.append(i)  

async def caller(): 
    tasks = [asyncio.create_task(do_requests(i)) for i in range(10000)] 
    try:
        await asyncio.gather(*tasks)  # 打包任務清單及執行
    except asyncio.exceptions.CancelledError as error:
        print("All tasks have been canceled")

if __name__ == '__main__':
    asyncio.run(caller())
    print(data)
    #loop.run_until_complete(caller())  
   