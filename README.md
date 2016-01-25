# L5MapEditor
Simple map editor (use sqlite)

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
LGPLv3
