## 命令说明

可以使用命令编辑地图。

### 命令列表
```bash
add shape           # 插入空多边形
add pt              # 向现有多边形插入顶点
del shape           # 删除多边形
del pt              # 删除多边形中的某个顶点
mov shape           # 移动多边形
mov pt              # 移动多边形的某个顶点
set pt              # 修改某个顶点的坐标
set layer           # 修改多边形的 layer 信息
set additional      # 修改多边形的附加信息
```

### 使用示例
```bash
# add shape polygon_id layer additional [parent_id]
add shape 2 1 0 1
# add pt polygon_id x y
add pt 2 0.0 0.0
# del shape polygon_id
del shape 3
# del pt polygon_id point_id
del pt 2 1
# mov shape polygon_id dx dy
mov shape 2 1.0 1.0
# mov pt polygon_id point_id dx dy
mov pt 2 0 1.0 1.0
# set pt polygon_id point_id x y
set pt 2 0 0.0 0.0
# set layer polygon_id layer
set layer 2 3
# set additional polygon_id layer
set additional 2 3
```
