from typing import Optional
import cadquery as cq
from cadquery import exporters

# box = (cq.Workplane()
#        .box(26, 26, 2)
#        .translate((0, 0, 1))
#        )


pottery = cq.Sketch().importDXF('pottery.dxf')
iron_mill_outer = cq.Sketch().importDXF('iron-mill-outer.dxf')
iron_mill_inner = cq.Sketch().importDXF('iron-mill-inner.dxf')

# w = cq.Workplane().placeSketch(pottery).extrude(2)
# w = cq.Workplane().placeSketch(iron_mill_outer).extrude(2)


def shrink(w: cq.Workplane, x: float, y: Optional[float] = None) -> cq.Workplane:
    if y is None:
        y = x

    assert len(w.objects) == 1
    obj = w.objects[0]
    assert isinstance(obj, cq.Shape)

    bb = obj.BoundingBox()
    fx = x / (bb.xmax - bb.xmin)
    fy = y / (bb.ymax - bb.ymin)
    t = cq.Matrix([
        [fx, 0, 0, 0],
        [0, fy, 0, 0],
        [0,  0, 1, 0],
        [0,  0, 0, 1]
    ])

    obj = obj.transformGeometry(t)
    c_bb = obj.CenterOfBoundBox()
    obj = obj.translate([-c_bb.x, -c_bb.y, 0])
    return w.newObject([obj])


# objs = list()
# for o in w.objects:
#     if isinstance(o, cq.Shape):
#         bb = o.BoundingBox()
#         print(bb.xmax - bb.xmin, bb.ymax - bb.ymin)
#         f = 26 / (bb.xmax - bb.xmin)
#         t = cq.Matrix([
#             [f, 0, 0, 0],
#             [0, f, 0, 0],
#             [0, 0, 1, 0],
#             [0, 0, 0, 1]
#         ])
#         o = o.transformGeometry(t)
#         c = o.CenterOfBoundBox()
#         o = o.translate([-c.x, -c.y, 0])
#     objs.append(o)
# w = w.newObject(objs)

# w = shrink(w, 26)

# pot = box.cut(w)
# exporters.export(w, 'pot.stl')

# print(pottery.wires().vals())

tile_size = 26
tile_height = 2
outer = cq.Workplane().placeSketch(iron_mill_outer).extrude(tile_height)
inner = cq.Workplane().placeSketch(iron_mill_inner).extrude(tile_height)
outer = shrink(outer, tile_size)
inner = shrink(inner, tile_size)
iron_mill = (cq.Workplane()
             .box(tile_size, tile_size, tile_height)
             .translate((0, 0, tile_height / 2))
             )
iron_mill = (iron_mill
             .cut(outer)
             .intersect(inner)
             )
exporters.export(iron_mill, 'iron-mill.stl')
show_object(iron_mill)
