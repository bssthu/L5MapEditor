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

## 数据库结构
- POLYGON (_id, type, vertex_Num, vertices)
- L0 (_id, polygon_Id, type)
- L1 (_id, polygon_Id, type, parent_Id)
- ...
- L4 (_id, polygon_Id, type, parent_Id)

POLYGON 为多边形表, type = #i 则在 L#i 表中可查到它的信息。

L0 至 L4 表示多边形的从属关系。

## 界面简介
略

## 操作说明

#### 打开/保存
略。注意本程序没有撤销、自动备份等功能。

#### 插入
点击 ![插入](https://github.com/bssthu/L5MapEditor/raw/master/img/add.png) 按钮开始插入多边形。

单击左键插入顶点，单击右键删除一个最新的顶点，按住左键可预览插入效果。

#### 删除
点击 ![删除](https://github.com/bssthu/L5MapEditor/raw/master/img/close.png) 按钮，
删除在表1中选中的多边形。
无法撤销。

#### 移动
点击 ![移动](https://github.com/bssthu/L5MapEditor/raw/master/img/move.png) 按钮开始移动操作。

当 ![移动点](https://github.com/bssthu/L5MapEditor/raw/master/img/dot.png) 按钮被激活时，
移动的是在表2中选中的点（用红色圈出）。
否则移动的是整个多边形。

单击左键移动，单击右键复原。

## License
LGPLv3
