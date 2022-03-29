#! /usr/bin/env python
"""
I make multiple renderings of Portal.
I am expected to run in the ./starter_kit
"""
import cable_robo_mount as rs
import merlict_camera_server
import os
import subprocess
import numpy as np
import json_numpy

MERLICT_CAMERA_SERVER = os.path.join(
    "build", "merlict", "merlict-cameraserver"
)
WORKD_DIR = os.path.join("portal-corporate-identity", "images", "work")
SCENERY_PATH = os.path.join(WORKD_DIR, "scenery.json")
VISUAL_CONFIG_PATH = os.path.join(WORKD_DIR, "visual_config.json")

os.makedirs(WORKD_DIR, exist_ok=True)

acp_config = {
    "pointing": {"azimuth": 20.0, "zenith_distance": 30.0,},
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
            "cpei": 1.5
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

if not os.path.exists(SCENERY_PATH):
    geometry = rs.Geometry(acp_config)
    reflector = rs.factory.generate_reflector(geometry)
    out = rs.mctracer_bridge.merlict_json.visual_scenery(reflector)
    rs.mctracer_bridge.merlict_json.write_json(out, SCENERY_PATH)
    json_numpy.write(SCENERY_PATH, out)


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
    "sky_dome": {"path": "", "color": [255, 255, 255]},
    "photon_trajectories": {"radius": 0.15},
}

json_numpy.write(VISUAL_CONFIG_PATH, merlict_visual_config)

image_general_config = {
    "sensor_size": 0.3,
    "f_stop": 0.95,
    "num_columns": 512 * 2,
    "num_rows": 288 * 2,
    "noise_level": 200,
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
}

server = merlict_camera_server.CameraServer(
    merlict_camera_server_path=MERLICT_CAMERA_SERVER,
    scenery_path=SCENERY_PATH,
    visual_config_path=VISUAL_CONFIG_PATH,
)
print("camera-server start")

for imgkey in image_configs:
    img_stem_path = os.path.join(WORKD_DIR, "{:s}".format(imgkey))
    img_tiff_path = img_stem_path + ".tiff"
    img_jpeg_path = img_stem_path + ".jpg"
    img_json_path = img_stem_path + ".json"

    if not os.path.exists(img_tiff_path):
        print("camera-server render", img_tiff_path)
        full_config = dict(image_general_config)
        full_config.update(image_configs[imgkey])

        json_numpy.write(img_json_path, full_config)
        server.render_image_and_write_to_tiff(
            image_config=full_config, path=img_tiff_path,
        )
        subprocess.call(["convert", img_tiff_path, img_jpeg_path])
print("camera-server done")

server.__exit__()
