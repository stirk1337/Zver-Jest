import json

import numpy as np
import onnxruntime as rt
from einops import rearrange
from sys import platform

from omegaconf import OmegaConf


def decode_preds(data):
    if platform == 'win32' or platform == 'win64':
        data = [i.encode('cp1251').decode('utf-8') for i in data]
    return data


class Predictor:
    def __init__(self, model_config, model_type="S3D"):
        """
        Initialize the Predictor class.

        Args:
            model_config (dict): Model configuration containing path_to_model,
                path_to_class_list, threshold, and topk values.
        """
        self.config = model_config
        self.model_type = model_type
        self.model_run(self.config["path_to_model"])

        with open(self.config["path_to_class_list"], "r") as f:
            labels = [line.strip() for line in f]
            labels = decode_preds(labels)

            idx_lbl_pairs = [x.split("\t") for x in labels]
            self.labels = {int(x[0]): x[1] for x in idx_lbl_pairs}

        self.threshold = self.config["threshold"]

    def softmax(self, x):
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)

    def predict(self, x):
        """
        Make a prediction using the provided input frames.

        Args:
            x (list): List of input frames.

        Returns:
            dict: Dictionary containing predicted labels and confidence values.
        """
        clip = np.array(x).astype(np.float32) / 255.0
        print(len(x))
        if self.model_type == "S3D":
            clip = rearrange(clip, "t h w c -> 1 c t h w")
        else:
            clip = rearrange(clip, "t h w c -> 1 1 c t h w")

        prediction = self.model([self.output_name], {self.input_name: clip})[0]
        prediction = self.softmax(prediction)
        prediction = np.squeeze(prediction)
        topk_labels = prediction.argsort()[-self.config["topk"]:][::-1]
        topk_confidence = prediction[topk_labels]
        # topk_confidence = topk_confidence * 1000
        result = [self.labels[lbl_idx] for lbl_idx in topk_labels]
        if np.max(topk_confidence) < self.threshold:
            return None
        else:
            return {
                "labels": dict(zip([i for i in range(len(result))], result)),
                "confidence": dict(
                    zip([i for i in range(len(result))], topk_confidence)
                ),
            }

    def model_run(self, path_to_model: str) -> None:
        """
        Load and run the ONNX model using the provided path.

        Args:
            path_to_model (str): Path to the ONNX model file.

        Returns:
            None
        """
        session = rt.InferenceSession(
            path_to_model, providers=["CPUExecutionProvider"]
        )
        self.input_name = session.get_inputs()[0].name
        self.output_name = session.get_outputs()[0].name

        self.model = session.run

    def decode_preds(self, data):
        if platform == 'win32' or platform == 'win64':
            data = [i.encode('cp1251').decode('utf-8') for i in data]
        return data


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

