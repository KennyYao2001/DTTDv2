import argparse
import cv2
import numpy as np
import copy
from tqdm import tqdm
import yaml
import json

import os, sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, ".."))

from utils.constants import AZURE_KINECT_COLOR_HEIGHT, AZURE_KINECT_COLOR_WIDTH, SCENES_DIR, IPHONE_COLOR_HEIGHT, IPHONE_COLOR_WIDTH
from utils.frame_utils import load_bgr, load_label

size = (IPHONE_COLOR_WIDTH //2, IPHONE_COLOR_HEIGHT//2)

def main():
    parser = argparse.ArgumentParser(description='Manually, check annotation')
    parser.add_argument('scene_name', type=str, help='scene directory (contains scene_meta.yaml and data (frames) and camera_poses)')

    args = parser.parse_args()

    scene_dir = os.path.join(SCENES_DIR, args.scene_name)
    frames_dir = os.path.join(scene_dir, "data")

    scene_metadata_file = os.path.join(scene_dir, "scene_meta.yaml")
    with open(scene_metadata_file, 'r') as file:
        scene_metadata = yaml.safe_load(file)

    num_frames = scene_metadata["num_frames"]

    # Create a list to save the selected frames
    save_frames_ids = []

    data_dir = os.path.join(scene_dir, "data")

    for frame_id in tqdm(range(num_frames), total=num_frames):
        color_img = load_bgr(frames_dir, frame_id, "jpg")
        label = load_label(frames_dir, frame_id)

        out = copy.deepcopy(color_img)

        label = label > 0

        out[:, :, 2] = label[:,:]*255 + (1-label[:,:])*color_img[:,:,2]

        out_resized = cv2.resize(out, size)  # resize for display


        cv2.imshow('Image and Label', out_resized)
        key = cv2.waitKey(0) # wait for user input

        if key == ord(','):  # ',' key
            save_frames_ids.append(frame_id)

        elif key == ord('.'):  # '.' key
            continue

        elif key == 27:  # ESC key
            break

    cv2.destroyAllWindows()
    with open(os.path.join(scene_dir, 'saved_frame_ids.json'),'w') as file:
        json.dump(save_frames_ids, file)
    print("the portion of the saved frame is ", len(save_frames_ids), '/',num_frames, '=', len(save_frames_ids)/num_frames)

""" with open(os.path.join(scene_dir, 'saved_frame_ids.json'),'r') as file:
        checked_ids = json.load(file)
    print(checked_ids)
    ids = [x[:x.find("_")] for x in list(os.listdir(data_dir)) if "meta.json" in x]
    ids = [ids[i] for i in checked_ids]
    print(ids)"""


    
if __name__ == "__main__":
    main()