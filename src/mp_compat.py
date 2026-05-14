from __future__ import annotations

import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional


DEFAULT_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/1/face_landmarker.task"
)


@dataclass
class _Landmark:
    x: float
    y: float
    z: float = 0.0


@dataclass
class _FaceLandmarks:
    landmark: List[_Landmark]


class _ProcessResult:
    def __init__(self, multi_face_landmarks: Optional[List[_FaceLandmarks]]):
        self.multi_face_landmarks = multi_face_landmarks


def _ensure_model_file(model_path: Path, url: str = DEFAULT_MODEL_URL) -> Path:
    model_path.parent.mkdir(parents=True, exist_ok=True)
    if model_path.exists() and model_path.stat().st_size > 0:
        return model_path

    try:
        with urllib.request.urlopen(url, timeout=120) as r:
            data = r.read()
        model_path.write_bytes(data)
        return model_path
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "Missing face landmarker model file and failed to download it.\n"
            f"Tried to download: {url}\n"
            f"Target path: {model_path}\n"
            f"Error: {e}\n\n"
            "Fix: download the file in a browser and save it at the target path."
        ) from e


class FaceMeshLike:
    """
    Compatibility wrapper for code written against `mp.solutions.face_mesh.FaceMesh`.

    MediaPipe 0.10.x removed legacy `mp.solutions` from the PyPI package. This wrapper
    uses MediaPipe Tasks FaceLandmarker and exposes a `.process(rgb)` API that returns
    an object with `.multi_face_landmarks` like the legacy solution.
    """

    def __init__(
        self,
        *,
        static_image_mode: bool,
        max_num_faces: int,
        min_detection_confidence: float,
        min_tracking_confidence: float,
        model_path: Path,
    ) -> None:
        import mediapipe as mp  # type: ignore
        from mediapipe.tasks.python import BaseOptions  # type: ignore
        from mediapipe.tasks.python.vision import face_landmarker  # type: ignore
        from mediapipe.tasks.python.vision.core.vision_task_running_mode import (  # type: ignore
            VisionTaskRunningMode,
        )

        model_path = _ensure_model_file(model_path)

        running_mode = (
            VisionTaskRunningMode.IMAGE
            if static_image_mode
            else VisionTaskRunningMode.VIDEO
        )

        options = face_landmarker.FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(model_path)),
            running_mode=running_mode,
            num_faces=int(max_num_faces),
            min_face_detection_confidence=float(min_detection_confidence),
            min_face_presence_confidence=float(min_detection_confidence),
            min_tracking_confidence=float(min_tracking_confidence),
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        self._mp = mp
        self._running_mode = running_mode
        self._landmarker = face_landmarker.FaceLandmarker.create_from_options(options)
        self._t0 = time.time()
        self._last_ts_ms = 0

    def close(self) -> None:
        try:
            self._landmarker.close()
        except Exception:
            pass

    def process(self, rgb_image: Any) -> _ProcessResult:
        # rgb_image: np.ndarray HxWx3 uint8
        ts_ms = int((time.time() - self._t0) * 1000.0)
        if ts_ms <= self._last_ts_ms:
            ts_ms = self._last_ts_ms + 1
        self._last_ts_ms = ts_ms

        image = self._mp.Image(
            image_format=self._mp.ImageFormat.SRGB,
            data=rgb_image,
        )

        if str(self._running_mode).endswith("IMAGE"):
            result = self._landmarker.detect(image)
        else:
            result = self._landmarker.detect_for_video(image, ts_ms)

        faces = []
        for face in (result.face_landmarks or []):
            faces.append(
                _FaceLandmarks(
                    landmark=[_Landmark(x=float(p.x), y=float(p.y), z=float(p.z)) for p in face]
                )
            )
        return _ProcessResult(faces if faces else None)


def create_face_mesh(
    *,
    static_image_mode: bool,
    max_num_faces: int,
    refine_landmarks: bool,
    min_detection_confidence: float,
    min_tracking_confidence: float,
) -> FaceMeshLike:
    # `refine_landmarks` is a legacy FaceMesh option; the Tasks model already includes iris.
    _ = bool(refine_landmarks)
    return FaceMeshLike(
        static_image_mode=static_image_mode,
        max_num_faces=max_num_faces,
        min_detection_confidence=min_detection_confidence,
        min_tracking_confidence=min_tracking_confidence,
        model_path=Path("models/face_landmarker.task"),
    )
