import cadquery as cq
import os
import math
from cadquery import exporters

tol_comfort = 0.3
tol_tight_fit = 0.16

T_wall = 1.2

W_finger_slot = 14

sides_treasure_token = 6
R_treasure_token = 27.5 / 2 / \
    math.sin(math.radians(360 / sides_treasure_token))
T_treasure_token = 11.3

H_market_item = 20
W_market_item = 20
T_blood_amulet = 3.2
T_backpack = 3.2
T_burglar_kit = 4.8
T_crown = 4.8

H_mastery_token = 20
W_mastery_token = 20
T_mastery_token = 6.6

R_monkey_idol = 20.2 / 2
T_monkey_idol = 4.8

H_shop_token = 58.6
W_shop_token = 130
T_shop_token = 1.6

H_shop_token_fit = H_shop_token + 2 * tol_comfort
W_shop_token_fit = W_shop_token + 2 * tol_comfort

H_shop_token_slot = 3
W_shop_token_slot = W_shop_token_fit
T_shop_token_slot = 7

H_shop_outer = H_shop_token_fit + H_shop_token_slot + 3 * T_wall
W_shop_outer = W_shop_token_slot + 2 * T_wall
T_shop_outer = T_shop_token + H_market_item + 2 * tol_comfort + T_wall

market_shop = (cq.Workplane()
               .box(H_shop_outer, W_shop_outer, T_shop_outer)
               .edges('|Z or <Z')
               .fillet(T_wall)
               )

market_shop = market_shop.faces('>Z').workplane()

# Cut shop display slot.
market_shop = (market_shop
               .moveTo(H_shop_outer / 2 - T_wall, 0)
               .rect(-H_shop_token_slot, W_shop_token_slot,
                     centered=(False, True))
               .extrude(-T_shop_token_slot, combine='cut')
               )

# Cut shop token slot.
market_shop = (market_shop
               .moveTo(-H_shop_outer / 2 + T_wall, 0)
               .rect(H_shop_token_fit, W_shop_token_fit,
                     centered=(False, True))
               .extrude(-T_shop_token, combine='cut')
               )

# Cut treasure slot.
R_treasure_token_fit = R_treasure_token + tol_comfort
H_treasure_token = 2 * R_treasure_token_fit
W_treasure_token = (2 * R_treasure_token_fit *
                    math.sin(math.radians(360 / sides_treasure_token)))
sketch_treasure_token = (cq.Sketch()
                         .regularPolygon(R_treasure_token_fit,
                                         sides_treasure_token,
                                         angle=360 / sides_treasure_token / 2)
                         )
treasure_x = -H_shop_outer / 2 + T_wall + H_shop_token_fit / 2
market_shop = (market_shop
               .moveTo(treasure_x,
                       W_shop_outer / 2 - T_wall - W_treasure_token / 2)
               .placeSketch(sketch_treasure_token)
               .extrude(-(T_treasure_token + T_shop_token), combine='cut')
               .moveTo(treasure_x, W_shop_outer / 2)
               .rect(W_finger_slot, -T_wall, centered=(True, False))
               .extrude(-(T_treasure_token + T_shop_token), combine='cut')
               )


# Cut market items.
T_items = [T_blood_amulet, T_backpack, T_burglar_kit, T_crown]  # L->R
item_y = W_shop_token_fit / (len(T_items) + 1)
for i, T_item in enumerate(T_items):
    cur_item_y = W_shop_outer / 2 - T_wall - item_y * (i + 1)
    market_shop = (market_shop
                   .moveTo(-H_shop_outer / 2 + T_wall, cur_item_y)
                   .rect(
                       T_item + 2 * tol_comfort,
                       W_market_item + 2 * tol_comfort,
                       centered=(False, True))
                   .extrude(
                       -(T_shop_token + H_market_item + 2 * tol_comfort),
                       combine='cut')
                   .moveTo(-H_shop_outer / 2, cur_item_y)
                   .rect(T_wall, W_finger_slot, centered=(False, True))
                   .extrude(
                       -(T_shop_token + H_market_item + 2 * tol_comfort),
                       combine='cut')
                   )

# Cut mastery and monkey idol tokens.
H_tokens = [H_mastery_token, 2 * R_monkey_idol]
W_tokens = [W_mastery_token, 2 * R_monkey_idol]
T_tokens = [T_mastery_token, T_monkey_idol]  # Bot->Top
item_x = H_shop_token_fit / 4
seps = [item_x, 3 * item_x]
for i, (H_token, W_token, T_token, sep) in enumerate(
        zip(H_tokens, W_tokens, T_tokens, seps)):
    cur_item_x = -H_shop_outer / 2 + T_wall + sep
    market_shop = (market_shop
                   .moveTo(cur_item_x, -W_shop_outer / 2 + T_wall)
                   .rect(H_token + 2 * tol_comfort,
                         T_token + 2 * tol_comfort,
                         centered=(True, False))
                   .extrude(-(T_shop_token + H_token + 2 * tol_comfort),
                            combine='cut')
                   .moveTo(cur_item_x, -W_shop_outer / 2)
                   .rect(W_finger_slot, T_wall, centered=(True, False))
                   .extrude(-(T_shop_token + H_token + 2 * tol_comfort),
                            combine='cut')
                   )

dir_cwd = os.getcwd()
dir_models = 'models'
os.makedirs(dir_models, exist_ok=True)
os.chdir(dir_models)
exporters.export(market_shop, 'market_shop.stl')
os.chdir(dir_cwd)
