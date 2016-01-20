## 外部数据

### 数据库结构
- POLYGON (_id, layer, vertex_Num, vertices)
- L0 (_id, polygon_Id, additional)
- L1 (_id, polygon_Id, additional, parent_Id)
- ...
- L4 (_id, polygon_Id, additional, parent_Id)

POLYGON 为多边形表, layer = #i 则在 L#i 表中可查到它的信息。

L0 至 L4 表示多边形的从属关系。
名字可以在`PolygonLayer.cfg`中修改。

### 配置文件
配置文件使用 JSON 格式编写。

在`PolygonLayer.cfg`中存储表名等信息，
示例见 ![PolygonLayer.cfg](https://github.com/bssthu/L5MapEditor/raw/master/docs/PolygonLayer.cfg.example)
