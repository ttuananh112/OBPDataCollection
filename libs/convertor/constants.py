FREQ = 10  # 1/delta_time based on recorded data
SCENE_DUR = 5  # in seconds
NUM_TS_PER_SCENE = FREQ * SCENE_DUR
RADIUS_AROUND_AGENT = 50.  # range to get surrounding objects, in meters

ORDERED_COLUMNS = [
    "timestamp",
    "id",
    "object_type",
    "center_x",
    "center_y",
    "heading",
    "status"
]  # a little fixed code here but, based on recorded data, too...

MAX_WORKERS = 5
