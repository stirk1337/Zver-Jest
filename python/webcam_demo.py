import argparse
from email.policy import default
import time
from collections import deque
from operator import itemgetter
from threading import Thread
import os
from sys import platform

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

import cv2
import numpy as np
from model import Predictor
from omegaconf import OmegaConf
from einops import rearrange
import json

FONTFACE = cv2.FONT_HERSHEY_COMPLEX
FONTSCALE = 0.8
FONTCOLOR = (255, 255, 255)  # BGR, white
MSGCOLOR = (128, 128, 128)  # BGR, gray
THICKNESS = 1
LINETYPE = 1

EXCLUED_STEPS = [
    'OpenCVInit', 'OpenCVDecode', 'DecordInit', 'DecordDecode', 'PyAVInit',
    'PyAVDecode', 'RawFrameDecode', 'FrameSelector'
]


def parse_args():
    parser = argparse.ArgumentParser(description='MMAction2 webcam demo')
    parser.add_argument('--config_path', default='config.json', help='model config')
    parser.add_argument(
        '--device', type=str, default='cpu', help='CPU/CUDA device option')
    parser.add_argument(
        '--camera-id', type=int, default=0, help='camera device id')
    parser.add_argument(
        '--sample-length',
        type=int,
        default=32,
        help='len of frame queue')
    parser.add_argument(
        '--drawing-fps',
        type=int,
        default=20,
        help='Set upper bound FPS value of the output drawing')
    parser.add_argument(
        '--inference-fps',
        type=int,
        default=4,
        help='Set upper bound FPS value of model inference')
    parser.add_argument(
        '--openvino',
        action='store_true',
        help='Use OpenVINO backend for inference. Available only on Linux')
    args = parser.parse_args()
    return args


def init_model(config_path):
    """
    Initialize the model using the provided configuration file.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        Predictor: Initialized instance of the Predictor class.
    """
    try:
        with open(config_path, "r") as read_content:
            config = json.load(read_content)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found at path: {config_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Error decoding the configuration file: {config_path}")

    try:
        cfg = OmegaConf.create(
            {
                "path_to_model": config["model"],
                "path_to_class_list": config["class_list"],
                "threshold": config["threshold"],
                "topk": config["topk"],
            }
        )
        model = Predictor(cfg)
        return model
    except KeyError as e:
        raise KeyError(f"Missing key in configuration file: {e}")
    except ValueError as e:
        raise ValueError(f"Error creating Predictor configuration: {e}")


def show_results(cam_disp):
    args = parse_args()
    print('Press "Esc", "q" or "Q" to exit')
    text_info = {}
    deque_info = {}
    cur_time = time.time()
    preds_queue = deque(maxlen=5)
    while True:
        msg = 'Waiting for action ...'
        _, frame = camera.read()
        #print(frame)
        # last dim is BGR2RGB
        frame_queue.append(np.array(cv2.resize(frame, (224, 224))[:, :, ::-1]))
        #print(frame_queue)
        location_fps = (0, 40)
        if len(result_queue) != 0:
            text_info = {}
            results = result_queue.popleft()

            label = results['labels'][0]
            confidence = results['confidence'][0]

            if len(preds_queue) == 0:
                preds_queue.append(label)
            elif preds_queue[-1] != label and len(preds_queue) != 0:
                preds_queue.append(label)
            location_label = (0, 110)
            text_label = label + ': ' + str(round(confidence, 2))
            text_info[location_label] = text_label
            cv2.putText(frame, text_info[location_label], location_label, FONTFACE, FONTSCALE,
                        FONTCOLOR, THICKNESS, LINETYPE)

        elif len(text_info) != 0:
            for location, text in text_info.items():
                cv2.putText(frame, text, location, FONTFACE, FONTSCALE,
                            FONTCOLOR, THICKNESS, LINETYPE)

        text_fps = f"FPS: {model_fps:.2f}"
        text_info[location_fps] = text_fps
        cv2.putText(frame, text_info[location_fps], location_fps, FONTFACE, FONTSCALE,
                    FONTCOLOR, THICKNESS, LINETYPE)

        deque_location = (1, 450)
        deque_info[deque_location] = " ".join(list(preds_queue))

        for location, text in deque_info.items():
            cv2.rectangle(frame, (0, frame_height), (int(frame_width), int(frame_height)), (255, 255, 255), -1)
            cv2.putText(frame, text, deque_location, FONTFACE, FONTSCALE,
                        FONTCOLOR, THICKNESS, LINETYPE)

        # add frame to dict()
        cam_disp['cam'] = frame

        if args.drawing_fps > 0:
            # add a limiter for actual drawing fps <= drawing_fps
            sleep_time = 1 / args.drawing_fps - (time.time() - cur_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
            cur_time = time.time()


def inference(model):
    args = parse_args()
    score_cache = deque()
    scores_sum = 0

    while True:
        cur_fps_time = time.time()
        cur_windows = []
        while len(cur_windows) == 0:
            if len(frame_queue) == args.sample_length:
                cur_windows = list(np.array(frame_queue))

        model_time = time.time()
        print(f"Inference through the model: {time.time() - model_time}")

        results = model.predict(cur_windows)
        if not results:
            # result_queue.append({'labels': {0: 'no'}, 'confidence': {0: 0.0}})
            pass
        else:
            result_queue.append(results)

        print("results", results)
        print(f"Data + model inference: {time.time() - cur_fps_time}")
        global model_fps
        model_fps = 1 / (time.time() - cur_fps_time)
        print(f"model fps: {model_fps}")


def on_resize(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONUP:
        cv2.resizeWindow('cam', 640, 480)


def main():
    global frame_queue, camera, threshold, \
        data, \
        result_queue, drawing_fps, inference_fps, cam_disp, model_fps
    args = parse_args()
    model_fps = 0
    model = init_model(args.config_path)
    camera = cv2.VideoCapture(args.camera_id)
    global frame_width, frame_height
    frame_width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    data = dict(img_shape=None, modality='RGB', label=-1)

    # use dict() to append frames
    cam_disp = {}
    cam_disp['cam'] = None
    cv2.namedWindow('cam', cv2.WINDOW_NORMAL)
    cv2.setMouseCallback('cam', on_resize)
    try:
        frame_queue = deque(maxlen=args.sample_length)
        result_queue = deque(maxlen=1)
        pw = Thread(target=show_results, args=(cam_disp,), daemon=True)
        pr = Thread(target=inference, args=(model,), daemon=True)
        pw.start()
        pr.start()
        # cv2.imshow works in the main thread
        while True:
            if cam_disp['cam'] is not None:
                cv2.imshow('cam', cam_disp['cam'])
                ch = cv2.waitKey(1)
                if ch == 27 or ch == ord('q') or ch == ord('Q'):
                    break

    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
