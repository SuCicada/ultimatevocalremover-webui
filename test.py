import os
import json
import sys
import tempfile

import librosa
import sounddevice
import soundfile
import numpy as np
import argparse

import gradio as gr
from UVR_interface import root, UVRInterface, VR_MODELS_DIR, MDX_MODELS_DIR, DEMUCS_MODELS_DIR
from gui_data.constants import *
from typing import List, Dict, Callable, Union

uvr = UVRInterface()
uvr.cached_sources_clear()


def set_arch_setting_value(arch: str, setting1, setting2):
    if arch == VR_ARCH_TYPE:
        root.window_size_var.set(setting1)
        root.aggression_setting_var.set(setting2)
    elif arch == MDX_ARCH_TYPE:
        root.mdx_batch_size_var.set(setting1)
        root.compensate_var.set(setting2)
    elif arch == DEMUCS_ARCH_TYPE:
        pass


def process(input_filename, model_name, arch, setting1, setting2):
    # def set_progress_func(step, inference_iterations=0):
    #     progress_curr = step + inference_iterations
    #     progress(progress_curr)
    audio, sampling_rate = librosa.load(input_filename)
    # sampling_rate, audio = input_audio
    if audio.dtype == np.float32 or audio.dtype == np.float64:
        # No need to normalize if already in floating-point format
        audio = audio.astype(np.float32)
    else:
        audio = (audio / np.iinfo(audio.dtype).max).astype(np.float32)
    if len(audio.shape) > 1:
        audio = librosa.to_mono(audio.transpose(1, 0))
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        input_path = temp_file.name  # os.path.join(temp_file, input_filename)
        soundfile.write(input_path, audio, sampling_rate, format="wav")

    set_arch_setting_value(arch, setting1, setting2)

    export_path = os.path.join(tempfile.gettempdir(), "uvr")
    seperator = uvr.process(
        model_name=model_name,
        arch_type=arch,
        audio_file=input_path,
        export_path=export_path,
        is_model_sample_mode=root.model_sample_mode_var.get(),
        set_progress_func=None,
    )

    primary_audio = None
    secondary_audio = None
    msg = ""
    if not seperator.is_secondary_stem_only:
        primary_stem_path = os.path.join(seperator.export_path,
                                         f"{seperator.audio_file_base}_({seperator.primary_stem}).wav")
        audio, rate = soundfile.read(primary_stem_path)
        primary_audio = (rate, audio)
        msg += f"{seperator.primary_stem} saved at {primary_stem_path}\n"
    if not seperator.is_primary_stem_only:
        secondary_stem_path = os.path.join(seperator.export_path,
                                           f"{seperator.audio_file_base}_({seperator.secondary_stem}).wav")
        audio, rate = soundfile.read(secondary_stem_path)
        secondary_audio = (rate, audio)
        msg += f"{seperator.secondary_stem} saved at {secondary_stem_path}\n"

    os.remove(input_path)

    return primary_audio, secondary_audio, msg


input_dir = sys.argv[1]
output_dir = sys.argv[2]

files = os.listdir(input_dir)
for file in files:
    input_path = os.path.join(input_dir, file)
    output_path = os.path.join(output_dir, file)
    primary_audio, secondary_audio, msg = process(
        input_path, "UVR-De-Echo-Aggressive", "VR Arc", 320, 10
    )
    sampling_rate, numpy_array = primary_audio
    soundfile.write(output_path, numpy_array, sampling_rate, format="wav")

# primary_audio, secondary_audio, msg = process(
# "/Users/peng/PROGRAM/GitHub/GPT-SoVITS/data/lain/Cou014_Sometimes it happens when Im all by myself, and sometimes when Im talking to my friends._0.wav",
#         "UVR-De-Echo-Aggressive", "VR Arc", 320, 10
# )
# sampling_rate, numpy_array = primary_audio
# # sounddevice.play(numpy_array, sampling_rate, blocking=True)
# # sampling_rate, numpy_array = secondary_audio
#
# soundfile.write(input_path, numpy_array, sampling_rate, format="wav")
#

# sounddevice.play(numpy_array, sampling_rate, blocking=True)

# from pydub import AudioSegment
# # from pydub.playback import play as pydub_play
# audio = AudioSegment.from_file()
# import pydub.playback
# pydub.playback.play(secondary_audio)
