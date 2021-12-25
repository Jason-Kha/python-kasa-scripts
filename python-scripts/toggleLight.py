import sys
import asyncio
import argparse
import threading
import time

from kasa import SmartBulb

# parser setup
parser = argparse.ArgumentParser()
parser.add_argument('--ip', type=str, nargs='+', required=True)
args = parser.parse_args()

async def turnOn(bulb):
    await bulb.update()
    await bulb.turn_on()

async def turnOff(bulb):
    await bulb.update()
    await bulb.turn_off()


def between_toggleLights(bulb, is_on):
    loop1 = asyncio.new_event_loop()
    asyncio.set_event_loop(loop1)
    
    # turn off
    if is_on:
        loop1.run_until_complete(turnOff(bulb))
        loop1.close()
    else:
        loop1.run_until_complete(turnOn(bulb))
        loop1.close()


async def main():
    BulbList = []
    lightCount = len(args.ip)
    is_on = False

    # store SmartBulb information
    for i in range(0, lightCount):
        BulbList.append(SmartBulb(args.ip[i]))
        await BulbList[i].update()

        if BulbList[i].is_on:
            is_on = True

    # blink with threads
    threads = list()
    for i in range(0, lightCount):
        x = threading.Thread(target=between_toggleLights, args=(BulbList[i], is_on))
        threads.append(x)
        x.start()

    # join threads
    for i, thread in enumerate(threads):
        thread.join()


if __name__ == "__main__":
    asyncio.run(main())
