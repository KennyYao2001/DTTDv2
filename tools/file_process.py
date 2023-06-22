import zipfile
import re
import glob
import subprocess
import shutil
import os, sys
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(dir_path, ".."))
from utils.constants import SCENES_DIR, EXTRINSICS_DIR
from utils.datetime_utils import get_latest_str_from_str_time_list


import argparse

def main():
    parser = argparse.ArgumentParser(description='extract zip file and process the input raw data')
    parser.add_argument('--scene_name', type=str, help='name of scene')
    parser.add_argument('--extrinsic', default=False, action="store_true", help='processing a extrinsic scene')
    args = parser.parse_args()

    if not args.scene_name and not args.extrinsic:
        print("Must be a scene capture (indicate a scene_name) or an extrinsic capture (use --extrinsic flag).")
        exit(-1)

    if args.extrinsic and args.scene_name:
        scene_dir = os.path.join(EXTRINSICS_DIR, args.scene_name)
    elif args.extrinsic:
        extrinsic_scenes = list(os.listdir(EXTRINSICS_DIR))
        latest_extrinsic_scene = get_latest_str_from_str_time_list(extrinsic_scenes)

        print("using extrinsic scene {0}".format(latest_extrinsic_scene))
        
        scene_dir = os.path.join(EXTRINSICS_DIR, latest_extrinsic_scene)
    else:
        scene_dir = os.path.join(SCENES_DIR, args.scene_name)
    target_directory = os.path.join(scene_dir, 'iphone_data')

    # Regular expression patterns for matching files
    zip_pattern = re.compile(r'\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}\.zip')
    csv_pattern = re.compile(r'^Take.*\.csv')

    # Find zip files in the scene_dir directory that match the pattern
    for file in glob.glob(os.path.join(scene_dir, '*.zip')):
        if zip_pattern.match(os.path.basename(file)):
            # Open the zip file and extract its contents to the scene_dir
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall(scene_dir)

            # Get the name of the extracted folder
            extracted_folder = os.path.join(scene_dir, zip_ref.namelist()[0].split('/')[0])

            # Rename the extracted folder to 'iphone_data'
            if not os.path.exists(target_directory):
                os.rename(extracted_folder, target_directory)
            else:
                shutil.rmtree(target_directory)
                os.rename(extracted_folder, target_directory)

            print(f"Contents of '{file}' have been extracted to the '{target_directory}' directory.")

    # Rename and move the CSV file
    for file in glob.glob(os.path.join(scene_dir, '*.csv')):
        if csv_pattern.match(os.path.basename(file)):
            camera_poses_dir = os.path.join(scene_dir, 'camera_poses')
            if not os.path.exists(camera_poses_dir):
                os.makedirs(camera_poses_dir)
            shutil.move(file, os.path.join(camera_poses_dir, 'camera_poses.csv'))
            print(f"CSV file '{file}' has been renamed and moved to '{camera_poses_dir}/camera_poses.csv'.")

    # Move timestamps.csv from iphone_data to scene_dir
    timestamps_src = os.path.join(target_directory, 'timestamps.csv')
    if os.path.exists(timestamps_src):
        shutil.move(timestamps_src, os.path.join(scene_dir, 'timestamps.csv'))
        print(f"File 'timestamps.csv' has been moved to '{scene_dir}'.")

    if args.extrinsic:
            # Execute the provided command
        cmd1 = f"python .\\tools\\process_iphone_data.py iphone14pro_camera1 --depth_type ARKit --scene_name {args.scene_name} --extrinsic"
        subprocess.run(cmd1, shell=True, check=True)

        cmd2 = f"python .\\tools\\process_data.py --scene_name {args.scene_name} --extrinsic"
        subprocess.run(cmd2, shell=True, check=True)

        cmd3 = f" python .\\tools\\calculate_camera_extrinsic.py --scene_name {args.scene_name}"
        subprocess.run(cmd3, shell=True, check=True)


    else:
        # Execute the provided command
        cmd1 = f"python .\\tools\\process_iphone_data.py iphone14pro_camera1 --depth_type ARKit --scene_name {args.scene_name}"
        subprocess.run(cmd1, shell=True, check=True)

        cmd2 = f"python .\\tools\\process_data.py --scene_name {args.scene_name}"
        subprocess.run(cmd2, shell=True, check=True)
        print("PLEASE fill the objects field in the scene_meta!!!")
if __name__ == "__main__":
    main()

