#! /usr/bin/env python
"""
I make multiple renderings of Portal.
I am expected to run in the ./starter_kit/packages
"""
import argparse
import cable_robo_mount as rs
import merlict_camera_server
import os
import subprocess
import numpy as np
import json_utils

parser = argparse.ArgumentParser(
    prog="make_images.py",
    description="Renders images of the Portal Cherenkov plenoscope",
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
    default=os.path.join("portal-corporate-identity", "images", "work"),
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
    "--azimuth-deg",
    default=20.0,
    type=float,
)
parser.add_argument(
    "--zenith-distance-deg",
    default=30.0,
    type=float,
)

parser.add_argument("--resolution", type=int, default=1)
parser.add_argument("-d", "--dark", action="store_true")

args = parser.parse_args()
workd_dir = args.work_dir


os.makedirs(workd_dir, exist_ok=True)

scenery_path = os.path.join(workd_dir, "scenery.json")
visual_config_path = os.path.join(workd_dir, "visual_config.json")

ppp = os.path.join(os.path.dirname(visual_config_path), args.sky_dome)
if args.sky_dome != "" and not os.path.isfile(ppp):
    print("Warning: Can not find: ", ppp)

acp_config = {
    "pointing": {
        "azimuth": args.azimuth_deg,
        "zenith_distance": args.zenith_distance_deg,
    },
    "camera": {
        "expected_imaging_system_focal_length": 106.05,
        "expected_imaging_system_aperture_radius": 35.35,
        "max_FoV_diameter_deg": 6.5,
        "hex_pixel_FoV_flat2flat_deg": 0.083333,
        "housing_overhead": 1.1,
        "number_of_paxel_on_pixel_diagonal": 9,
        "sensor_distance_to_principal_aperture_plane": 106.05,
        "offset_position": [0, 0, 0],
        "offset_rotation_tait_bryan": [0, 0, 0],
    },
    "system": {
        "merlict": {
            "hostname": "192.168.56.101",
            "username": "spiros",
            "key_path": "C:\\Users\\Spiros Daglas\\Desktop\\ssh\\spiros",
            "run_path_linux": "/home/spiros/Desktop/run",
            "ray_tracer_propagation_path_linux": "/home/spiros/Desktop/build/mctPropagate",
        },
        "sap2000": {
            "path": "C:\Program Files\Computers and Structures\SAP2000 19\sap2000.exe",
            "working_directory": "C:\\Users\\Spiros Daglas\\Desktop\\SAP2000_working_directory\\example_1",
        },
    },
    "structure_spatial_position": {
        "translational_vector_xyz": [0.0, 0.0, 0.0],
        # not used anymore. created from the tait bryan angle Ry
        "rotational_vector_Rx_Ry_Rz": [0.0, 0.0, 0.0],
    },
    "reflector": {
        "main": {
            "max_outer_radius": 40.8187,
            "min_inner_radius": 2.5,
            "number_of_layers": 3,
            "x_over_z_ratio": 1.66,
            # for truss function always keep it between 1.36 and 2.26
            "security_distance_from_ground": 2.6,
        },
        "optics": {
            "focal_length": 106.05,
            "davies_cotton_over_parabola_ratio": 0.0,
        },
        "facet": {
            "gap_in_between": 0.025,
            "inner_hex_radius": 0.75,  # CTA LST facet size
            "surface_weight": 20.0,
            "actuator_weight": 0.0,
        },
        "material": {
            "specific_weight": 78.5,
            "e_modul": 210e6,
            "yielding_point": 1460000.0,
            "ultimate_point": 1360000.0,
            "security_factor": 1.05,
        },
        "bars": {
            "outer_diameter": 0.10,
            "thickness": 0.0025,
            "imperfection_factor": 0.49,
            "buckling_length_factor": 0.9,
        },
    },
    "tension_ring": {
        "width": 1.1,
        "support_position": 10,
        "material": {
            "specific_weight": 78.5,
            "e_modul": 210e6,
            "yielding_point": 1460000.0,
            "ultimate_point": 1360000.0,
            "security_factor": 1.05,
        },
        "bars": {
            "outer_diameter": 0.081,
            "thickness": 0.005,
            "imperfection_factor": 0.49,
            "buckling_length_factor": 0.9,
        },
    },
    "cables": {
        "material": {
            "e_modul": 95e6,
            # according to Bridon Endurance Dyform 18 PI
            "specific_weight": 89.9,
            # according to Bridon Endurance Dyform 18 PI
            "yielding_point": 1671000.0,
            "ultimate_point": 1671000.0,
            "security_factor": 1.05,
        },
        "cross_section_area": 0.000221,
    },
    "load_scenario": {
        "security_factor": {"dead": 1.00, "live": 1.00, "wind": 1.00},
        "wind": {
            "direction": 0.0,
            # OK
            "speed": 55,
            # m/s.OK
            "terrain_factor": 1,
            # Terrain 1.OK
            "orography_factor": 1,
            # No increase of the wind due to mountains etc.OK
            "K1": 1,
            # Turbulence factor. No accurate information available.OK
            "CsCd": 1.2,
            # usually 1. But our structure very prone to dynamic efects,
            # so Cd very conservative 1.2.OK
            "wind_density": 1.25,
            # wind density.OK
            "cpei": 1.5,
            # according to EC1-4 Z.7.3(freistehende Dächer) und Z. 7.2 Tab.7.4a
            # (big?, although a preciser definition is impossible), OK
        },
        "seismic": {"acceleration": 3.6},
    },
    "star_light_analysis": {
        "photons_per_square_meter": 1000,
        "sensor": {"bin_width_deg": 0.0005, "region_of_interest_deg": 0.5},
        "ground": {"bin_width_m": 0.1},
    },
}

if not os.path.exists(scenery_path):
    geometry = rs.Geometry(acp_config)
    reflector = rs.factory.generate_reflector(geometry)
    out = rs.mctracer_bridge.merlict_json.visual_scenery(reflector)

    if args.dark:
        out["colors"] = [
            {"name": "facet_color", "rgb": [128, 128, 128]},
            {"name": "pale_blue_white", "rgb": [225, 255, 255]},
            {"name": "desert_sand", "rgb": [25, 12, 0]},
            {"name": "concrete_grey", "rgb": [220, 220, 220]},
            {"name": "cable_color", "rgb": [255, 220, 220]},
        ]
    else:
        out["colors"] = [
            {"name": "facet_color", "rgb": [75, 75, 75]},
            {"name": "pale_blue_white", "rgb": [225, 255, 255]},
            {"name": "desert_sand", "rgb": [204, 102, 0]},
            {"name": "concrete_grey", "rgb": [128, 128, 128]},
            {"name": "cable_color", "rgb": [140, 128, 128]},
        ]

    rs.mctracer_bridge.merlict_json.write_json(out, scenery_path)
    json_utils.write(scenery_path, out)

if args.dark:
    sky_dome_color = [0, 0, 0]
else:
    sky_dome_color = [255, 255, 255]

merlict_visual_config = {
    "max_interaction_depth": 41,
    "preview": {"cols": 128, "rows": 72, "scale": 10},
    "snapshot": {
        "cols": 1920,
        "rows": 1080,
        "noise_level": 25,
        "focal_length_over_aperture_diameter": 0.95,
        "image_sensor_size_along_a_row": 0.07,
    },
    "global_illumination": {
        "on": True,
        "incoming_direction": [-0.15, -0.2, 1.0],
    },
    "sky_dome": {"path": args.sky_dome, "color": sky_dome_color},
    "photon_trajectories": {"radius": 0.15},
}

json_utils.write(visual_config_path, merlict_visual_config)


image_general_config = {
    "sensor_size": 0.3,
    "f_stop": 0.95,
    "num_columns": 480 * args.resolution,
    "num_rows": 270 * args.resolution,
    "noise_level": 50,
}

image_configs = {
    "top": {
        "position": [-1.256e00, 0.000e00, 1.200e03],
        "orientation": np.deg2rad([0, -1.800e02, -7.249e01]),
        "object_distance": 1200,
        "field_of_view": np.deg2rad(14),
    },
    "top_total": {
        "position": [-1.256e00, 0.000e00, 1.200e03],
        "orientation": np.deg2rad([0, -1.800e02, 45.0]),
        "object_distance": 1200,
        "field_of_view": np.deg2rad(30),
    },
    "mirror_closeup": {
        "position": [3.609e00, 9.980e01, 1.825e01],
        "orientation": np.deg2rad([0, -8.508e01, 1.032e02]),
        "object_distance": 90,
        "field_of_view": np.deg2rad(44.4),
    },
    "sensor_closeup_mirror_background": {
        "position": [5.431e01, 3.093e00, 1.530e02],
        "orientation": np.deg2rad([0, -1.461e02, 1.726e02]),
        "object_distance": 150,
        "field_of_view": np.deg2rad(5.909e01),
    },
    "side_total_from_distance": {
        "position": [2.182e03, 6.191e02, 8.434e00],
        "orientation": np.deg2rad([0, -8.759e01, -1.959e02]),
        "object_distance": 2300,
        "field_of_view": np.deg2rad(1.063e01),
    },
    "side_from_distance": {
        "position": [2.182e03, 6.191e02, 8.434e00],
        "orientation": np.deg2rad([0, -8.759e01 * 1.008, -1.959e02]),
        "object_distance": 2300,
        "field_of_view": np.deg2rad(1.063e01 * 0.67),
    },
}

server = merlict_camera_server.CameraServer(
    merlict_camera_server_path=args.merlict_camera_server,
    scenery_path=scenery_path,
    visual_config_path=visual_config_path,
)
print("camera-server start")

if args.images is None:
    image_keys = [imgkey for imgkey in image_configs]
else:
    image_keys = args.images.split(",")

for imgkey in image_keys:
    img_stem_path = os.path.join(workd_dir, "{:s}".format(imgkey))
    img_tiff_path = img_stem_path + ".tiff"
    img_jpeg_path = img_stem_path + ".jpg"
    img_json_path = img_stem_path + ".json"
    img_png_path = img_stem_path + ".png"

    if not os.path.exists(img_tiff_path):
        print("camera-server render", img_tiff_path)
        full_config = dict(image_general_config)
        full_config.update(image_configs[imgkey])

        json_utils.write(img_json_path, full_config)
        server.render_image_and_write_to_tiff(
            image_config=full_config,
            path=img_tiff_path,
        )
    if not os.path.exists(img_jpeg_path):
        subprocess.call(["convert", img_tiff_path, img_jpeg_path])

    if not os.path.exists(img_png_path):
        if args.dark:
            background_color = "#000000"
        else:
            background_color = "#ffffff"
        subprocess.call(
            [
                "convert",
                img_tiff_path,
                "-transparent",
                background_color,
                "-gamma",
                "1.33",
                img_png_path,
            ]
        )
print("camera-server done")

server.__exit__()
