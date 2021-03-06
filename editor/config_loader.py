#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Module        : config_loader.py
# Author        : bssthu
# Project       : L5MapEditor
# Creation date : 2016-01-20
# Description   :
#


import json
from editor import log


LAYER_NAMES = ('L0', 'L1', 'L2', 'L3', 'L4')
ADDITIONAL_NAMES = {}


def load_all():
    """载入配置文件"""
    load_layer_names()


def get_layer_names():
    """获取 layer 名称列表

    Returns:
        layer_names (list[str]): layer 名称列表
    """
    return LAYER_NAMES


def get_layer_name(_id):
    """获取 layer 名称

    Args:
        _id (int): layer id

    Returns:
        layer_name (str): layer 名称
    """
    if 0 <= _id < len(LAYER_NAMES):
        return LAYER_NAMES[_id]
    else:
        return str(_id)


def get_additional_name(layer, additional):
    """获取 additional 对应的名称

    Args:
        layer (int): layer id
        additional (int): additional id

    Returns:
        additional_name (str): additional 名称
    """
    layer_name = get_layer_name(layer)
    if layer_name in ADDITIONAL_NAMES:
        NAMES = ADDITIONAL_NAMES[layer_name]
        if additional in range(0, len(NAMES)):
            return NAMES[additional]
    return str(additional)


def load_layer_names():
    global LAYER_NAMES
    with open('conf/PolygonLayer.cfg', encoding='utf-8') as fp:
        try:
            string = ''.join(fp.readlines())
            layer_name_json = json.loads(string)
            LAYER_NAMES = tuple(layer_name_json['layer_name'])
        except Exception as e:
            log.error(repr(e))
