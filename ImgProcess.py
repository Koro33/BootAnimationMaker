# -*- coding: utf-8 -*-
import concurrent.futures
import functools
import os
import platform
import shutil
import subprocess
from typing import Any, Dict, List, Optional, Tuple, Union

from colorama import Fore
import PIL
from PIL import GifImagePlugin, Image, ImageColor, ImageSequence
from tqdm import tqdm


def gif2png(gif_path: str, to_dir_path: str, temp_im_path: str = './temp.gif') -> None:
    """
    Iterate the GIF, extracting each frame.
    :param gif_path: path to gif
    :param to_dir_path: path to extracting directory
    :param temp_im_path: use gifsicle to unoptimize the gif, the path to that temporary file
    :return: None
    """

    cmds = {
        'Linux': f'gifsicle --colors=256 --unoptimize -i "{gif_path}" -o "{temp_im_path}"',
        'Windows': f'.\\bin\\gifsicle\\gifsicle.exe --colors=256 --unoptimize -i "{gif_path}" -o "{temp_im_path}"'
        }
    cmd1 = cmds.get(platform.system(), None)
    if cmd1 is None:
        print('platform not support!')
        exit()
    else:
        subprocess.run(cmd1, shell=True)

    with Image.open(temp_im_path) as im:
        im_iter = ImageSequence.Iterator(im)

        p = im_iter[0].getpalette()  # pylint: disable=maybe-no-member
        last_frame = im_iter[0].convert('RGBA')  # pylint: disable=maybe-no-member

        for index, frame in enumerate(im_iter):
            # print("saving {} frame {}, {} {}".format(to_dir_path, index, frame.size, frame.tile))
            # if not frame.getpalette():
            #     frame.putpalette(p)

            new_frame = Image.new('RGBA', frame.size)

            new_frame.paste(last_frame)
            new_frame.paste(frame, (0, 0), frame.convert('RGBA'))

            result_frame_path = os.path.join(to_dir_path, "{0:0{width}}.png".format(index, width=5))
            new_frame.save(result_frame_path, 'PNG')

            last_frame = new_frame

    os.remove(temp_im_path)


def _png_iter(png_dir_path: str):
    for png_name in sorted(os.listdir(png_dir_path))[1:]:
        png_path = os.path.join(png_dir_path, png_name)
        with Image.open(png_path) as png:
            yield png.convert('RGBA')


def png2gif(png_dir_path: str, to_gif_path: str, duration: int = 30) -> None:
    """

    :param png_dir_path:  path to png directory
    :param to_gif_path: path to gif
    :param duration: interval between the frame
    :return:
    """
    png0_path = os.path.join(png_dir_path, sorted(os.listdir(png_dir_path))[0])
    with Image.open(png0_path) as png0:
        png0.convert('RGBA').save(to_gif_path,
                                  save_all=True,
                                  format='GIF',
                                  append_images=_png_iter(png_dir_path),
                                  loop=0,
                                  duration=duration
                                  )
    cmds = {
            'Linux': f'gifsicle --colors=255 --optimize -i {to_gif_path} -o {to_gif_path}',
            'Windows': f'.\\bin\\gifsicle\\gifsicle.exe --colors=255 --optimize -i {to_gif_path} -o {to_gif_path}'
    }
    cmd1 = cmds.get(platform.system(), None)
    if cmd1 is None:
        print('platform not support!')
        exit()
    else:
        subprocess.run(cmd1, shell=True)


def _get_gif_num(im: Image.Image) -> int:
    """
    get the frame number of Image
    :param im: Image
    :return: frame number
    """
    im_iter = ImageSequence.Iterator(im)
    _num = 0

    for frame in im_iter:
        _num += 1
    return _num


def _get_gif_duration_sum(im: Image.Image) -> int:
    """
    get the gif duration
    :param im: Image
    :return: time(ms)
    """
    im_iter = ImageSequence.Iterator(im)
    _curr_time_temp = 0

    for frame in im_iter:
        _curr_time_temp += frame.info['duration']
    _duration_sum = _curr_time_temp
    return _duration_sum


def _check_equal_interval(im: Image.Image) -> Union[bool, int, float, List]:
    """
    check if the gif frame interval is equal, and return related information
    :param Image.Image im: Image
    :return: is interval, interval, fps, interval list for each frame
    """
    im_iter = ImageSequence.Iterator(im)
    _time_interval = 0
    interval_list = []

    for index, frame in enumerate(im_iter):
        interval_list.append(frame.info['duration'])

    for index, interval in enumerate(interval_list):
        if index == 0:
            _time_interval = interval
        elif _time_interval != interval:
            return [False, -1, -1, interval_list]
        else:
            pass
    try:
        _fps = 1000 / _time_interval
    except ZeroDivisionError:
        _fps = 999999
    return [True, _time_interval, _fps, interval_list]


def gif_info(im_path: str) -> Dict:
    """
    get gif information
    :param im_path: path to image
    :return: gif information
    """
    ginfo = dict()

    with Image.open(im_path) as im:
        ginfo['width'], ginfo['height'] = im.size
        ginfo['equal_interval'], ginfo['interval'], ginfo['fps'], ginfo['interval_list'] = _check_equal_interval(im)
        ginfo['frame_num'] = _get_gif_num(im)
        ginfo['duration'] = _get_gif_duration_sum(im)

    return ginfo


def auto_bg_color(im_path: str):
    # TODO: auto generate background color
    return (0, 0, 0, 255)


class PasteConf():
    """
    paste configuration class
    """
    def __init__(self, im_path: Optional[str], resize_mode: str, target_w: int, target_h: int, c_pos_x: int, c_pos_y: int):
        self.im_path = im_path
        self.resize_mode = resize_mode
        self.target_w = target_w
        self.target_h = target_h
        self.c_pos_x = c_pos_x
        self.c_pos_y = c_pos_y


def _paste(bg: Image, p_conf: PasteConf) -> None:
    """
    according to paste configuration paste image over another
    :param bg: background image
    :param p_conf: paste configuration
    :return: None
    """
    with Image.open(p_conf.im_path) as im:
        im = im.convert('RGBA')
        im_w, im_h = im.size
        if p_conf.target_w <= 0 or p_conf.target_h <= 0:
            print('Target size(w, h) must > 0!')
            exit()
        if p_conf.resize_mode == 'scale':
            # 缩放贴图，以宽 target_w 为准，等比计算高度，可放大缩小
            p_conf.target_h = int(p_conf.target_w / im_w * im_h)
            im = im.resize((p_conf.target_w, p_conf.target_h), Image.LANCZOS)
        elif p_conf.resize_mode == 'trim':
            # 裁剪贴图，默认中心裁剪，只能缩小
            if p_conf.target_w > im_w:
                p_conf.target_w = im_w
            if p_conf.target_h > im_h:
                p_conf.target_h = im_h
            crop1_x = int((im_w - p_conf.target_w) // 2)
            crop1_y = int((im_h - p_conf.target_h) // 2)
            crop2_x = int((im_w + p_conf.target_w) // 2)
            crop2_y = int((im_h + p_conf.target_h) // 2)
            crop_box = (crop1_x, crop1_y, crop2_x, crop2_y)
            im = im.crop(crop_box)

        bg.paste(im, (p_conf.c_pos_x - p_conf.target_w // 2, p_conf.c_pos_y - p_conf.target_h // 2), im)


def combination(im_path: str, bg_conf: Dict, dyn_conf: Dict, sta_confs: List) -> None:
    """
    component combination with one extracting png file
    :param im_path: path to extracting png
    :param bg_conf: background component configuration
    :param dyn_conf: dynamic component configuration
    :param sta_confs: static component configurations list
    :return: None
    """
    bg_size = bg_conf.get('bg_size', None)
    # bg_w, bg_h = bg_size
    try:
        bg_color = PIL.ImageColor.getrgb(bg_conf.get('bg_color', 'auto'))
    except ValueError:
        bg_color = auto_bg_color(dyn_conf.get('ext_dir', None))

    dyn_paste_conf = PasteConf(
        im_path=None,
        resize_mode=dyn_conf.get('resize_mode', None),
        target_w=dyn_conf.get('target_size', None)[0],
        target_h=dyn_conf.get('target_size', None)[1],
        c_pos_x=dyn_conf.get('c_pos', None)[0],
        c_pos_y=dyn_conf.get('c_pos', None)[1]
    )
    dyn_on_top = dyn_conf.get('on_top', False)
    dyn_paste_conf.im_path = im_path

    bg = Image.new('RGBA', bg_size, bg_color)

    if dyn_on_top is True:
        for sta_conf in sta_confs:
            sta_paste_conf = PasteConf(
                im_path=sta_conf.get('im_path', None),
                resize_mode=sta_conf.get('resize_mode', None),
                target_w=sta_conf.get('target_size', None)[0],
                target_h=sta_conf.get('target_size', None)[1],
                c_pos_x=sta_conf.get('c_pos', None)[0],
                c_pos_y=sta_conf.get('c_pos', None)[1]
            )
            _paste(bg, sta_paste_conf)

        _paste(bg, dyn_paste_conf)
    else:
        _paste(bg, dyn_paste_conf)

        for sta_conf in sta_confs:
            sta_paste_conf = PasteConf(
                im_path=sta_conf.get('im_path', None),
                resize_mode=sta_conf.get('resize_mode', None),
                target_w=sta_conf.get('target_size', None)[0],
                target_h=sta_conf.get('target_size', None)[1],
                c_pos_x=sta_conf.get('c_pos', None)[0],
                c_pos_y=sta_conf.get('c_pos', None)[1]
            )
            _paste(bg, sta_paste_conf)

    bg.save(im_path)
    # 不带返回值，返回值与多进程的进度条实现方法冲突 -> list(Image)，会造成内存爆炸


def combination_multi(bg_conf: Dict, dyn_conf: Dict, sta_confs: List) -> None:
    """
    component combination (multiprocess)
    :param bg_conf: background component configuration
    :param dyn_conf: dynamic component configuration
    :param sta_confs: static component configurations list
    :return:
    """
    combination_single = functools.partial(combination, bg_conf=bg_conf, dyn_conf=dyn_conf, sta_confs=sta_confs)
    im_name_list = os.listdir(dyn_conf.get('ext_dir', None))
    im_path_list = []
    for im_name in im_name_list:
        im_path_list.append(os.path.join(dyn_conf.get('ext_dir', None), im_name))
    with concurrent.futures.ProcessPoolExecutor() as executor:
        list(
            tqdm(
                executor.map(combination_single, im_path_list),
                total=len(im_path_list),
                dynamic_ncols=True,
                bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.BLUE, Fore.RESET),
                ascii=True
            )
        )
        # for im_path, combination_task in zip(im_path_list, executor.map(combination_single, im_path_list)):
        #     print(im_path, combination_task)


"""
# example for bg_conf, dyn_conf, sta_confs

bg_conf = {
    'bg_size': (1080, 1920),
    'bg_color': 'rgba(255,0,0,155)',
}
dyn_conf = {
    'gif_path': './123.gif',
    'ext_dir': './',
    'resize_mode': 'scale',
    'target_size': (1080, 123),
    'c_pos': (1080 // 2, 756),
    'o_top': True
}
sta_confs = [
    {
        'im_path': '123.png',
        'resize_mode': 'scale',
        'target_size': (674, 123),
        'c_pos': (1080 // 2, 1456)
    },
    {
        'im_path': '123.png',
        'resize_mode': 'scale',
        'target_size': (674, 123),
        'c_pos': (1080 // 2, 1256)
    }
]
"""


def combination_prev(im_path: str, bg_conf: Dict, dyn_conf: Dict, sta_confs: Dict) -> Image:
    """
    component combination with one extracting png file (for preview)
    :param im_path: path to extracting png
    :param bg_conf: background component configuration
    :param dyn_conf: dynamic component configuration
    :param sta_confs: static component configurations list
    :return: Image, combined image
    """
    bg_size = bg_conf.get('bg_size', None)
    # bg_w, bg_h = bg_size
    try:
        bg_color = PIL.ImageColor.getrgb(bg_conf.get('bg_color', 'auto'))
    except ValueError:
        bg_color = auto_bg_color(dyn_conf.get('ext_dir', None))

    dyn_paste_conf = PasteConf(
        im_path=None,
        resize_mode=dyn_conf.get('resize_mode', None),
        target_w=dyn_conf.get('target_size', None)[0],
        target_h=dyn_conf.get('target_size', None)[1],
        c_pos_x=dyn_conf.get('c_pos', None)[0],
        c_pos_y=dyn_conf.get('c_pos', None)[1]
    )
    dyn_on_top = dyn_conf.get('on_top', False)
    dyn_paste_conf.im_path = im_path

    bg = Image.new('RGBA', bg_size, bg_color)

    if dyn_on_top is True:
        for sta_conf in sta_confs:
            sta_paste_conf = PasteConf(
                im_path=sta_conf.get('im_path', None),
                resize_mode=sta_conf.get('resize_mode', None),
                target_w=sta_conf.get('target_size', None)[0],
                target_h=sta_conf.get('target_size', None)[1],
                c_pos_x=sta_conf.get('c_pos', None)[0],
                c_pos_y=sta_conf.get('c_pos', None)[1]
            )
            _paste(bg, sta_paste_conf)

        _paste(bg, dyn_paste_conf)
    else:
        _paste(bg, dyn_paste_conf)

        for sta_conf in sta_confs:
            sta_paste_conf = PasteConf(
                im_path=sta_conf.get('im_path', None),
                resize_mode=sta_conf.get('resize_mode', None),
                target_w=sta_conf.get('target_size', None)[0],
                target_h=sta_conf.get('target_size', None)[1],
                c_pos_x=sta_conf.get('c_pos', None)[0],
                c_pos_y=sta_conf.get('c_pos', None)[1]
            )
            _paste(bg, sta_paste_conf)

    return bg


def combination_preview(bg_conf: Dict, dyn_conf: Dict, sta_confs: Dict) -> None:
    """
    image preview using matplotlib
    :param bg_conf: background component configuration
    :param dyn_conf: dynamic component configuration
    :param sta_confs: static component configurations list
    :return: None
    """
    import matplotlib.pyplot as plt

    im_name_list = os.listdir(dyn_conf.get('ext_dir', None))
    im_path_list = []
    for im_name in im_name_list:
        im_path_list.append(os.path.join(dyn_conf.get('ext_dir', None), im_name))

    im_path = im_path_list[0]
    bg = combination_prev(im_path, bg_conf, dyn_conf, sta_confs)

    fig, ax = plt.subplots()
    ax.imshow(bg)

    plt.show()


def combination_edit():
    pass


def _compression(png_path: str, q_min: int = 65, q_max: int = 80, speed: int = 3, ext: str = '.png') -> None:
    """
    compress a png file using pngquant
    :param png_path: path to png file
    :param q_min: quality min >0
    :param q_max: quality max <100
    :param speed: speed/quality trade-off. 1=slow, 3=default, 11=fast & rough
    :param ext: custom suffix/extension for output filenames
    :return: None
    """
    cmds = {
        'Linux': f'pngquant --strip --force --skip-if-larger --ext {ext} --speed {speed} --quality={q_min}-{q_max} "{png_path}"',
        'Windows': f'.\\bin\\pngquant\\pngquant.exe --strip --force --skip-if-larger --ext {ext} --speed {speed} --quality={q_min}-{q_max} "{png_path}"'
    }
    cmd1 = cmds.get(platform.system(), None)
    if cmd1 is None:
        print('platform not support!')
        exit()
    else:
        subprocess.run(cmd1, shell=True)


def part_compression_multi(part_dir: str, q_min: int = 70, q_max: int = 80, speed: int = 3, ext: str = '.png') -> None:
    """
    compress png files multiprocess using pngquant
    :param part_dir: path to png file
    :param q_min: quality min >0
    :param q_max: quality max <100
    :param speed: speed/quality trade-off. 1=slow, 3=default, 11=fast & rough
    :param ext: custom suffix/extension for output filenames
    :return:
    """
    _compression_single = functools.partial(_compression, q_min=q_min, q_max=q_max, speed=speed, ext=ext)
    png_name_list = os.listdir(part_dir)
    png_path_list = []
    for png_name in png_name_list:
        if os.path.splitext(png_name)[-1]:
            png_path_list.append(os.path.join(part_dir, png_name))
    with concurrent.futures.ProcessPoolExecutor() as executor:
        list(
            tqdm(
                executor.map(_compression_single, png_path_list),
                total=len(png_path_list),
                dynamic_ncols=True,
                bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.BLUE, Fore.RESET),
                ascii=True
            )
        )


if __name__ == '__main__':
    check_env()
    pass




