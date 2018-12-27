import os
from typing import Any, List, Dict, Tuple, Optional


def yes_or_no(input_content: str, default: Optional[bool] = None) -> Optional[bool]:
    """
    according to input content return True or False
    :param input_content: input content
    :param default: if input is None, using default as choice
    :return: bool, choice
    """
    yes_list = ['Y', 'y', 'Yes', 'yes', 'YES']
    no_list = ['N', 'n', 'No', 'no', 'NO']

    if default is True:
        yes_list.append('')
    elif default is False:
        no_list.append('')
    else:
        pass

    if input_content in yes_list:
        return True
    elif input_content in no_list:
        return False
    else:
        print('输入无效，请重试！')
        return None


def quit_() -> None:
    """
    custom exit
    :return: None
    """
    ipt = input('按回车键退出...')
    exit()



















