import torch

print("--- GPU Verification ---")
is_cuda_available = torch.cuda.is_available()
print(f"Is CUDA (GPU) available? {is_cuda_available}")

if is_cuda_available:
    gpu_count = torch.cuda.device_count()
    print(f"Number of GPUs available: {gpu_count}")
    gpu_name = torch.cuda.get_device_name(0)
    print(f"GPU Name: {gpu_name}")
else:
    print("PyTorch cannot see your GPU. Make sure you installed the CUDA-enabled version and your NVIDIA drivers are up to date.")