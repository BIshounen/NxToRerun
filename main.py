import rerun as rr
import json
from collections import defaultdict

from pathlib import Path

METADATA_PATH = "metadata.json"
IMAGE_PATH = "map.png"

rr.init("rerun_test_cars")

rr.serve_web(open_browser=True)

image_file_path = Path(__file__).parent / IMAGE_PATH

with open(METADATA_PATH, 'r') as f:
    metadata = json.load(f)


timeline_start = 0
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
            latitudes.append(attribute['value'])
        if attribute['name'] == 'pos_longitude':
            longitudes.append(attribute['value'])
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
        box_centers = [[latitudes[i], longitudes[i], 0]]
        color = (0, 255, 0) if object_type == 'car' else (255, 0, 0)
        (rr.log(
            f"vehicles/{object_type}/{track['id']}",
            rr.Boxes3D(half_sizes=[0.01,0.01,0.01], centers=box_centers, fill_mode="solid", colors=[color]))
        )
        current_time += (max_time - min_time)/num_of_steps
        i += 1

    rr.set_time_seconds("stable_time", current_time / 1000)
    rr.log(f"vehicles/{object_type}/{track['id']}", rr.Clear(recursive=True))

rr.set_time_seconds("stable_time", timeline_start/1000)

rr.log('background', rr.EncodedImage(path=image_file_path))
