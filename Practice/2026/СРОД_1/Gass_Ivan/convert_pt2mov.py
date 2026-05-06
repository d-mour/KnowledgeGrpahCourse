import torch
import imageio
import os


def save_video_with_imageio(tensor, file_path, fps=30):
    """
    Сохраняет видео из тензора PyTorch, используя imageio.
    Это простой и надежный способ.
    """
    print(f"Исходная форма тензора: {tensor.shape}")

    # 1. Приводим тензор к формату [T, H, W, C] (Time, Height, Width, Channels)
    # Если ваш тензор в формате [T, C, H, W], что верно для вашего случая
    if tensor.dim() == 4 and tensor.shape[1] == 3:
        # Меняем местами оси: из [T, C, H, W] в [T, H, W, C]
        tensor = tensor.permute(0, 2, 3, 1)
        print(f"После преобразования в [T, H, W, C]: {tensor.shape}")

    # 2. Преобразуем в numpy и меняем тип данных, если нужно
    # imageio ожидает массив numpy с значениями от 0 до 255 и типом uint8
    if tensor.max() <= 1.0:
        tensor_np = (tensor * 255).to(torch.uint8).cpu().numpy()
    else:
        tensor_np = tensor.to(torch.uint8).cpu().numpy()

    # 3. Сохраняем видео
    imageio.mimsave(file_path, tensor_np, fps=fps)
    print(f"✓ Видео успешно сохранено как '{file_path}' с помощью imageio")


# --- Пример использования с вашим тензором ---
# Создаем тестовый тензор в формате [T, C, H, W] (100 кадров, 3 канала, 256x256)
paths = ["id_0", "id_40", "id_60"]

for path in paths:
    tensor = torch.load(path + "/sparse_weight.pt").to_dense()

    tensor /= tensor.abs().max()
    tensor *= 255
    print(tensor.size())
    save_video_with_imageio(tensor, f'sparse_weight_{path}.mp4', fps=30)
