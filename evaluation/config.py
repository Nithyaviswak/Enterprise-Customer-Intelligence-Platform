import os
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


@dataclass
class YOLOConfig:
    model_path: str = "models/yolov8n.pt"
    imgsz: int = 640
    conf_threshold: float = 0.25
    iou_threshold: float = 0.45
    max_det: int = 300
    device: str = "cpu"
    half_precision: bool = False
    batch_size: int = 16
    warmup_iterations: int = 50
    num_inference_runs: int = 500


@dataclass
class EvaluationConfig:
    project_name: str = "yolo-retail-intelligence"
    experiment_name: str = "model_evaluation"
    output_dir: str = "evaluation_output"
    dataset_dir: str = "data"

    regression_thresholds: dict = field(default_factory=lambda: {
        "mAP50": -0.02,
        "mAP50_95": -0.02,
        "precision": -0.03,
        "recall": -0.03,
        "f1_score": -0.03,
        "fps": -5.0,
    })

    class_names: List[str] = field(default_factory=lambda: [
        "person", "bicycle", "car", "motorcycle", "airplane", "bus",
        "train", "truck", "boat", "traffic_light", "fire_hydrant",
        "stop_sign", "parking_meter", "bench", "bird", "cat", "dog",
        "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe",
        "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
        "skis", "snowboard", "sports_ball", "kite", "baseball_bat",
        "baseball_glove", "skateboard", "surfboard", "tennis_racket",
        "bottle", "wine_glass", "cup", "fork", "knife", "spoon", "bowl",
        "banana", "apple", "sandwich", "orange", "broccoli", "carrot",
        "hot_dog", "pizza", "donut", "cake", "chair", "couch",
        "potted_plant", "bed", "dining_table", "toilet", "tv", "laptop",
        "mouse", "remote", "keyboard", "cell_phone", "microwave",
        "oven", "toaster", "sink", "refrigerator", "book", "clock",
        "vase", "scissors", "teddy_bear", "hair_drier", "toothbrush",
    ])

    @property
    def output_path(self) -> Path:
        return Path(self.output_dir)

    @property
    def reports_dir(self) -> Path:
        return self.output_path / "reports"

    @property
    def visualizations_dir(self) -> Path:
        return self.output_path / "visualizations"

    @property
    def artifacts_dir(self) -> Path:
        return self.output_path / "artifacts"

    @property
    def registry_path(self) -> Path:
        return self.output_path / "registry.json"

    def ensure_dirs(self):
        for d in [self.output_path, self.reports_dir, self.visualizations_dir, self.artifacts_dir]:
            d.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls) -> "EvaluationConfig":
        return cls(
            project_name=os.getenv("EVAL_PROJECT_NAME", cls.project_name),
            experiment_name=os.getenv("EVAL_EXPERIMENT_NAME", cls.experiment_name),
            output_dir=os.getenv("EVAL_OUTPUT_DIR", cls.output_dir),
            dataset_dir=os.getenv("EVAL_DATASET_DIR", cls.dataset_dir),
        )
