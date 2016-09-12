# L5MapEditor
Simple map editor (use sqlite)

[![Build Status](http://img.shields.io/travis/bssthu/L5MapEditor.svg)](https://travis-ci.org/bssthu/L5MapEditor)
[![Coverage Status](http://img.shields.io/coveralls/bssthu/L5MapEditor.svg)](https://coveralls.io/r/bssthu/L5MapEditor)
[![Code Climate](http://img.shields.io/codeclimate/github/bssthu/L5MapEditor.svg)](https://codeclimate.com/github/bssthu/L5MapEditor)
[![License](http://img.shields.io/:license-lgplv3-blue.svg)](http://www.gnu.org/licenses/lgpl-3.0.html)

简易地图编辑器，将分级的多边形数据存储到 sqlite 数据库中。

## 开发环境
PyQt5 (PyQt5-5.5-gpl-Py3.4-Qt5.5.0-x64)

#### 发布方法
```bash
make      # 生成 *_rc.py, ui_*.py 等
make install  # 在 build/ 路径生成 .exe 等，需要 cx_Freeze
```

## 其他说明
* [快速入门](docs/quickstart.md)
* [外部数据](docs/data.md)
* [命令说明](docs/commands.md)
* [开发规范](docs/spec.md)
* [主要模块](docs/modules.md)

## License
LGPL-3.0
