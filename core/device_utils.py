"""
디바이스 감지 및 설정 유틸리티
"""

import torch
import os

def get_optimal_device():
    """
    최적의 디바이스를 자동으로 감지
    우선순위: CUDA > CPU
    """
    if torch.cuda.is_available():
        device = "cuda"
        gpu_count = torch.cuda.device_count()
        gpu_name = torch.cuda.get_device_name(0) if gpu_count > 0 else "Unknown"
        print(f"🚀 GPU 감지됨: {gpu_name} (디바이스: {gpu_count}개)")
        return device
    else:
        print("💻 CPU 모드로 실행됩니다")
        return "cpu"

def check_device_compatibility():
    """디바이스 호환성 확인"""
    info = {
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
        "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "current_device": torch.cuda.current_device() if torch.cuda.is_available() else None,
    }

    if torch.cuda.is_available():
        info["gpu_names"] = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
        info["gpu_memory"] = [f"{torch.cuda.get_device_properties(i).total_memory // (1024**3)} GB"
                             for i in range(torch.cuda.device_count())]

    return info

def get_device_from_env():
    """환경변수에서 디바이스 설정 읽기"""
    env_device = os.getenv("EMOTION_DEVICE", "auto")

    if env_device.lower() == "auto":
        return get_optimal_device()
    elif env_device.lower() in ["cuda", "gpu"] and torch.cuda.is_available():
        return "cuda"
    else:
        return "cpu"