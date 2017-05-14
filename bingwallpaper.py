#!/bin/python

import argparse
import os
import requests
import platform
import subprocess

import sys

URL = "https://cn.bing.com"
IMAGE_URL_API = "https://cn.bing.com/HPImageArchive.aspx"


def download_images(image_dir, image_urls):
    for start_date in image_urls:
        print("downloading", image_urls[start_date])
        response = requests.get(image_urls[start_date])
        with open(image_dir + os.sep + start_date + ".jpg", "wb") as code:
            code.write(response.content)


def set_random_wallpaper(image_dir):
    command = "feh --recursive --randomize -F --bg-fill {}".format(image_dir)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    for line in p.stdout.readlines():
        print(line)


def set_wallpaper(image_path):
    system_type = platform.system()
    system_type = system_type.lower()
    if "linux" in system_type:
        command = "feh -F --bg-fill {}".format(image_path)
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print(line)
    elif "windows" in system_type:
        absolute_path = os.path.abspath(image_path)
        import win32api
        import win32con
        import win32gui
        k = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
        win32api.RegSetValueEx(k, "WallpaperStyle", 0, win32con.REG_SZ, "2")  # 2拉伸适应桌面,0桌面居中
        win32api.RegSetValueEx(k, "TileWallpaper", 0, win32con.REG_SZ, "0")
        win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER, absolute_path, win32con.SPIF_SENDWININICHANGE)
    else:
        print("error:unknown system type {}".format(system_type))


def set_today_wallpaper(image_dir):
    payload = {'format': 'js',
               'idx': 0,
               'n': 1}
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


def clean_stored_images(image_dir, count):
    image_files = os.listdir(image_dir)
    if len(image_files) > count:
        for image_file in image_files[0:len(image_files) - count]:
            os.remove(image_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--today',
        type=bool,
        default=False,
        help='Set today wallpaper'
    )
    parser.add_argument(
        '--stored_image_count',
        type=int,
        default=7,
        help='Set today wallpaper'
    )
    image_dir = os.getenv("HOME", default=".")
    image_dir += (os.sep + ".bingwallpapers")
    FLAGS, unparsed = parser.parse_known_args()
    if not os.path.exists(image_dir):
        os.mkdir(image_dir)
    clean_stored_images(image_dir, FLAGS.stored_image_count)
    set_random_wallpaper(image_dir)
    if FLAGS.today:
        set_today_wallpaper(image_dir)


if __name__ == '__main__':
    main()
