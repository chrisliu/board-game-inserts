import cadquery as cq
import os
from cadquery import exporters

T_box = 51.3
WH_corner = 65

T_wall = 1.2

WH_corner_all = WH_corner + T_wall
T_corner_all = T_box + 2 * T_wall


corner = (cq.Workplane()
          .box(WH_corner_all, WH_corner_all, T_corner_all, centered=False)
          .faces('>X')
          .workplane(origin=(0, 0, 0))
          .moveTo(0, T_corner_all / 2)
          .rect(WH_corner, T_box, centered=(False, True))
          .extrude(-WH_corner, combine='cut')
          .faces('>Z')
          .workplane(origin=(0, 0, 0))
          .moveTo(0, 0)
          .lineTo(WH_corner_all, WH_corner_all)
          .lineTo(WH_corner_all, 0)
          .close()
          .cutThruAll()
          )

corner = (corner
          .faces('not(+X or -Y or |Z)')
          .edges()
          .fillet(T_wall / 2 * 0.95)
          )

dir_out = 'models'
os.makedirs(dir_out, exist_ok=True)
exporters.export(corner, os.path.join(dir_out, 'box_corner.stl'))
