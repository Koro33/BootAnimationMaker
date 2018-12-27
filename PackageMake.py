import os
import re
import shutil
from typing import Any, List, Dict, Tuple, Optional, IO
import utils


def desc_file_creat(desc_path: str, desc_conf: Dict) -> IO:
    """
    creat <desc.txt> file
    reference: <https://android.googlesource.com/platform/frameworks/base/+/master/cmds/bootanimation/FORMAT.md>
    :param desc_path: path to desc.txt
    :param desc_conf:
    desc_dict = {
        'width': '1080',
        'height': '1920',
        'fps': '30',
        'parts': [
            {'type': 'p', 'count': '0', 'pause': '0', 'path': 'part0'},
            {'type': 'c', 'count': '0', 'pause': '0', 'path': 'part1'}
        ]
    }
    :return: file IO
    """
    width = desc_conf.get('width')
    height = desc_conf.get('height')
    fps = desc_conf.get('fps')

    with open(desc_path, mode="w+") as desc_f:
        content = "{} {} {}\n".format(width, height, fps)
        for part in desc_conf.get('parts'):
            content += "{} {} {} {}\n".format(part['type'], part['count'], part['pause'], part['path'])
        desc_f.write(content)

    return desc_f


def bootani_zip_file_creat(zipped_dir_path: str, bootani_zip_path: str) -> None:
    """
    creat <bootanimation.zip>
    :param zipped_dir_path: directory to be zipped
    :param bootani_zip_path: path to <bootanimation.zip>
    :return: None
    """
    utils.dir2zipfile(zipped_dir_path, bootani_zip_path, incl_emptydir=True)


def template_prepare(template_dir_path: str, template_file_name: str, download_url: str, unzip_dir_path: str) -> None:
    """
    download and unzip Magisk template
    :param template_dir_path: directory content template
    :param template_file_name: template file name
    :param download_url: Magisk template url
    :param unzip_dir_path: path to unzip
    :return: None
    """
    template_file_path = os.path.join(template_dir_path, template_file_name)
    if not os.path.exists(template_file_path):
        utils.download_file(download_url, template_file_path)
    utils.unzipfile(template_file_path, unzip_dir_path)


def module_prop_modify(module_prop_file_path: str, module_prop_conf: Dict) -> None:
    """
    <module.prop> modify
    :param module_prop_file_path: path to <module.prop> file
    :param module_prop_conf:
    {
    'mid': 'bootanimation-000'
    'name': 'BootAnimation'
    'version': '1.0'
    'versionCode': '2018103101'
    'author': 'Zarcher'
    'description': 'A Boot Animation Magisk Module'
    'minMagisk': '17000'
    }
    :return: None
    """
    content_list = [
        f"id={module_prop_conf.get('mid')}\n",
        f"name={module_prop_conf.get('name')}\n",
        f"version={module_prop_conf.get('version')}\n",
        f"versionCode={module_prop_conf.get('versionCode')}\n",
        f"author={module_prop_conf.get('author')}\n",
        f"description={module_prop_conf.get('description')}\n",
        f"minMagisk={module_prop_conf.get('minMagisk')}\n"
    ]
    content = ''.join(content_list)
    with open(module_prop_file_path, 'w+') as mp_f:
        mp_f.write(content)


def module_config_modify(module_config_file_path: str, module_config_conf: Optional[Dict] = None) -> None:
    """
    module <config.sh> modify
    :param module_config_file_path:
    :param module_config_conf:
    {
    'ui_print': 'ui_print "     Boot Animation    "\n'
    'REPLACE': 'REPLACE="\n\n"'
    }
    :return:
    """
    if module_config_conf is None:
        sub_contents = [
            'ui_print "     A Boot Animation Magisk Module    "\n',
            'REPLACE="\n' + '' + '\n"'
        ]
    else:
        sub_contents = [
            module_config_conf.get('ui_print'),
            module_config_conf.get('REPLACE')
        ]

    patts = [
        re.compile('ui_print "     Magisk Module Template    "\n'),
        re.compile('REPLACE="\n"')
    ]

    with open(module_config_file_path, 'r') as f:
        content = f.read()
    with open(module_config_file_path, 'w') as f:
        for patt, sub_content in zip(patts, sub_contents):
            # print(re.findall(patt, content))
            content = re.sub(patt, sub_content, content)
        f.write(content)


def module_pack(bootani_zip_path: str, module_media_dir_path: str, placeholder_path: str, template_dir_path: str,
                module_export_file_path: str) -> None:
    """
    pack the module
    :param bootani_zip_path:
    :param module_media_dir_path:
    :param placeholder_path:
    :param template_dir_path:
    :param module_export_file_path:
    :return: None
    """
    os.mkdir(module_media_dir_path)
    shutil.move(bootani_zip_path, module_media_dir_path)
    os.remove(placeholder_path)
    utils.dir2zipfile(template_dir_path, module_export_file_path)


def clean(export_temp_dir_path) -> None:
    """
    clean temporary directory
    :param export_temp_dir_path: temporary directory path to be cleaned
    :return:
    """
    shutil.rmtree(export_temp_dir_path)


if __name__ == '__main__':
    pass









