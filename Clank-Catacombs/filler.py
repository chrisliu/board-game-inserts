import cadquery as cq
import os
from cadquery import exporters

tol_comfort = 0.3
tol_tight_fit = 0.16

H_deck = 96.5
W_deck = 87.2
T_deck = 70

T_wall = 1.2

H_box = 290
W_box = 290
H_tile_box = 104.6
H_market_box = 65.8

W_tile_box = 207.2

H_deck_aligner = H_box - H_tile_box - H_market_box - 0.5
W_deck_aligner = W_tile_box
T_deck_aligner = 50

deck_aligner = (cq.Workplane()
                .box(H_deck_aligner, W_deck_aligner, T_deck_aligner)
                .moveTo(0, W_deck_aligner / 2)
                .rect(W_deck, -H_deck, centered=(True, False))
                .moveTo(0, -W_deck_aligner / 2)
                .rect(W_deck, H_deck, centered=(True, False))
                .cutThruAll()
                .fillet(T_wall)
                )

print(H_deck_aligner + H_tile_box)

H_misc_box_inner = H_deck_aligner + H_tile_box - 2 * T_wall
W_misc_box_inner = W_box - W_tile_box - 0.5 - 2 * T_wall
T_misc_box_inner = T_deck / 3 - T_wall
misc_box = (cq.Workplane()
            .box(H_misc_box_inner, W_misc_box_inner, T_misc_box_inner)
            .faces('>Z')
            .shell(T_wall)
            )

half_misc_box = (cq.Workplane()
                 .box((H_misc_box_inner - 2 * T_wall - tol_tight_fit) / 2,
                      W_misc_box_inner,
                      T_misc_box_inner)
                 .faces('>Z')
                 .shell(T_wall)
                 )

H_tile_misc_box_inner = H_tile_box - 2 * T_wall
W_tile_misc_box_inner = W_tile_box - 2 * T_wall
T_tile_misc_box_inner = T_deck - 44 - T_wall
tile_misc_box = (cq.Workplane()
                 .box(H_tile_misc_box_inner,
                      W_tile_misc_box_inner,
                      T_tile_misc_box_inner)
                 .faces('>Z')
                 .shell(T_wall)
                 )

T_top_misc_box_outer = 31
H_top_misc_box_outer = W_misc_box_inner + 2 * T_wall
H_top_misc_box_support = 37.5
top_misc_box = (cq.Workplane()
                .box(H_misc_box_inner, W_misc_box_inner,
                T_top_misc_box_outer - T_wall)
                .faces('>Z')
                .shell(T_wall)
                .faces('>Z')
                .workplane()
                .moveTo(0, H_top_misc_box_outer / 2 - H_top_misc_box_support)
                .rect(H_misc_box_inner + 2 * T_wall,
                      -(H_top_misc_box_outer - H_top_misc_box_support),
                      centered=(True, False))
                .extrude(-(T_top_misc_box_outer - T_misc_box_inner + T_wall),
                         combine='cut')
                )

H_upper_filler_outer = H_market_box
W_upper_filler_outer = (W_box - 0.5) / 2
T_upper_filler_outer = 50.5
upper_filler_box = (cq.Workplane()
                    .box(H_upper_filler_outer - 2 * T_wall,
                         W_upper_filler_outer - 2 * T_wall,
                         T_upper_filler_outer - T_wall)
                    .faces('>Z')
                    .shell(T_wall)
                    )

show_object(upper_filler_box)


dir_cwd = os.getcwd()
dir_models = 'models'
os.makedirs(dir_models, exist_ok=True)
os.chdir(dir_models)
exporters.export(deck_aligner, 'deck_aligner.stl')
exporters.export(misc_box, 'misc_box.stl')
exporters.export(half_misc_box, 'half_misc_box.stl')
exporters.export(tile_misc_box, 'tile_misc_box.stl')
exporters.export(top_misc_box, 'top_misc_box.stl')
exporters.export(upper_filler_box, 'upper_filler_box.stl')
os.chdir(dir_cwd)
