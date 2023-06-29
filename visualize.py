import asyncio
from dis import dis
import os
import json

import hashlib
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

'''
Takes in the data from a specific label id and maps it to the proper color for the bounding box
'''
def data_to_colour(data):
    if isinstance(data, str):
        data = bytes(data, "utf-8")
    else:
        data = bytes(data)
    m = hashlib.sha256()
    m.update(data)
    key = int(m.hexdigest()[:8], 16)
    r = ((((key >> 0) & 0xFF) + 1) * 33) % 255
    g = ((((key >> 8) & 0xFF) + 1) * 33) % 255
    b = ((((key >> 16) & 0xFF) + 1) * 33) % 255

    # illumination normalization to 128
    inv_norm_i = 128 * (3.0 / (r + g + b))

    return (int(r * inv_norm_i) / 255, int(g * inv_norm_i) / 255, int(b * inv_norm_i) / 255)

'''
Takes in the path to the rgb image for the background, then it takes bounding box data, the labels and the place to store the visualization. It outputs a colorized bounding box.
'''
def colorize_bbox_2d(rgb_path, data, id_to_labels, file_path):

    rgb_img = Image.open(rgb_path)
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(rgb_img)
    for bbox_2d in data:
        id = bbox_2d["semanticId"]
        color = data_to_colour(id)
        labels = id_to_labels[str(id)]
        rect = patches.Rectangle(
            xy=(bbox_2d["x_min"], bbox_2d["y_min"]),
            width=bbox_2d["x_max"] - bbox_2d["x_min"],
            height=bbox_2d["y_max"] - bbox_2d["y_min"],
            edgecolor=color,
            linewidth=2,
            label=labels,
            fill=False,
        )
        ax.add_patch(rect)

    plt.legend(loc="upper left")

    plt.savefig(file_path)

'''
Takes the depth data and colorizes it.
'''
def colorize_depth(depth_data):
    near = 0.01
    far = 100
    depth_data = np.clip(depth_data, near, far)
    # depth_data = depth_data / far
    depth_data = (np.log(depth_data) - np.log(near)) / (np.log(far) - np.log(near))
    # depth_data = depth_data / far
    depth_data = 1.0 - depth_data

    depth_data_uint8 = (depth_data * 255).astype(np.uint8)

    return Image.fromarray(depth_data_uint8)


'''
Takes the segmentation images, the color for the labels and the output path to visualize the segmentation output
'''

def create_segmentation_legend(segmentation_img, color_to_labels, file_path):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(segmentation_img)

    color_patch_list = []
    for color, labels in color_to_labels.items():
        color_val = eval(color)
        color_patch = patches.Patch(color=[i / 255 for i in color_val], label=labels)
        color_patch_list.append(color_patch)

    ax.legend(handles=color_patch_list)

    plt.savefig(file_path)

rgb_dir = "C:\\Users\\adam\\Desktop\\Omniverse\\Src\\data\\rendered\\V1\\2023-06-29-00-54-00\\Apple\\RenderProduct_Replicator\\rgb"
bbox_dir = "C:\\Users\\adam\\Desktop\\Omniverse\\Src\\data\\rendered\\V1\\2023-06-29-00-54-00\\Apple\\RenderProduct_Replicator\\bounding_box_2d_tight"
vis_out_dir = "C:\\Users\\adam\\Desktop\\Omniverse\\Src\\data\\visualize"

file_number = "0000"

rgb_file_name = "rgb_"+file_number+".png" # to be changed by you
rgb_path = os.path.join(rgb_dir, rgb_file_name)
rgb_image = Image.open(rgb_path)

bbox2d_tight_file_name = "bounding_box_2d_tight_"+file_number+".npy"
data = np.load(os.path.join(bbox_dir, bbox2d_tight_file_name))

# Check for labels
bbox2d_tight_labels_file_name = "bounding_box_2d_tight_labels_"+file_number+".json"
with open(os.path.join(bbox_dir, bbox2d_tight_labels_file_name), "r") as json_data:
    bbox2d_tight_id_to_labels = json.load(json_data)

# colorize and save image
colorize_bbox_2d(rgb_path, data, bbox2d_tight_id_to_labels, os.path.join(vis_out_dir, "bbox2d_"+file_number+"_tight.png"))