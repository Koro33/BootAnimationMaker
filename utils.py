import functools
import os
import zipfile
from time import sleep, time

import requests
from colorama import Fore
from tqdm import tqdm


def time_it(func):
    """
    using decorator method to determine function run time, adding '@time_it' before the function
    :param func: Measured function
    :return: None
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tic = time()
        result = func(*args, **kwargs)
        toc = time()
        t = toc - tic
        if t >= 1:
            print("Run '{0}' for {1} s".format(func.__name__, t))
        elif (t < 1) and (t >= 0.001):
            print("Run '{0}' for {1} ms".format(func.__name__, t * 1000))
        elif t < 0.001:
            print("Run '{0}' for {1} ns".format(func.__name__, t * 1000 * 1000))
        return result
    return wrapper


def download_file(url: str, name=None) -> bool:
    """
    download file with url
    :param url: url for downloaded file
    :param name: custom name for downloaded file
    :return: bool, if success
    """
    block_size = 1024
    wrote = 0

    res = requests.get(url=url, stream=True, timeout=12)
    if res.status_code != 200:
        print('Error in URL!')
        return False
    total_size = int(res.headers.get('content-length', 0)) / block_size  # 确定整个安装包的大小
    with open(name, "wb+") as f:
        print("安装包整个大小是：{} KB，开始下载...".format(total_size))
        for data in tqdm(iterable=res.iter_content(block_size),
                         total=total_size,
                         unit='KB',
                         desc=name,
                         bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.BLUE, Fore.RESET)
                         ):
            # 调用iter_content，一块一块的遍历要下载的内容，搭配 stream=True，此时才开始真正的下载
            # iterable：可迭代的进度条 total：总的迭代次数 desc：进度条的前缀
            wrote += len(data)
            f.write(data)
    # if total_size != 0 and wrote != total_size:
    #     print("ERROR, something went wrong")
    sleep(0.5)
    print("{} 已经下载完毕！".format(name))
    sleep(0.5)
    return True


def dir2zipfile(zipped_dir_path: str, creat_zip_file_path: str, incl_rootdir=False, incl_emptydir=False) -> bool:
    """
    zip directory to given path (STORED)
    :param zipped_dir_path: path the zipped directory
    :param creat_zip_file_path: path to zip file
    :param incl_rootdir: if include the root directory ({zipped_dir_path})
    :param incl_emptydir: if include the empty directory
    :return: bool, if success
    """
    with zipfile.ZipFile(creat_zip_file_path, 'w', zipfile.ZIP_STORED) as z:
        empty_dirs = []
        for rootdir, dirs, files in os.walk(zipped_dir_path):
            if incl_rootdir:
                inzip_root_path = rootdir.replace(os.path.dirname(zipped_dir_path), '')
            else:
                inzip_root_path = rootdir.replace(zipped_dir_path, '')

            for file in files:
                z.write(os.path.join(rootdir, file), os.path.join(inzip_root_path, file))

            if incl_emptydir:
                empty_dirs.extend([dir for dir in dirs if os.listdir(os.path.join(rootdir, dir)) == []])
                for dir in empty_dirs:
                    zif = zipfile.ZipInfo(os.path.join(inzip_root_path, dir) + "/")
                    z.writestr(zif, "")
                empty_dirs = []
    return True


def unzipfile(zip_file_path: str, unzipped_dir_path: str) -> bool:
    """
    unzip file
    :param zip_file_path: path to zipfile
    :param unzipped_dir_path: directory path to unzip
    :return: bool, if success
    """
    z = zipfile.ZipFile(zip_file_path, 'r')
    # for file in z.namelist():
    #     z.extract(file, path)
    z.extractall(path=unzipped_dir_path)
    return True

