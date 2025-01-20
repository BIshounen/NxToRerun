import rerun as rr
from PIL.ImageOps import scale
from rerun import blueprint as rrb
import json
from collections import defaultdict

from pathlib import Path
import cv2


METADATA_PATH = "metadata.json"
IMAGE_PATH = "map.png"

rr.init("rerun_test_cars")

rr.serve_web(open_browser=True)

image_file_path = Path(__file__).parent / IMAGE_PATH

blueprint = rrb.Horizontal(
    rrb.Spatial3DView(origin="/root", name="Root")
)

with open(METADATA_PATH, 'r') as f:
    metadata = json.load(f)


timeline_start = 0
min_lat = 90.0
min_long = 180.0
max_lat = -90.0
max_long = -180.0

for track in metadata:
    min_time = track['firstAppearanceTimeMs']
    max_time = track['lastAppearanceTimeMs']

    if timeline_start == 0 or timeline_start > min_time:
        timeline_start = min_time

    latitudes = []
    longitudes = []

    object_types = defaultdict(lambda : 0)
    for attribute in track['attributes']:
        if attribute['name'] == 'pos_latitude':
            pos_lat = float(attribute['value'])/1000
            latitudes.append(pos_lat)
            if pos_lat > max_lat:
                max_lat = pos_lat
            if pos_lat < min_lat:
                min_lat = pos_lat
        if attribute['name'] == 'pos_longitude':
            pos_long = float(attribute['value'])/1000
            longitudes.append(pos_long)
            if pos_long > max_long:
                max_long = pos_long
            if pos_long < min_long:
                min_long = pos_long
        if attribute['name'] == 'object_type':
            object_types[attribute['value']] += 1

    num_of_steps = min(len(latitudes), len(longitudes))

    object_type = 'unknown'
    object_type_confidence = 0
    for key, value in object_types.items():
        if value > object_type_confidence:
            object_type = key

    i = 0
    current_time = min_time
    while i < num_of_steps:
        rr.set_time_seconds("stable_time", current_time/1000)
        box_centers = [[latitudes[i]*10000, longitudes[i]*10000, 0.3]]
        color = (0, 255, 0) if object_type == 'car' else (255, 0, 0)
        (rr.log(
            f"vehicles/{object_type}/{track['id']}",
            rr.Boxes3D(half_sizes=[.3,.3,.3], centers=box_centers, fill_mode="solid", colors=[color]))
        )
        current_time += (max_time - min_time)/num_of_steps
        i += 1

    rr.set_time_seconds("stable_time", current_time / 1000)
    rr.log(f"vehicles/{object_type}/{track['id']}", rr.Clear(recursive=True))

rr.set_time_seconds("stable_time", timeline_start/1000)

vertex_positions_1 = [
    [39.110778*10000, -100.495148*10000, 0],
    [39.112409*10000, -100.495191*10000, 0],
    [39.110253*10000, -100.487617*10000, 0]
]

pixel_normals = [0, 0, 0]

vertex_positions_2 = [
    [39.112409*10000, -100.495191*10000, 0],
    [39.112359*10000, -100.487552*10000, 0],
    [39.110253*10000, -100.487617*10000, 0]
]

vertex_normal = [-1, 0, 0]

vertex_texcoord_1 = [[0, 0], [0, 1], [1, 0]]
vertex_texcoord_2 = [[0, 1], [1, 1], [1, 0]]

image = cv2.imread('map.png')


rr.log("bg/1", rr.Mesh3D(
    vertex_positions=vertex_positions_1,
    albedo_texture=image,
    vertex_texcoords=vertex_texcoord_1,
    vertex_normals=vertex_normal
))

rr.log("bg/2", rr.Mesh3D(
    vertex_positions=vertex_positions_2,
    albedo_texture=image,
    vertex_texcoords=vertex_texcoord_2,
    vertex_normals=vertex_normal
))
