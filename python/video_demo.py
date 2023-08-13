import argparse
import json
import os
import cv2
from tqdm import tqdm

from omegaconf import OmegaConf
from model import Predictor



def split_list_into_batches(input_list, stride, window_size=32):
    """
    Splits a given input list into batches of specified window size with a given stride.

    Args:
        input_list (list): The list to be split into batches.
        stride (int): The stride value that determines the step size between batch windows.
        window_size (int, optional): The desired size of each batch window. Default is 32.

    Returns:
        list: A list of batches, each containing elements from the input list according to window size and stride.

    Example:
        input_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        stride = 2
        window_size = 3
        batches = split_list_into_batches(input_list, stride, window_size)
        # Result: [[1, 2, 3], [3, 4, 5], [5, 6, 7], [7, 8, 9]]
    """
    if len(input_list) <= window_size:
        return [input_list]
    else:
        batches = []
        for i in range(0, len(input_list) - window_size -1, stride):
            batches.append(input_list[i:i + window_size])
        return batches

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


def process_frames(frames, model):
    """
    Process the frames using the provided model.

    Args:
        frames (list): List of frames to process.
        model (Predictor): Model instance for frame prediction.

    Returns:
        str: The predicted label for the frames.
    """
    pred_dict = model.predict(frames)
    # take the top-1 label from the dict
    if pred_dict is not None:
        return pred_dict["labels"][0]


def process_video(video_path, config_path, stride=1, window_size=32):
    """
    Process the video frames and generate predictions.

    Args:
        video_path (str): Path to the video file.
        config_path (str): Path to the configuration file.
        stride (int): Stride value (default: 2).
        window_size (int): Number of frames to process at a time (default: 32).

    Returns:
        list: List of predicted labels for each set of frames.
    """
    result = []
    model = init_model(config_path)

    try:
        cap = cv2.VideoCapture(video_path)
    except cv2.error as e:
        raise ValueError(f"Error opening video file: {e}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frames = []

    for i in range(frame_count):
        try:
            frame = cv2.resize(cap.read()[1], (224,224))
            frames.append(frame)
        except cv2.error as e:
            continue

    # if sequence less than window_size copy last frames to extend
    if len(frames) < window_size:
        add_frames_idx = len(frames) - (window_size - len(frames))
        frames += frames[add_frames_idx:]

    cap.release()
    frames = split_list_into_batches(frames, stride, window_size=window_size)
    result = [process_frames(i, model) for i in tqdm(frames) if process_frames(i, model) is not None]
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Process video frames and generate text output."
    )
    parser.add_argument("video_path", type=str, help="Path to the video file")
    parser.add_argument("-c", "--config_path", default="config.json", type=str, help="Path to the configuration file")
    args = parser.parse_args()

    if not os.path.exists(args.video_path):
        raise OSError (f"video_path - {args.video_path} doesnt exist")
    if not os.path.exists(args.config_path):
        raise OSError (f"config_path - {args.config_path} doesnt exist")

    result = process_video(args.video_path, args.config_path, stride=15)
    print(result)
