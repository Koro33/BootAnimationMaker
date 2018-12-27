"""
Run this script to make boot animation
"""
import os
import shutil

import click
import yaml

from ConfigCheck import quit_, yes_or_no
from ImgProcess import (check_env, combination_multi, combination_preview, gif2png, gif_info, part_compression_multi,
                        png2gif)
from PackageMake import (bootani_zip_file_creat, clean, desc_file_creat, module_config_modify, module_pack,
                         module_prop_modify, template_prepare)
from typing import Any, Dict, List, Optional, Tuple, Union


@click.command()
@click.option('--config', default='./config.yml', type=str, help='Config file path')
def main(config):
    # ******************************************************************************************************
    # 欢迎
    print('×××××××××××××××××××××××××××××××××××××××')
    print('××× 这是一个 Android 系统开机动画制作工具 ×××')
    print('×××××××××××××××××××××××××××××××××××××××')
    print('')
    print('[START]')

    # ******************************************************************************************************
    # 加载配置文件
    config_file_path = config
    all_config = dict()
    try:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            all_config = yaml.load(f)
        # print(all_config)
    except FileNotFoundError:
        print('[ERROR] 未找到 <config.yml> 配置文件！')
        print('[Info] 请将 <config.yml> 配置文件放入脚本根目录，或使用 "--config" 指定配置文件位置')
        exit()
    print('[Info] 加载配置文件 <config.yml> 成功')

    # ******************************************************************************************************
    # 检查系统环境和软件包
    is_pass = check_env()
    if is_pass is False:
        exit()

    # ******************************************************************************************************
    export_dir_path = os.path.join(os.path.dirname(__file__), 'export')
    module_export_filename: str = all_config.get('module_export_filename')
    export_temp_dir_path = os.path.join(export_dir_path, 'Temp')
    export_bootani_dir_path = os.path.join(export_temp_dir_path, 'bootanimation')

    desc_file_path = os.path.join(export_bootani_dir_path, 'desc.txt')

    zipped_dir_path = export_bootani_dir_path
    bootani_zip_path = os.path.join(export_temp_dir_path, 'bootanimation.zip')

    template_file_name = 'magisk-module-template-17000.zip'
    template_download_url = 'https://github.com/topjohnwu/magisk-module-template/archive/17000.zip'
    template_dir_path = os.path.join(export_temp_dir_path, 'magisk-module-template-17000')
    module_prop_file_path = os.path.join(template_dir_path, 'module.prop')
    module_config_file_path = os.path.join(template_dir_path, 'config.sh')
    module_media_dir_path = os.path.join(template_dir_path, 'system', 'media')
    module_placeholder_file_path = os.path.join(template_dir_path, 'system', 'placeholder')
    module_export_file_path = os.path.join(export_dir_path, module_export_filename)

    # *******************************************************************************************************
    # 检查配置文件合法性
    # 输出文件路径
    if os.path.isfile(export_dir_path):
        print(f'[ERROR] {export_dir_path} 是文件！请检查 >>> Exit...')
        exit()
    if not os.path.exists(export_dir_path):
        print(f'[WARNING] 路径 <{export_dir_path}> 不存在！')
        while True:
            ipt = input(f'[INPUT] 是否要新建路径 <{export_dir_path}> ? (*Yes*/No)')
            choose = yes_or_no(ipt, default=True)
            if choose is True:
                os.mkdir(export_dir_path)
                break
            elif choose is False:
                print(f'[ERROR] 无 <{export_dir_path}> 路径，请手动检查 >>> Exit...')
                exit()
                break
            else:
                continue
    # 图元路径及 FPS
    print('[Info] 正在检查图元配置...')
    real_fps_list = []
    all_config['fps'] = int(all_config.get('fps'))
    assigned_fps = all_config.get('fps')

    for idx, anime_part in enumerate(all_config['anime']):
        gif_path = anime_part.get('gif_path')
        if os.path.exists(gif_path) and os.path.isfile(gif_path):
            print(f'  * <{gif_path}> 路径有效.')
        else:
            print(f'[ERROR] <{gif_path}> 路径无效 >>> Exit...')
            exit()
        info = gif_info(gif_path)
        if info['equal_interval'] is False:
            print(f'[ERROR] gif 文件 <{gif_path}> 含有不等间隔帧，当前版本脚本不支持，请更换 gif >>> Exit...')
            print(f'[INFO] Gif Info for {gif_path}')
            print(info)
            exit()
        real_fps_list.append(info.get('fps'))
        for png_cpnt in anime_part.get('cpnt_conf').get('sta_cpnt'):
            png_path = png_cpnt.get('im_path')
            if os.path.exists(png_path) and os.path.isfile(png_path):
                print(f'  * <{png_path}> 路径有效.')
            else:
                print(f'[ERROR] <{png_path}> 路径无效 >>> Exit...')
                exit()

    # 进一步检查并调整fps
    if all_config.get('check_gif', True) is True:
        print('[Info] 正在检查FPS...')
        print(f' - 配置指定 <{assigned_fps}>')
        print(f' - 实际')
        for idx, fps in enumerate(real_fps_list):
            print(f'   * <part{idx}>  -  <{fps}>')

        if len(set(real_fps_list)) == 1:
            if assigned_fps != real_fps_list[0]:
                print(f'[WARNING] 配置文件指定的 fps 与实际不同')
                while True:
                    ipt = input(f'[INPUT] 是否要使用 gif 实际 fps [{real_fps_list[0]}] ? (*Yes*/No)')
                    choose = yes_or_no(ipt, default=True)
                    if choose is True:
                        all_config['fps'] = int(real_fps_list[0])
                        print(f"[Info] FPS 改变 [{assigned_fps}] -> [{all_config['fps']}]")
                        break
                    elif choose is False:
                        print(f'[Info] FPS 未改变')
                        break
                    else:
                        print('输入无效，请重试！')
                        continue
            else:
                print('[Info] FPS 检查通过.')
        else:
            print('[WARNING] 不同 part 的实际 fps 不同！')
            if max(real_fps_list) - min(real_fps_list) <= 5:
                while True:
                    ipt = input(f'[INPUT] part 间 FPS 相差不大，是否采用平均值代替指定值? (*Yes*/No)')
                    choose = yes_or_no(ipt, default=True)
                    if choose is True:
                        all_config['fps'] = int((max(real_fps_list) + min(real_fps_list)) / 2)
                        print(f"[Info] FPS 改变 [{assigned_fps}] -> [{all_config['fps']}]")
                        break
                    elif choose is False:
                        print(f'[Info] FPS 未改变 {assigned_fps}')
                        break
                    else:
                        print('输入无效，请重试！')
                        continue
            else:
                print('[ERROR] part 间 FPS 相差过大，不建议继续生成，请调整gif文件后再试! >>> Exit...')
                print('[INFO]')
                print(f'Fps List {real_fps_list}')
                exit()
    else:
        print(f'[WARNING] 不检查 FPS，使用指定 FPS <{assigned_fps}>，可能会导致生成动画不正常')

    # *******************************************************************************************************
    # 初始化临时环境
    if os.path.exists(export_temp_dir_path):
        try:
            shutil.rmtree(export_temp_dir_path)
        except Exception as e:
            print(e)
    os.makedirs(export_temp_dir_path)
    os.makedirs(export_bootani_dir_path)
    print('')
    # ********************************************************************************************************
    # 退出 FOR DEBUG
    # exit()

    # ********************************************************************************************************
    # 处理图片

    for idx, anime_part in enumerate(all_config['anime']):
        print(f'××××××××××××××××part{idx}××××××××××××××××')
        # 生成 bg_conf dyn_conf sta_confs
        bg_conf = {
            'bg_size': all_config.get('device_size'),
            'bg_color': anime_part.get('cpnt_conf').get('bg_cpnt').get('bg_color'),
        }
        dyn_conf = {
            'gif_path': anime_part.get('gif_path'),
            'ext_dir': os.path.join(export_bootani_dir_path, f'part{idx}'),
            'resize_mode': anime_part.get('cpnt_conf').get('dyn_cpnt').get('resize_mode'),
            'target_size': anime_part.get('cpnt_conf').get('dyn_cpnt').get('target_size'),
            'c_pos': anime_part.get('cpnt_conf').get('dyn_cpnt').get('c_pos'),
            'on_top': anime_part.get('cpnt_conf').get('dyn_cpnt').get('on_top')
        }
        sta_confs = anime_part.get('cpnt_conf').get('sta_cpnt')

        # 建立中间文件夹
        os.makedirs(dyn_conf.get('ext_dir'))
        # 离散 gif
        print(f'[INFO] 正在离散 gif...')
        gif2png(
            gif_path=dyn_conf.get('gif_path'),
            to_dir_path=dyn_conf.get('ext_dir'),
            temp_im_path=os.path.join(dyn_conf.get('ext_dir'), 'temp.gif')
        )
        while True:
            ipt = input(f'[INPUT] 是否对 <part{idx}> 组合后的图片进行预览? (Yes/*No*)')
            choose = yes_or_no(ipt, default=False)
            if choose is True:
                print(f'[INFO] 正在预览...')
                combination_preview(
                    bg_conf=bg_conf,
                    dyn_conf=dyn_conf,
                    sta_confs=sta_confs
                )
                print(f'[INFO] 预览完毕！')
                while True:
                    ipt = input(f'[INPUT] 是否继续生成? (*Yes*/No)')
                    choose = yes_or_no(ipt, default=True)
                    if choose is True:
                        break
                    elif choose is False:
                        print(f'[ERROR] 不继续生成 >>> Exit...')
                        exit()
                        break
                    else:
                        print('输入无效，请重试！')
                        continue
                break
            elif choose is False:
                break
            else:
                print('输入无效，请重试！')
                continue

        # 多进程组合部件
        print(f'[INFO] 正在组合图片...')
        combination_multi(
            bg_conf=bg_conf,
            dyn_conf=dyn_conf,
            sta_confs=sta_confs
        )
        # 压缩 png
        print(f'[INFO] 正在压缩 png 文件...')
        part_compression_multi(
            part_dir=dyn_conf.get('ext_dir')
        )
        # 生成预览 gif
        print(f'[INFO] 生成预览gif...')
        preview_gif_name = f'{module_export_filename}_p{idx}_preview.gif'
        png2gif(
            png_dir_path=dyn_conf.get('ext_dir'),
            to_gif_path=os.path.join(export_dir_path, preview_gif_name),
            duration=int(1000 / all_config['fps'])
        )
        print(f'×××××××××××××××××××××××××××××××××××××')
        print('')
    # ********************************************************************************************************
    # 制作 bootanimation.zip
    # 生成 desc_conf
    print(f'[INFO] 正在生成 desc.txt...')
    desc_conf = {
        'width': all_config.get('device_size')[0],
        'height': all_config.get('device_size')[1],
        'fps': all_config.get('fps'),
        'parts': []
    }
    for idx, anime_part in enumerate(all_config['anime']):
        part = anime_part.get('desc_conf')
        part['path'] = f'part{idx}'
        desc_conf.get('parts').append(part)

    # 建立 desc.txt
    desc_file_creat(
        desc_path=desc_file_path,
        desc_conf=desc_conf
    )
    # 压缩为 bootanimation.zip
    print(f'[INFO] 正在压缩为 bootanimation.zip...')
    bootani_zip_file_creat(
        zipped_dir_path=zipped_dir_path,
        bootani_zip_path=bootani_zip_path
    )

    # ********************************************************************************************************
    # 模块打包
    # 生成 module_prop_conf module_config_conf
    module_prop_conf: Dict = all_config.get('module_prop_conf')
    module_config_conf: Dict = all_config.get('module_config_conf', None)

    # 准备 Magisk 模板文件
    print('[INFO] 正在打包...')
    template_prepare(
        template_dir_path=export_dir_path,
        template_file_name=template_file_name,
        download_url=template_download_url,
        unzip_dir_path=export_temp_dir_path
    )
    # 修改 module.prop 文件
    module_prop_modify(
        module_prop_file_path=module_prop_file_path,
        module_prop_conf=module_prop_conf
    )
    # 修改 config.sh 文件
    module_config_modify(
        module_config_file_path=module_config_file_path,
        module_config_conf=module_config_conf
    )
    # 打包
    module_pack(
        bootani_zip_path=bootani_zip_path,
        module_media_dir_path=module_media_dir_path,
        placeholder_path=module_placeholder_file_path,
        template_dir_path=template_dir_path,
        module_export_file_path=module_export_file_path
    )

    # ********************************************************************************************************
    # 清理
    while True:
        ipt = input(f'[INPUT] 是否清理临时文件? (*Yes*/No)')
        choose = yes_or_no(ipt, default=True)
        if choose is True:
            clean(export_temp_dir_path)
            break
        elif choose is False:
            break
        else:
            continue

    print(f'')
    print(f'[INFO] 全部生成已完毕')
    print(f'       请前往 {os.path.abspath(export_dir_path)} 寻找模块文件 <{module_export_filename}> 及其预览 gif 文件.')
    print(f'[END]')


if __name__ == '__main__':
    main()

"""
# File struct
./export
    |- MagiskModule.zip
    |- {name}_p{0,1,2...}_preview.gif
    |- Temp(delete after)
         |- magisk-module-template-17000 (exact)
             |- system
             |- common
             |- META-INF
             |- config.sh
             |- module.prop
             |- README.md
             |- ...
         |- bootanimation
             |- part0
                 |- 00000.png
                 |- 00001.png
                 |- ...
             |- part1
                 |- ...
             |- desc.txt
         |- bootanimation.zip (*pack, delete after)
"""



