#!/usr/local/bin/python3 python3
import os
import sys
sys.path.insert(0,"../")
if not os.getenv("DJANGO_SETTINGS_MODULE"):  # 获取全局变量DJANGO_SETTINGS_MODULE
    os.environ["DJANGO_SETTINGS_MODULE"] = 'mall.settings.dev'

import django

django.setup()

from contents.crons import  generate_static_index_html

if __name__ == '__main__':
    generate_static_index_html()