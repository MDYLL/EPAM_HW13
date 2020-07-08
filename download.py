import argparse
import os
import threading
import time
from io import BytesIO
from multiprocessing.pool import ThreadPool
from pathlib import Path

import requests
from PIL import Image


def check_args(args):
    if not os.path.exists(args.filename):
        raise FileNotFoundError(f"File {args.filename} doesn't exist")
    Path(args.dir).mkdir(parents=True, exist_ok=True)
    if int(args.threads) < 1:
        raise ValueError("Number of threads should be integer 1 or more")
    try:
        h, w = args.size.split('x')
        h, w = int(h), int(w)
    except ValueError as e:
        print("Incorrect size format")
        raise e
    h, w = int(h), int(w)
    if h < 1 or w < 1:
        raise ValueError("height and weight should be integer 1 or more")
    return None


class PreviewImage:
    file_with_error = 0
    file_success = 0
    dir = ""
    size = 0
    byte_size = 0
    __slots__ = ("url", "idx")

    def __init__(self, url, idx):
        self.url = url
        self.idx = idx

    def create_preview(self):
        try:
            response = requests.get(self.url)
            img = Image.open(BytesIO(response.content))
            self.byte_size += len(response.content)
            img = img.resize(self.size)
            img_name = str(self.idx).zfill(5) + '.jpg'
            img.save(os.path.join(self.dir, img_name), format='JPEG')
            print(f"URL {self.url} was processed. File: {str(self.idx).zfill(5) + '.jpg'}")
        except Exception as e:
            print(f"URL {self.url} was not processed. {e}")
            lock.acquire()
            self.__class__.file_with_error += 1
            lock.release()
        else:
            lock.acquire()
            self.__class__.file_success += 1
            lock.release()


start_time = time.time()
parser = argparse.ArgumentParser(description='parsing and processing images')
parser.add_argument('filename', help='file with list of urls')
parser.add_argument('--dir', '-d', default=os.getcwd(), help='folder for images')
parser.add_argument('--threads', '-t', default=1, help='quantity of threads')
parser.add_argument('--size', '-s', default='100x100', help='size of saved images, example: 100x100')

args = parser.parse_args()
check_args(args)
h, w = [int(el) for el in args.size.split('x')]
PreviewImage.size = h, w
PreviewImage.dir = args.dir
image_queue = []
with open(args.filename) as file:
    for idx, line in enumerate(file):
        image_queue.append(PreviewImage(line.rstrip('\n'), idx))


def ret(q):
    for task in q:
        yield task


lock = threading.Lock()
pool = ThreadPool(int(args.threads))
pool.map(PreviewImage.create_preview, ret(image_queue))

pool.close()
pool.join()

print("Program finished")
print(f"Successed URL - {PreviewImage.file_success}")
print(f"URL with error - {PreviewImage.file_with_error}")
print(f"{PreviewImage.byte_size} bytes downloaded")

print(f"Time of execution: {time.time() - start_time:0.1f} seconds")
