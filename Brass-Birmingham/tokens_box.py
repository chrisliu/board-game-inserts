import cadquery as cq
import enum
import math
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


tol_tight_fit = 0.1
T_wall_min = 1
R_printer_fillet = 0.75
T_token_slot = 2

T_finger_slot = 13

W_industry_token = 25.5
H_industry_token = 25.5
T_industry_tokens = {
    Industry.BREWERY: 15.1,
    Industry.MANUFACTURER: 24,
    Industry.COTTON_MILL: 24,
    Industry.COAL_MINE: 15.1,
    Industry.POTTERY: 11.1,
    Industry.IRON_WORK: 8.6,
}
industry_order = [Industry.BREWERY, Industry.MANUFACTURER, Industry.COTTON_MILL,
                  Industry.COAL_MINE, Industry.POTTERY, Industry.IRON_WORK]
N_industry_tokens = len(T_industry_tokens)

W_link_token = 30.2  # Long side.
H_link_token = 16.2
T_link_token = 15
N_link_tokens = 2

W_box_space = 190
H_box_space = 227
T_box_space = 27

# Compute dimension for each player's token box
N_players = 4
W_player_box = (max(W_industry_token, W_link_token)
                + 2 * T_wall_min
                + 2 * tol_tight_fit)
H_player_box = H_box_space
T_player_box = T_box_space

assert W_player_box <= W_box_space / N_players

T_dividing_wall = (
    (H_player_box
     - N_industry_tokens * (H_industry_token + 2 * tol_tight_fit)
     - N_link_tokens * (H_link_token + 2 * tol_tight_fit))
    / (N_industry_tokens + N_link_tokens + 1)
)
T_industry_wall = (
    (W_player_box
     - (W_industry_token + 2 * tol_tight_fit))
    / 2)
T_link_wall = (
    (W_player_box
     - (W_link_token + 2 * tol_tight_fit))
    / 2)

assert T_dividing_wall > T_wall_min
assert T_industry_wall > T_wall_min
assert T_link_wall > T_wall_min

T_industry_icon = 0.64
T_base_min = 1
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


# Draw token box
# H_player_box = (3 * (H_industry_token + 2 * tol_tight_fit)
#                 + H_link_token + 2 * tol_tight_fit
#                 + 5 * T_dividing_wall)
token_box = (cq.Workplane()
             .box(H_player_box, W_player_box, T_player_box, centered=False)
             .edges().fillet(R_printer_fillet)
             )

X_bottom = T_dividing_wall
Y_center = W_player_box / 2
Z_top = T_player_box

R_industry_finger_slot = math.sqrt(
    (T_finger_slot / 2) ** 2 + T_industry_wall ** 2)
sphere_industry_finger = cq.Workplane().sphere(R_industry_finger_slot)

token_box = token_box.faces('>Z').workplane()
token_icons = list()
for industry in industry_order:
# for industry in [Industry.POTTERY, Industry.IRON_WORK, Industry.MANUFACTURER]:
    T_industry_fit = T_industry_tokens[industry] + tol_tight_fit
    W_industry_fit = W_industry_token + 2 * tol_tight_fit
    H_industry_fit = H_industry_token + 2 * tol_tight_fit

    token_box = (token_box
                 .moveTo(X_bottom, Y_center)
                 .rect(H_industry_fit, W_industry_fit, centered=(False, True))
                 .extrude(-T_industry_fit, combine='cut')
                 .moveTo(X_bottom + H_industry_fit / 2, Y_center + W_player_box / 2)
                 .circle(R_industry_finger_slot)
                 .moveTo(X_bottom + H_industry_fit / 2, Y_center - W_player_box / 2)
                 .circle(R_industry_finger_slot)
                 .extrude(-T_industry_fit, combine='cut')
                 )

    # Cut finger notch.
    token_box = token_box.cut(sphere_industry_finger.translate(
        (X_bottom + H_industry_fit / 2,
         Y_center + W_player_box / 2,
         Z_top - T_industry_fit)
    ))

    token_box = token_box.cut(sphere_industry_finger.translate(
        (X_bottom + H_industry_fit / 2,
         Y_center - W_player_box / 2,
         Z_top - T_industry_fit)
    ))

    # Cut icon.
    dxfs = industry_icon_dxf[industry]
    T_icon = min(T_player_box - T_industry_fit - T_base_min, T_industry_icon)
    icon = (load_icon(outer_dxf=dxfs['outer'],
                      x=H_industry_fit, y=W_industry_fit, t=T_icon,
                      inner_dxfs=dxfs.get('inner', list()))
            .translate((X_bottom + H_industry_fit / 2,
                        Y_center,
                        Z_top - T_industry_fit))
            )
    icon = icon.intersect(token_box)
    token_box = token_box.cut(icon)
    token_icons.append(icon)

    X_bottom += H_industry_fit + T_dividing_wall

for _ in range(N_link_tokens):
# for _ in range(1):
    T_link_fit = T_link_token + tol_tight_fit
    W_link_fit = W_link_token + 2 * tol_tight_fit
    H_link_fit = H_link_token + 2 * tol_tight_fit

    token_box = (token_box
                 .moveTo(X_bottom, Y_center)
                 .rect(H_link_fit, W_link_fit - H_link_fit,
                       centered=(False, True))
                 .extrude(-T_link_fit, combine='cut')
                 .moveTo(X_bottom + H_link_fit / 2,
                         Y_center + (W_link_fit - H_link_fit) / 2)
                 .circle(H_link_fit / 2)
                 .moveTo(X_bottom + H_link_fit / 2,
                         Y_center - (W_link_fit - H_link_fit) / 2)
                 .circle(H_link_fit / 2)
                 .extrude(-T_link_fit, combine='cut')
                 .moveTo(X_bottom + H_link_fit / 2, Y_center + W_player_box / 2)
                 .circle(R_industry_finger_slot)
                 .moveTo(X_bottom + H_link_fit / 2, Y_center - W_player_box / 2)
                 .circle(R_industry_finger_slot)
                 .extrude(-T_link_fit, combine='cut')
                 )

    token_box = token_box.cut(sphere_industry_finger.translate(
        (X_bottom + H_link_fit / 2,
         Y_center + W_player_box / 2,
         Z_top - T_link_fit)
    ))

    token_box = token_box.cut(sphere_industry_finger.translate(
        (X_bottom + H_link_fit / 2,
         Y_center - W_player_box / 2,
         Z_top - T_link_fit)
    ))

    X_bottom += H_link_fit + T_dividing_wall

# Chamfer token slots.
token_box = (token_box
             .edges('>Z')
             .edges('not(>X or <X or >Y or <Y)')
             .edges('not(>Y or <Y)')
             .edges('not(>Y or <Y)')
             .chamfer(T_token_slot / 2)
             )

vals = list()
for w in [token_box] + token_icons:
    for o in w.all():
        vals.extend(o.vals())
token_box_compound = cq.Compound.makeCompound(vals)
show_object(token_box_compound)

dir_out = 'models'
os.makedirs(dir_out, exist_ok=True)
token_box_compound.exportStep(os.path.join(dir_out, 'token_box.step'))
