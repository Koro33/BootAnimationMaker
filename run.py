"""
Run this script to make boot animation
"""
import os
import shutil
import json
import platform

import click
import yaml
import PrintTags as pt

from utils import quit_, bool_input_select, num_input_select
from ImgProcess import (combination_multi, combination_preview, gif2png, gif_info, part_compression_multi, png2gif)
from PackageMake import (bootani_zip_file_creat, clean, desc_file_creat, update_binary_modify, module_config_modify, module_pack,
                         module_prop_modify, template_prepare)
from typing import Any, Dict, List, Optional, Tuple, Union


def check_env(show_text) -> bool:
    """
    check the system environment, Availability of tools such as 'gifsicle', 'pngquant'
    :return: bool
    """
    e = platform.uname()

    if e.system == 'Linux':
        cmds = ['gifsicle', 'pngquant']
        for cmd in cmds:
            if shutil.which(cmd) is None:
                pt.error(show_text.get("CHECK_ENV_NOT_INSTALLED").format(cmd=cmd))
                return False

    elif e.system == 'Windows':
        cmds = ['.\\bin\\gifsicle\\gifsicle.exe', '.\\bin\\pngquant\\pngquant.exe']
        for cmd in cmds:
            if shutil.which(cmd) is None:
                pt.error(show_text.get("CHECK_ENV_NOT_EXIST").format(cmd=cmd))
                return False
    else:
        sys = e.system
        pt.error(show_text.get("CHECK_ENV_PLATFORM_NOT_SUPPORTED").format(sys=sys))
        return False

    return True


@click.command()
@click.option('--config', default='./config.yml', type=str, help='Config file path')
def main(config):
    # ****************************************************************************************************
    # load language
    i18n_info = json.load(open("./i18n/i18n.json", 'r', encoding='utf-8'))

    default_lang_key = json.load(open("./i18n/default.json", 'r', encoding='utf-8')).get("default")

    lang_info = i18n_info.get(default_lang_key)
    if lang_info is None:
        pt.warn("Can't find <{key}> in './i18n/i18n.json', please check!".format(key=default_lang_key))
        pt.notice("Use <English> as default")
        lang_info = i18n_info.get("en")

    default_lang_name = lang_info.get("name")
    default_lang_path = lang_info.get("path")
    show_text = json.load(open(default_lang_path, 'r', encoding='utf-8'))

    pt.info(show_text.get("DEFAULT_LANG").format(lang=default_lang_name))
    pt.info(show_text.get("DEFAULT_LANG_CHANGE"))

    # ******************************************************************************************************
    # Welcome
    print("")
    pt.blue('×××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××')
    pt.blue(show_text.get("WELCOME"))
    pt.blue('×××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××××')
    print("")

    # ******************************************************************************************************
    # Loading Config
    config_file_path = config
    all_config = dict()
    try:
        with open(config_file_path, 'r', encoding='utf-8') as f:
            all_config = yaml.load(f)

    except FileNotFoundError:
        pt.error(show_text.get('CONFIG_NOT_FOUND'))
        pt.error(show_text.get('CONFIG_NOT_FOUND_HELP'))
        exit()
    pt.info(show_text.get('CONFIG_LOAD_SUCCESS'))

    # ******************************************************************************************************
    # Check system environment
    if check_env(show_text) is False:
        exit()

    # ******************************************************************************************************
    export_dir_path = os.path.join(os.path.dirname(__file__), 'export')
    module_export_filename = all_config.get('module_export_filename')
    export_temp_dir_path = os.path.join(export_dir_path, 'Temp')
    export_bootani_dir_path = os.path.join(export_temp_dir_path, 'bootanimation')

    desc_file_path = os.path.join(export_bootani_dir_path, 'desc.txt')

    zipped_dir_path = export_bootani_dir_path
    bootani_zip_path = os.path.join(export_temp_dir_path, 'bootanimation.zip')

    template_file_name = 'magisk-module-installer-master.zip'
    template_download_url = 'https://github.com/topjohnwu/magisk-module-installer/archive/master.zip'
    template_dir_path = os.path.join(export_temp_dir_path, 'magisk-module-installer-master')
    module_installer_sh_url = "https://raw.githubusercontent.com/topjohnwu/Magisk/master/scripts/module_installer.sh"
    update_binary_file_path = os.path.join(template_dir_path, 'META-INF', 'com', 'google', 'android', 'update-binary')
    module_prop_file_path = os.path.join(template_dir_path, 'module.prop')
    module_install_file_path = os.path.join(template_dir_path, 'install.sh')
    module_media_dir_path = os.path.join(template_dir_path, 'system', 'media')
    module_placeholder_file_path = os.path.join(template_dir_path, 'system', 'placeholder')
    module_export_file_path = os.path.join(export_dir_path, module_export_filename)

    # *******************************************************************************************************
    # Check config
    # - export path
    pt.info(show_text.get("EXPORT_PATH_CHECK"))
    if os.path.isfile(export_dir_path):
        pt.error(show_text.get("EXPORT_PATH_IS_FILE").format(export_dir_path=export_dir_path))
        exit()
    if not os.path.exists(export_dir_path):
        pt.warn(show_text.get("EXPORT_PATH_NOT_EXIST").format(export_dir_path=export_dir_path))
        pt.notice(show_text.get("EXPORT_PATH_NEW").format(export_dir_path=export_dir_path))

        os.mkdir(export_dir_path)

    # picture element
    pt.info(show_text.get("PIC_ELEMENT_CHECK"))
    real_fps_list = []
    all_config['fps'] = int(all_config.get('fps'))
    assigned_fps = all_config.get('fps')

    for idx, anime_part in enumerate(all_config['anime']):
        gif_path = anime_part.get('gif_path')
        if os.path.exists(gif_path) and os.path.isfile(gif_path):
            print(show_text.get("PIC_ELEMENT_PATH_VALID").format(path=gif_path))
        else:
            pt.error(show_text.get("PIC_ELEMENT_PATH_INVALID").format(path=gif_path))
            exit()
        info = gif_info(gif_path)
        if info['equal_interval'] is False:
            pt.error(show_text.get("PIC_ELEMENT_GIF_UNEQUAL_INTERVALS").format(gif_path=gif_path))
            pt.notice(show_text.get("PIC_ELEMENT_GIF_INFO").format(gif_path=gif_path))
            print(info)
            exit()
        real_fps_list.append(info.get('fps'))
        for png_cpnt in anime_part.get('cpnt_conf').get('sta_cpnt'):
            png_path = png_cpnt.get('im_path')
            if os.path.exists(png_path) and os.path.isfile(png_path):
                print(show_text.get("PIC_ELEMENT_PATH_VALID").format(path=png_path))
            else:
                pt.error(show_text.get("PIC_ELEMENT_PATH_INVALID").format(path=png_path))
                exit()

    # gif fps
    if all_config.get('check_gif', True) is True:
        pt.info(show_text.get("FPS_CHECK"))
        print(show_text.get("FPS_ASSIGNED").format(assigned_fps=assigned_fps))
        print(show_text.get("FPS_REAL"))
        for idx, fps in enumerate(real_fps_list):
            print(show_text.get("FPS_REAL_LIST").format(idx=idx, fps=fps))

        if len(set(real_fps_list)) == 1:
            if assigned_fps != real_fps_list[0]:
                pt.warn(show_text.get("FPS_ASSIGNED_REAL_DIFF"))
                while True:
                    ipt = input(show_text.get("FPS_USE_REAL").format(real_fps=real_fps_list[0]))
                    choose = bool_input_select(ipt, default=True)
                    if choose is True:
                        all_config['fps'] = int(real_fps_list[0])
                        pt.info(show_text.get("FPS_CHANGE").format(fps_before=assigned_fps, fps_after=all_config['fps']))
                        break
                    elif choose is False:
                        pt.info(show_text.get("FPS_UNCHANGED"))
                        break
                    else:
                        pt.warn(show_text.get("INPUT_INVALID"))
                        continue
            else:
                pt.info(show_text.get("FPS_CHECK_PASS"))
        else:
            pt.warn(show_text.get("FPS_MULTIPART_DIFF"))
            if max(real_fps_list) - min(real_fps_list) <= 5:
                while True:
                    ipt = input(show_text.get("FPS_MULTIPART_SMALL_DIFF"))
                    choose = bool_input_select(ipt, default=True)
                    if choose is True:
                        all_config['fps'] = int((max(real_fps_list) + min(real_fps_list)) / 2)
                        pt.info(show_text.get("FPS_CHANGE").format(fps_before=assigned_fps, real_after=all_config['fps']))
                        break
                    elif choose is False:
                        pt.info(show_text.get("FPS_UNCHANGED"))
                        break
                    else:
                        pt.warn(show_text.get("INPUT_INVALID"))
                        continue
            else:
                pt.error(show_text.get("FPS_MULTIPART_BIG_DIFF"))
                pt.info(show_text.get("FPS_MULTIPART_INFO").format(real_fps_list=real_fps_list))
                exit()
    else:
        pt.warn(show_text.get("FPS_DEBUG_NOT_CHECK"))

    # *******************************************************************************************************
    # Initialize the temporary environment
    if os.path.exists(export_temp_dir_path):
        try:
            shutil.rmtree(export_temp_dir_path)
        except Exception as e:
            print(e)
    os.makedirs(export_temp_dir_path)
    os.makedirs(export_bootani_dir_path)
    print('')
    # ********************************************************************************************************
    # exit FOR DEBUG
    # exit()

    # ********************************************************************************************************
    # Processing pictures
    pt.info(show_text.get("PIC_PROCESS"))
    for idx, anime_part in enumerate(all_config['anime']):
        print(f'××××××××××××××××part{idx}××××××××××××××××')
        # generate bg_conf dyn_conf sta_confs
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

        # Create an intermediate folder
        os.makedirs(dyn_conf.get('ext_dir'))
        # Discrete gif
        pt.info(show_text.get("PIC_PROCESS_GIF_DISCRETE"))
        gif2png(
            gif_path=dyn_conf.get('gif_path'),
            to_dir_path=dyn_conf.get('ext_dir'),
            temp_im_path=os.path.join(dyn_conf.get('ext_dir'), 'temp.gif')
        )
        while True:
            ipt = input(show_text.get("PIC_PROCESS_PREVIEW").format(idx=idx))
            choose = bool_input_select(ipt, default=False)
            if choose is True:
                pt.info(show_text.get("PIC_PROCESS_PREVIEW_ING"))
                combination_preview(
                    bg_conf=bg_conf,
                    dyn_conf=dyn_conf,
                    sta_confs=sta_confs
                )
                pt.info(show_text.get("PIC_PROCESS_PREVIEW_ED"))
                while True:
                    ipt = input(show_text.get("PIC_PROCESS_GEN_CONTINUE"))
                    choose = bool_input_select(ipt, default=True)
                    if choose is True:
                        break
                    elif choose is False:
                        pt.notice(show_text.get("PIC_PROCESS_GEN_NOT_CONTINUE"))
                        exit()
                        break
                    else:
                        pt.warn(show_text.get("INPUT_INVALID"))
                        continue
                break
            elif choose is False:
                break
            else:
                pt.warn(show_text.get("INPUT_INVALID"))
                continue

        # Combination
        pt.info(show_text.get("PIC_PROCESS_COMBINATION"))
        combination_multi(
            bg_conf=bg_conf,
            dyn_conf=dyn_conf,
            sta_confs=sta_confs
        )
        # Compression
        pt.info(show_text.get("PIC_PROCESS_COMPRESSION"))
        part_compression_multi(
            part_dir=dyn_conf.get('ext_dir')
        )
        # Generate preview gif
        pt.info(show_text.get("PIC_PROCESS_GENERATE_PREVIEW"))
        preview_gif_name = f'{module_export_filename}_p{idx}_preview.gif'
        png2gif(
            png_dir_path=dyn_conf.get('ext_dir'),
            to_gif_path=os.path.join(export_dir_path, preview_gif_name),
            duration=int(1000 / all_config['fps'])
        )
        print('×××××××××××××××××××××××××××××××××××××')
        print('')

    # ********************************************************************************************************
    # Make bootanimation.zip

    # Generate desc.txt
    pt.info(show_text.get("BOOTANIMATION_GENERATE_DESC"))
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

    desc_file_creat(
        desc_path=desc_file_path,
        desc_conf=desc_conf
    )

    # Make bootanimation.zip
    pt.info(show_text.get("BOOTANIMATION_MAKE"))
    bootani_zip_file_creat(
        zipped_dir_path=zipped_dir_path,
        bootani_zip_path=bootani_zip_path
    )

    # Generate module_prop_conf module_config_conf
    module_prop_conf: Dict = all_config.get('module_prop_conf')
    module_config_conf: Dict = all_config.get('module_config_conf', None)

    # ********************************************************************************************************
    # Make module

    pt.info(show_text.get("MODULE_MAKE"))
    # Prepare Magisk template
    template_prepare(
        template_dir_path=export_dir_path,
        template_file_name=template_file_name,
        download_url=template_download_url,
        unzip_dir_path=export_temp_dir_path
    )
    # Edit update-binary
    update_binary_modify(
        update_binary_file_path=update_binary_file_path,
        module_installer_sh_url=module_installer_sh_url
    )
    # Edit module.prop
    module_prop_modify(
        module_prop_file_path=module_prop_file_path,
        module_prop_conf=module_prop_conf
    )
    # Edit install.sh
    module_config_modify(
        module_config_file_path=module_install_file_path,
        module_config_conf=module_config_conf
    )
    # Packaging
    module_pack(
        bootani_zip_path=bootani_zip_path,
        module_media_dir_path=module_media_dir_path,
        placeholder_path=module_placeholder_file_path,
        template_dir_path=template_dir_path,
        module_export_file_path=module_export_file_path
    )

    # ********************************************************************************************************
    # Clean
    while True:
        ipt = input(show_text.get("CLEAN"))
        choose = bool_input_select(ipt, default=True)
        if choose is True:
            clean(export_temp_dir_path)
            break
        elif choose is False:
            break
        else:
            continue

    print("")
    pt.info(show_text.get("COMPLETE_0"))
    pt.info(show_text.get("COMPLETE_1").format(path=os.path.abspath(export_dir_path), filename=module_export_filename))


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



