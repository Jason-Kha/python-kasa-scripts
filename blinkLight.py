import sys
import asyncio
import argparse
import threading
import time

from kasa import SmartBulb


def check_hue(value):
    ivalue = int(value)
    if ivalue < 0 or ivalue > 360:
        raise argparse.ArgumentTypeError("%s is an invalid int value" % value)
    return ivalue


def check_satval(value):
    ivalue = int(value)
    if ivalue < 0 or ivalue > 100:
        raise argparse.ArgumentTypeError("%s is an invalid int value" % value)
    return ivalue


# parser setup
parser = argparse.ArgumentParser()
parser.add_argument('--h', type=check_hue, nargs=1, required=True)
parser.add_argument('--s', type=check_satval, nargs=1, required=True)
parser.add_argument('--v', type=check_satval, nargs=1, required=True)
parser.add_argument('--ip', type=str, nargs='+', required=True)
args = parser.parse_args()


async def getHSV(ip):
    light = SmartBulb(ip)
    await light.update()
    return light.hsv


async def setHSV(bulb, h, s, v):
    await bulb.update()
    await bulb.set_hsv(h, s, v, transition=250)


def between_setHSV(bulb, h1, s1, v1, h2, s2, v2):
    loop1 = asyncio.new_event_loop()
    asyncio.set_event_loop(loop1)

    # set to new color
    loop1.run_until_complete(setHSV(bulb, h1, s1, v1))
    loop1.close()

    time.sleep(.55)

    # change back to old color
    loop2 = asyncio.new_event_loop()
    asyncio.set_event_loop(loop2)

    loop2.run_until_complete(setHSV(bulb, h2, s2, v2))
    loop2.close()


async def main():
    BulbList = []
    HSVList = []
    lightCount = len(args.ip)

    # store SmartBulb information
    for i in range(0, lightCount):
        BulbList.append(SmartBulb(args.ip[i]))
        HSVList.append(await getHSV(args.ip[i]))

    '''
    # store list of original hsv's here
    for h, s, v in HSVList:
        print(h, s, v)
    '''

    # blink with threads
    threads = list()
    for i in range(0, lightCount):
        x = threading.Thread(target=between_setHSV, args=(BulbList[i], args.h[0], args.s[0], args.v[0], *HSVList[i]))
        threads.append(x)
        x.start()

    # join threads
    for i, thread in enumerate(threads):
        thread.join()


if __name__ == "__main__":
    asyncio.run(main())
