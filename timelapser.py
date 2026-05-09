import obspython as obs

import subprocess
import shlex
import glob
import os
from os import path

tag = "[Timelapser]"

default_input_fps = 1
default_input_ext = ".mkv"
default_output_fps = 10
default_output_ext = ".timelapse.mp4"

input_fps = default_input_fps
input_ext = default_input_ext
output_fps = default_output_fps
output_ext = default_output_ext


def on_recording_stop(calldata):
    file_types = "*" + input_ext
    output_dir = obs.obs_frontend_get_current_record_output_path()
    files = glob.glob(path.join(output_dir, file_types))
    latest_file = max(files, key=path.getctime)

    name, ext = path.splitext(path.basename(latest_file))
    ffmpeg_input_file = shlex.quote(latest_file)
    ffmpeg_output_file = shlex.quote(path.join(output_dir, name + output_ext))
    ffmpeg_pts = input_fps / output_fps

    print(f"{tag} Creating timelapse from file:\n\t{ffmpeg_input_file}")

    ffmpeg_args = [
        "ffmpeg",
        "-xerror",
        "-i",
        ffmpeg_input_file,
        "-filter:v",
        f"'setpts={ffmpeg_pts}*PTS'",
        "-r",
        str(output_fps),
        "-an",
        ffmpeg_output_file,
    ]
    ffmpeg_exit_code = os.system(" ".join(ffmpeg_args))

    match ffmpeg_exit_code:
        case 0:
            print(f"{tag} Timelapse saved:\n\t{ffmpeg_output_file}")
        case _:
            print(
                f"{tag} Failed to create timelapse. FFmpeg error code: {ffmpeg_exit_code}"
            )


def main():
    sh = obs.obs_output_get_signal_handler(obs.obs_frontend_get_recording_output())
    obs.signal_handler_connect(sh, "stop", on_recording_stop)


def script_update(settings):
    input_fps = obs.obs_data_get_int(settings, "input_fps")
    input_ext = obs.obs_data_get_string(settings, "input_ext")
    output_fps = obs.obs_data_get_int(settings, "output_fps")
    output_ext = obs.obs_data_get_string(settings, "output_ext")
    print(
        f"""{tag} Settings updated:
    input_fps: {input_fps}
    input_ext: {input_ext}
    output_fps: {output_fps}
    output_ext: {output_ext}"""
    )


def script_description():
    return """When recording stops, automatically create a timelapse using FFmpeg.

Input settings must be adjusted to match your current recording profile."""


def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_int(
        props, "input_fps", "Input FPS", default_input_fps, 1000, 1
    )
    obs.obs_properties_add_text(
        props, "input_ext", "Input Extension", obs.OBS_TEXT_DEFAULT
    )
    obs.obs_properties_add_int(
        props, "output_fps", "Output FPS", default_output_fps, 10000, 1
    )
    obs.obs_properties_add_text(
        props, "output_ext", "Output Extension", obs.OBS_TEXT_DEFAULT
    )

    return props


def script_defaults(settings):
    obs.obs_data_set_default_int(settings, "input_fps", default_input_fps)
    obs.obs_data_set_default_string(settings, "input_ext", default_input_ext)
    obs.obs_data_set_default_int(settings, "output_fps", default_output_fps)
    obs.obs_data_set_default_string(settings, "output_ext", default_output_ext)


main()
