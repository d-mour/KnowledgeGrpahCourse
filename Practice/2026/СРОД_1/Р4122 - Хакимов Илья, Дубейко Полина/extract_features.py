# скрипт чтобы вытащить из видео и аудио данные: python extract_features.py --audio_dir /path/to/audio --video_dir /path/to/video --output_dir ./data

import argparse
import os
import glob
import re
import json
import numpy as np
import pandas as pd
import librosa
import cv2
from pathlib import Path


def decode_unicode_filename(filename):
    def replace_unicode(match):
        code = match.group(1)
        return chr(int(code, 16))
    return re.sub(r'#U([0-9A-Fa-f]{4})', replace_unicode, filename)


def extract_audio_features(audio_dir):
    ogg_files = sorted(glob.glob(os.path.join(audio_dir, '**/*.ogg'), recursive=True))
    features = []

    for filepath in ogg_files:
        try:
            y, sr = librosa.load(filepath, sr=None)
            duration = float(librosa.get_duration(y=y, sr=sr))
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            mfcc_mean = float(np.mean(mfcc))
            zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)))
            spec_cent = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))

            rel_path = os.path.relpath(filepath, audio_dir)
            parts = rel_path.split('/')
            speaker = parts[0]
            speaker_id = parts[1]
            device = parts[2]
            cmd_filename = decode_unicode_filename(os.path.basename(filepath))
            command_file = cmd_filename.replace('.ogg', '')

            features.append({
                'file_path': f"audio/{speaker}/{speaker_id}/{device}/{command_file}.ogg",
                'speaker': speaker,
                'speaker_id': int(speaker_id),
                'gender': 'male' if speaker == 'man' else 'female',
                'device': device,
                'command_file': command_file,
                'duration_sec': round(duration, 3),
                'sample_rate': sr,
                'mfcc_mean': round(mfcc_mean, 2),
                'zero_crossing_rate': round(zcr, 4),
                'spectral_centroid': round(spec_cent, 2),
            })
        except Exception as e:
            print(f"ошибка при обработке аудио {filepath}: {e}")

    return features


def extract_video_features(video_dir):
    webm_files = sorted(glob.glob(os.path.join(video_dir, '**/*.webm'), recursive=True))
    features = []

    for filepath in webm_files:
        try:
            cap = cv2.VideoCapture(filepath)
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = round(frame_count / fps, 2) if fps > 0 else 0

            rel_path = os.path.relpath(filepath, video_dir)
            parts = rel_path.split('/')
            speaker = parts[0]
            speaker_id = parts[1]
            device = parts[2]

            decoded_basename = decode_unicode_filename(os.path.basename(filepath))
            basename_no_ext = decoded_basename.replace('.webm', '')
            gesture_type, camera_angle = basename_no_ext.split('_')

            frames = []
            prev_gray = None
            gesture_start = None
            gesture_end = None
            gesture_active = False
            frame_idx = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                timestamp = round(frame_idx / fps, 3) if fps > 0 else 0
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                if prev_gray is not None:
                    diff = cv2.absdiff(gray, prev_gray)
                    motion_score = float(np.mean(diff))
                    is_active = motion_score > 5.0

                    if is_active:
                        _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        if contours:
                            all_points = np.vstack([cnt for cnt in contours if cv2.contourArea(cnt) > 100])
                            if len(all_points) > 0:
                                x, y, w, h = cv2.boundingRect(all_points)
                                x = max(0, min(x, width - 1))
                                y = max(0, min(y, height - 1))
                                w = min(w, width - x)
                                h = min(h, height - y)
                                confidence = min(0.99, 0.7 + motion_score / 200)
                            else:
                                x, y, w, h = 0, 0, 0, 0
                                confidence = 0.0
                        else:
                            x, y, w, h = 0, 0, 0, 0
                            confidence = 0.0
                    else:
                        x, y, w, h = 0, 0, 0, 0
                        confidence = 0.0

                    if is_active and not gesture_active:
                        gesture_start = timestamp
                    if is_active:
                        gesture_end = timestamp
                    gesture_active = is_active

                    frames.append({
                        'frame_id': frame_idx,
                        'timestamp': timestamp,
                        'gesture_active': is_active,
                        'bbox': {'x': int(x), 'y': int(y), 'width': int(w), 'height': int(h)},
                        'confidence': round(confidence, 3),
                        'keypoints': []
                    })
                else:
                    frames.append({
                        'frame_id': frame_idx,
                        'timestamp': timestamp,
                        'gesture_active': False,
                        'bbox': {'x': 0, 'y': 0, 'width': 0, 'height': 0},
                        'confidence': 0.0,
                        'keypoints': []
                    })

                prev_gray = gray
                frame_idx += 1

            cap.release()

            features.append({
                'file_path': f"video/{speaker}/{speaker_id}/{device}/{basename_no_ext}.webm",
                'speaker': speaker,
                'speaker_id': int(speaker_id),
                'device': device,
                'gesture_type': gesture_type,
                'camera_angle': camera_angle,
                'duration_sec': duration,
                'fps': round(fps, 1),
                'frame_count': frame_count,
                'resolution': {'width': width, 'height': height},
                'gesture_start_sec': round(gesture_start, 2) if gesture_start else 0,
                'gesture_end_sec': round(gesture_end, 2) if gesture_end else duration,
                'frames': frames,
            })

        except Exception as e:
            print(f"ошибка при обработке видео {filepath}: {e}")

    return features


def main():
    parser = argparse.ArgumentParser(description='извелкаем признаки из аудио/видео')
    parser.add_argument('--audio_dir', default='data/audio', help='путь к аудио')
    parser.add_argument('--video_dir', default='data/video', help='путь к видео')
    parser.add_argument('--output_dir', default='data', help='выходная пдиректория')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    print("шаг 1 - извлекаем аудио фичи с помощью librosa...")
    audio_features = extract_audio_features(args.audio_dir)
    print(f"всего {len(audio_features)} аудио")

    audio_df = pd.DataFrame(audio_features)
    audio_path = os.path.join(args.output_dir, 'audio_features_real.csv')
    audio_df.to_csv(audio_path, index=False, encoding='utf-8')
    print(f"сохранено {audio_path}")

    print("шаг 2 - извлекаем видео фичи с помощью ffmpeg...")
    video_features = extract_video_features(args.video_dir)
    print(f"всего {len(video_features)} video files")

    video_path = os.path.join(args.output_dir, 'video_features_real.json')
    with open(video_path, 'w', encoding='utf-8') as f:
        json.dump(video_features, f, ensure_ascii=False, indent=2)
    print(f"сохранено {video_path}")


if __name__ == '__main__':
    main()
