"""
GPU 기능 테스트 스크립트
"""

from core.device_utils import check_device_compatibility, get_device_from_env
import sys

def test_gpu_functionality():
    print("=== GPU 기능 테스트 ===\n")

    try:
        import torch
        print(f"✅ PyTorch 가져오기 성공: {torch.__version__}")
    except ImportError as e:
        print(f"❌ PyTorch 가져오기 실패: {e}")
        return False

    # 디바이스 정보 확인
    device_info = check_device_compatibility()
    print("\n📊 디바이스 정보:")
    for key, value in device_info.items():
        print(f"   {key}: {value}")

    # 자동 디바이스 선택 테스트
    selected_device = get_device_from_env()
    print(f"\n🎯 선택된 디바이스: {selected_device}")

    # 간단한 텐서 연산 테스트
    try:
        import torch
        device = torch.device(selected_device)
        test_tensor = torch.randn(3, 3).to(device)
        result = test_tensor @ test_tensor.T
        print(f"✅ {selected_device}에서 텐서 연산 성공!")
        print(f"   텐서 크기: {test_tensor.shape}")
        print(f"   디바이스: {test_tensor.device}")
    except Exception as e:
        print(f"❌ 텐서 연산 실패: {e}")
        return False

    # GPU 메모리 정보 (CUDA인 경우)
    if selected_device == "cuda":
        try:
            total_memory = torch.cuda.get_device_properties(0).total_memory
            allocated_memory = torch.cuda.memory_allocated()
            cached_memory = torch.cuda.memory_reserved()

            print(f"\n💾 GPU 메모리 정보:")
            print(f"   전체: {total_memory // (1024**3)} GB")
            print(f"   할당됨: {allocated_memory // (1024**2)} MB")
            print(f"   예약됨: {cached_memory // (1024**2)} MB")
        except Exception as e:
            print(f"⚠️ GPU 메모리 정보 조회 실패: {e}")

    return True

if __name__ == "__main__":
    success = test_gpu_functionality()
    if success:
        print("\n🎉 GPU 테스트 완료! 모든 기능이 정상 작동합니다.")
    else:
        print("\n❌ GPU 테스트 실패. 환경을 확인해주세요.")
        sys.exit(1)