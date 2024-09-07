#! /usr/bin/env python

import argparse
import os
import subprocess
import numpy as np

parser = argparse.ArgumentParser(
    prog="make_pointing_sweep.py",
    description=(
        "Renders an image sequence of the Portal Cherenkov plenoscope "
        "while pointing"
    ),
)
parser.add_argument(
    "--merlict-camera-server",
    default=os.path.join(
        "build", "merlict_development_kit", "merlict-cameraserver"
    ),
    type=str,
)
parser.add_argument(
    "--work-dir",
    default=os.path.join("portal-corporate-identity", "images", "pointing"),
    type=str,
)
parser.add_argument(
    "--make_images",
    default=os.path.join(
        "portal-corporate-identity", "images", "make_images.py"
    ),
    type=str,
)
parser.add_argument(
    "--sky-dome",
    default="",
    type=str,
)
parser.add_argument(
    "--images",
    default=None,
    type=str,
)
parser.add_argument(
    "--steps",
    default=30,
    type=int,
)
parser.add_argument(
    "--azimuth-deg",
    default=20.0,
    type=float,
)
parser.add_argument("--resolution", type=int, default=1)
parser.add_argument("-d", "--dark", action="store_true")

image_key = "side_from_distance"

args = parser.parse_args()
workd_dir = args.work_dir

os.makedirs(workd_dir, exist_ok=True)

zenith_distances_deg = np.linspace(-45, 45, args.steps)

for i_zd in range(len(zenith_distances_deg)):
    i_work_dir = os.path.join(workd_dir, f"{i_zd:06d}")

    call = [
        args.make_images,
        "--merlict-camera-server",
        args.merlict_camera_server,
        "--work-dir",
        i_work_dir,
        "--azimuth-deg",
        f"{args.azimuth_deg:f}",
        "--zenith-distance-deg",
        f"{zenith_distances_deg[i_zd]:f}",
        "--sky-dome",
        args.sky_dome,
        "--images",
        image_key,
        "--resolution",
        f"{args.resolution:d}",
    ]
    if args.dark:
        call += ["--dark"]

    subprocess.call(call)
    os.remove(os.path.join(i_work_dir, "scenery.json"))

    for ext in [".tiff", ".png", ".jpg"]:
        os.rename(
            os.path.join(i_work_dir, image_key + ext),
            os.path.join(workd_dir, f"{image_key:s}_{i_zd:06d}{ext:s}"),
        )
