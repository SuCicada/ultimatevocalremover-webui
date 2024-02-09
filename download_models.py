import os
import subprocess
from typing import Dict
from gui_data.constants import *
import json5
import wget


def get_models_url(models_info_path: str) -> Dict[str, Dict]:
    with open(models_info_path, "r") as f:
        online_data = json5.loads(f.read())
    models_url = {}
    for arch, download_list_key in zip([VR_ARCH_TYPE, MDX_ARCH_TYPE], ["vr_download_list", "mdx_download_list"]):
        models_url[arch] = {model: NORMAL_REPO + model_path for model, model_path in
                            online_data[download_list_key].items()}
    return models_url


def exec_cmd(cmd):
    # 使用Popen执行命令
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    # 实时输出命令的执行结果
    for line in process.stdout:
        print(line.strip())
    # 等待命令执行完毕并获取返回码
    return process.wait()


model_dict = get_models_url('models/download_checks.json5')

for category, models in model_dict.items():
    if category in ['VR Arc', 'MDX-Net', 'Demucs']:
        if category == 'VR Arc':
            model_path = 'models/VR_Models'
        elif category == 'MDX-Net':
            model_path = 'models/MDX_Net_Models'
        for model_name, model_url in models.items():
            cmd = f"aria2c --optimize-concurrent-downloads --console-log-level=error --summary-interval=10 -j5 -x16 -s16 -k1M -c -d {model_path} -Z {model_url}"
            print(cmd)
            exec_cmd(cmd)

        print("Models downloaded successfully.")
