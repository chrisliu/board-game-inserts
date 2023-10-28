import cadquery as cq
from cadquery import exporters

tol_comfort = 0.3
tol_tight_fit = 0.1

T_wall = 0.8
T_wall_reinforced = 1.2

T_inner_40 = 25.5
T_inner_30 = T_inner_40 / 40 * 30
T_inner_28 = T_inner_40 / 40 * 28
T_inner_15 = T_inner_40 / 40 * 15
T_inner_12 = T_inner_40 / 40 * 12
H_card = 92.25
W_card = 66.5

W_border = 4.5

H_inner = H_card + 2 * tol_comfort
W_inner = W_card + 2 * tol_comfort

# Unit sizes.
T_max = T_inner_28 + T_inner_12
H_unit = (H_inner + T_wall + 2 * tol_tight_fit) + 2 * T_wall
W_unit = (W_inner + 2 * T_wall + 2 * tol_tight_fit) + 2 * T_wall
T_unit = (T_max + T_wall + 4 * tol_tight_fit) + 2 * T_wall
T_deck_box = (T_inner_40 + 2 * T_wall + 2 * tol_tight_fit) + 2 * T_wall

# Side dimensions.
W_side = 44
H_side = 2 * H_unit
T_side = T_unit

# Top dimennsions.
W_top = 3 * W_unit + W_side
H_top_container = 56.5
H_top_all = 63.5
T_top_container = 2 * T_deck_box
T_top_other = T_unit

# H_side = 10
# W_top = 10

# Side container.
box_side = (cq.Workplane()
            .box(W_side - 2 * T_wall_reinforced,
                 H_side - 2 * T_wall_reinforced,
                 T_side - T_wall_reinforced)
            .faces('>Z')
            .shell(T_wall_reinforced)
            )

# Top container.
box_top = (cq.Workplane()
           .box(W_top - 2 * T_wall_reinforced,
                H_top_container - 2 * T_wall_reinforced,
                T_top_container - T_wall_reinforced)
           .faces('>Z')
           .shell(T_wall_reinforced, kind='intersection')
           .faces('>Y')
           .workplane()
           .moveTo(0, -T_top_container / 2 - T_wall_reinforced / 2)
           .rect(W_top, T_top_other, centered=(True, False))
           .extrude(H_top_all - H_top_container)
           )

exporters.export(box_top, 'layout_top.stl')
exporters.export(box_side, 'layout_side.stl')
