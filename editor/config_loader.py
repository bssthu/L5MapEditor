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


def loadAll():
    loadLayerNames()


def getLayerNames():
    return LAYER_NAMES


def getLayerName(_id):
    if 0 <= _id < len(LAYER_NAMES):
        return LAYER_NAMES[_id]
    else:
        return str(_id)


def getAdditionalName(layer, additional):
    layer_name = getLayerName(layer)
    if layer_name in ADDITIONAL_NAMES:
        NAMES = ADDITIONAL_NAMES[layer_name]
        if additional in range(0, len(NAMES)):
            return NAMES[additional]
    return str(additional)


def loadLayerNames():
    global LAYER_NAMES
    with open('conf/PolygonLayer.cfg', encoding='utf-8') as fp:
        try:
            string = ''.join(fp.readlines())
            layer_name_json = json.loads(string)
            LAYER_NAMES = tuple(layer_name_json['layer_name'])
        except Exception as e:
            log.error(repr(e))

