import cadquery as cq
import enum
import os
from cadquery import exporters
from typing import List, Optional


class Industry(enum.Enum):
    MANUFACTURER = enum.auto()
    COTTON_MILL = enum.auto()
    BREWERY = enum.auto()
    POTTERY = enum.auto()
    IRON_WORK = enum.auto()
    COAL_MINE = enum.auto()


dir_icon = 'icons'
industry_icon_dxf = {
    Industry.BREWERY: {
        'outer': os.path.join(dir_icon, 'brewery.dxf'),
    },
    Industry.MANUFACTURER: {
        'outer': os.path.join(dir_icon, 'manufacturer.dxf'),
    },
    Industry.COTTON_MILL: {
        'outer': os.path.join(dir_icon, 'cotton-mill.dxf'),
    },
    Industry.COAL_MINE: {
        'outer': os.path.join(dir_icon, 'coal-mine.dxf'),
    },
    Industry.POTTERY: {
        'outer': os.path.join(dir_icon, 'pottery.dxf'),
    },
    Industry.IRON_WORK: {
        'outer': os.path.join(dir_icon, 'iron-mill-outer.dxf'),
        'inner': [
            os.path.join(dir_icon, 'iron-mill-inner.dxf'),
        ],
    },
}


def load_icon(outer_dxf: str, t: float, x: float, y: Optional[float] = None,
              inner_dxfs: Optional[List[str]] = None) -> cq.Workplane:
    '''Returns icon centeerd on X & Y and top at Z=0'''
    if y is None:
        y = x
    if inner_dxfs is None:
        inner_dxfs = list()

    part = cq.Workplane().box(x, y, t).translate((0, 0, -t/2))
    outer_negative = load_negative(outer_dxf, x, y, t)
    part = part.cut(outer_negative)
    for inner_dxf in inner_dxfs:
        inner_negative = load_negative(inner_dxf, x, y, t)
        part = part.intersect(inner_negative)

    return part


def load_negative(dxf: str, x: float, y: float, t: float) -> cq.Workplane:
    '''Returns negative centeerd on X & Y and top at Z=0'''
    s = cq.Sketch().importDXF(dxf)
    o = cq.Workplane().placeSketch(s).extrude(-t)
    o = shrink_xy(o, x, y)
    return o


def shrink_xy(w: cq.Workplane, x: float, y: Optional[float] = None
              ) -> cq.Workplane:
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


# industry = Industry.IRON_WORK
# icon = load_icon(outer_dxf=industry_icon_dxf[industry]['outer'],
#                  t=2, x=26, y=26,
#                  inner_dxfs=industry_icon_dxf[industry].get('inner', list()))

tol_tight_fit = 0.1
T_wall = 0.5
T_wall_height = 1
T_base = 3
T_icon = 2
HW_token = 25.4 + 2 * tol_tight_fit
sampler = (cq.Workplane()
           .box(T_wall + (HW_token + T_wall) * len(industry_icon_dxf),
                2 * T_wall + HW_token,
                T_base + T_wall_height,
                centered=False)
           )

X_bottom = T_wall
Y_center = (2 * T_wall + HW_token) / 2
Z_top = T_base

sampler = sampler.faces('>Z').workplane()
workplanes = list()
for industry, dxfs in industry_icon_dxf.items():
    X_center = X_bottom + HW_token / 2
    sampler = (sampler
               .moveTo(X_center, Y_center)
               .rect(HW_token, HW_token)
               .extrude(-T_wall_height, combine='cut')
               )
    icon = (load_icon(outer_dxf=dxfs['outer'],
                      t=T_icon, x=HW_token, y=HW_token,
                      inner_dxfs=dxfs.get('inner', list()))
            .translate((X_center, Y_center, Z_top))
            )
    sampler = sampler.cut(icon)
    workplanes.append(icon)

    X_bottom += HW_token + T_wall
workplanes.append(sampler)

vals = list()
for w in workplanes:
    for o in w.all():
        vals.extend(o.vals())
sampler_compound = cq.Compound.makeCompound(vals)
show_object(sampler_compound)


dir_out = 'models'
os.makedirs(dir_out, exist_ok=True)
sampler_compound.exportStep(os.path.join(dir_out, 'sampler.step'))
