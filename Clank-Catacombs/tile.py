import cadquery as cq
import os
from cadquery import exporters

tol_comfort = 0.3
tol_tight_fit = 0.16

H_tile = 100
W_tile = 100
T_tile = 1.60
T_tiles = 24

T_wall = 2
W_finger_cutout = 28
H_finger_cutout = 5

W_tile_inner = W_tile + 2 * tol_comfort
W_box_inner = W_tile_inner + T_wall + W_tile_inner
H_box_inner = H_tile + 2 * tol_comfort
T_box_inner = T_tiles + T_tile
T_box_wall_inner = T_tiles

tile_box = (cq.Workplane()
            .box(H_box_inner, W_box_inner, T_box_inner)
            .faces('>Z')
            .shell(T_wall)
            .faces('+Z').faces('<Z')
            .workplane()
            .rect(H_box_inner, T_wall)
            .extrude(T_box_wall_inner)
            .moveTo(0, T_wall / 2 + W_tile_inner / 2)
            .rect(H_box_inner + 2 * T_wall, W_finger_cutout)
            .moveTo(0, -(T_wall / 2 + W_tile_inner / 2))
            .rect(H_box_inner + 2 * T_wall, W_finger_cutout)
            .extrude(T_box_inner, combine='cut')
            .moveTo((H_box_inner + 2 * T_wall) / 2,
                    (T_wall + W_tile_inner) / 2 + W_finger_cutout / 2)
            .sagittaArc(((H_box_inner + 2 * T_wall) / 2,
                        (T_wall + W_tile_inner) / 2 - W_finger_cutout / 2),
                        -H_finger_cutout)
            .close()
            .mirrorX()
            .mirrorY()
            .cutThruAll()
            )

print(T_box_inner + T_wall)

dir_cwd = os.getcwd()
dir_models = 'models'
os.makedirs(dir_models, exist_ok=True)
os.chdir(dir_models)
exporters.export(tile_box, 'tile_box.stl')
os.chdir(dir_cwd)
