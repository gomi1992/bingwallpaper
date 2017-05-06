#!/bin/python

import argparse
import os
import requests
import subprocess

URL = "https://cn.bing.com"
IMAGE_URL_API = "https://cn.bing.com/HPImageArchive.aspx"


def download_images(image_dir, image_urls):
    for startdate in image_urls:
        print("downloading", image_urls[startdate])
        response = requests.get(image_urls[startdate])
        with open(image_dir + os.sep + startdate + ".jpg", "wb") as code:
            code.write(response.content)


def set_random_wallpaper(image_dir):
    command = "feh --recursive --randomize -F --bg-fill {}".format(image_dir)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print(line)


def set_wallpaper(image):
    command = "feh -F --bg-fill {}".format(image)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print(line)


def set_today_wallpaper(image_dir):
    payload = {'format': 'js',
               'idx': 0,
               'n': 1, }
    response = requests.get(IMAGE_URL_API, params=payload)
    if response.status_code != 200:
        print("network error,set random existed wallpaper")
        set_random_wallpaper(image_dir)
        return
    images = response.json()
    image_url = URL + images["images"][0]["url"]
    image_startdate = images["images"][0]["startdate"]
    image = image_dir + os.sep + image_startdate + ".jpg"
    if os.path.exists(image):
        set_wallpaper(image)
        return
    tmp = {}
    tmp[image_startdate] = image_url
    download_images(image_dir, tmp)
    if not os.path.exists(image):
        set_random_wallpaper(image_dir)
        return
    set_wallpaper(image)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--today',
        type=bool,
        default=False,
        help='Set today wallpaper'
    )
    image_dir = os.getenv("HOME")
    image_dir += (os.sep + ".bingwallpapers")
    FLAGS, unparsed = parser.parse_known_args()
    if not os.path.exists(image_dir):
        os.mkdir(image_dir)
    set_random_wallpaper(image_dir)
    if FLAGS.today:
        set_today_wallpaper(image_dir)


if __name__ == '__main__':
    main()
