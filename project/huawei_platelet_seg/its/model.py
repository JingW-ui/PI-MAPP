from __future__ import annotations

from pathlib import Path
from typing import Any, List, Dict, Optional, Tuple

import torch
import torch.nn.functional as F
import numpy as np

from ultralytics.engine.model import Model
from ultralytics.models import yolo
from ultralytics.nn.tasks import (
    ClassificationModel,
    DetectionModel,
    OBBModel,
    PoseModel,
    SegmentationModel,
    WorldModel,
)
from ultralytics.utils import ROOT, YAML
from ultralytics.utils.checks import print_args
from ultralytics.data.augment import LetterBox
from ultralytics.utils import ops
from PIL import Image


class PlateletSegmentationModel(SegmentationModel):
    """
    Specialized SegmentationModel for platelet segmentation on gray-scale images.
    Includes enhancements for better boundary detection and small object segmentation.
    """
    def __init__(self, cfg, ch=3, nc=None, verbose=True):
        super().__init__(cfg, ch, nc, verbose)
        # Add specialized layers for platelet segmentation
        self._add_platelet_enhancement_layers()
        
    def _add_platelet_enhancement_layers(self):
        """Add specialized layers to improve platelet segmentation performance."""
        # Enhance boundary detection
        self.boundary_enhancer = torch.nn.Conv2d(self.model[-2].cv2.cv.out_channels, 
                                                1, kernel_size=3, padding=1)
        
        # Add attention mechanism for small platelet detection
        self.platelet_attention = torch.nn.Sequential(
            torch.nn.AdaptiveAvgPool2d(1),
            torch.nn.Conv2d(self.model[-2].cv2.cv.out_channels, 
                          self.model[-2].cv2.cv.out_channels // 16, 1, bias=False),
            torch.nn.ReLU(inplace=True),
            torch.nn.Conv2d(self.model[-2].cv2.cv.out_channels // 16, 
                          self.model[-2].cv2.cv.out_channels, 1, bias=False),
            torch.nn.Sigmoid()
        )
    
    def forward(self, x, augment=False, profile=False, visualize=False):
        """Enhanced forward pass with platelet-specific processing."""
        outputs = super().forward(x, augment, profile, visualize)
        
        # Apply platelet attention to improve small object detection
        if isinstance(outputs, list):
            # For training
            features = self.model[-2].cv2.cv(self.model[-3](self.model[-4](x)))
            attention = self.platelet_attention(features)
            features = features * attention
            
            # Update the segmentation output
            outputs[0][..., :self.nc + 1] = self.model[-1](features)
        else:
            # For inference
            features = self.model[-2].cv2.cv(self.model[-3](self.model[-4](x)))
            attention = self.platelet_attention(features)
            features = features * attention
            
            # Update the segmentation output
            outputs[..., :self.nc + 1] = self.model[-1](features)
            
        return outputs


class HuaWeiSegModel(Model):
    """
    Specialized model for platelet segmentation on gray-scale images.
    Enhanced with custom preprocessing, postprocessing, and model architecture.
    """

    def __init__(self, model: str | Path = "yolo11n.pt", task: str | None = None, verbose: bool = False):
        path = Path(model if isinstance(model, (str, Path)) else "")
        print(f"Loading YOLO model from {path}")
        if "-world" in path.stem and path.suffix in {".pt", ".yaml", ".yml"}:  # if YOLOWorld PyTorch model
            new_instance = HuaWeiSegModelWorld(path, verbose=verbose)
            self.__class__ = type(new_instance)
            self.__dict__ = new_instance.__dict__
        else:
            # Continue with default YOLO initialization
            super().__init__(model=model, task=task, verbose=verbose)
            if hasattr(self.model, "model") and "RTDETR" in self.model.model[-1]._get_name():  # if RTDETR head
                from ultralytics import RTDETR

                new_instance = RTDETR(self)
                self.__class__ = type(new_instance)
                self.__dict__ = new_instance.__dict__

    def _custom_platelet_preprocess(self, image: torch.Tensor) -> torch.Tensor:
        """
        Custom preprocessing for platelet images:
        - Enhance contrast for better platelet boundary detection
        - Apply adaptive histogram equalization to improve visibility of small platelets
        - Convert to RGB if grayscale (3 channels for model compatibility)
        """
        # If grayscale, convert to 3-channel
        if image.ndim == 3 and image.shape[0] == 1:
            image = image.repeat(3, 1, 1)
        elif image.ndim == 4 and image.shape[1] == 1:
            image = image.repeat(1, 3, 1, 1)
        
        # Apply contrast enhancement
        image = self._enhance_contrast(image)
        
        return image
    
    def _enhance_contrast(self, image: torch.Tensor) -> torch.Tensor:
        """Enhance contrast using adaptive histogram equalization-like technique."""
        # Normalize to 0-1 range
        image_norm = (image - image.min()) / (image.max() - image.min() + 1e-6)
        
        # Apply CLAHE-like enhancement
        clip_limit = 0.03
        tile_size = 16
        
        # Process in tiles
        if image.ndim == 4:  # Batch processing
            batch_size, channels, height, width = image.shape
            enhanced = torch.zeros_like(image)
            
            for b in range(batch_size):
                for c in range(channels):
                    for i in range(0, height, tile_size):
                        for j in range(0, width, tile_size):
                            tile = image_norm[b, c, i:i+tile_size, j:j+tile_size]
                            tile_mean = tile.mean()
                            tile_std = tile.std() + 1e-6
                            
                            # Clip values and normalize
                            tile_clipped = torch.clamp(tile, tile_mean - clip_limit * tile_std, tile_mean + clip_limit * tile_std)
                            tile_enhanced = (tile_clipped - tile_clipped.min()) / (tile_clipped.max() - tile_clipped.min() + 1e-6)
                            
                            enhanced[b, c, i:i+tile_size, j:j+tile_size] = tile_enhanced
            
            return enhanced
        else:
            # Single image processing
            channels, height, width = image.shape
            enhanced = torch.zeros_like(image)
            
            for c in range(channels):
                for i in range(0, height, tile_size):
                    for j in range(0, width, tile_size):
                        tile = image_norm[c, i:i+tile_size, j:j+tile_size]
                        tile_mean = tile.mean()
                        tile_std = tile.std() + 1e-6
                        
                        # Clip values and normalize
                        tile_clipped = torch.clamp(tile, tile_mean - clip_limit * tile_std, tile_mean + clip_limit * tile_std)
                        tile_enhanced = (tile_clipped - tile_clipped.min()) / (tile_clipped.max() - tile_clipped.min() + 1e-6)
                        
                        enhanced[c, i:i+tile_size, j:j+tile_size] = tile_enhanced
            
            return enhanced
    
    def _custom_platelet_postprocess(self, preds: List[torch.Tensor], img: torch.Tensor, orig_imgs: List[Image.Image]) -> List[Dict[str, Any]]:
        """
        Custom postprocessing for platelet segmentation:
        - Refine boundaries using boundary enhancer output
        - Apply size filtering for platelet-specific objects
        - Improve mask quality with morphological operations
        """
        # Default postprocessing first
        results = super()._postprocess(preds, img, orig_imgs)
        
        # Apply platelet-specific postprocessing
        for result in results:
            if 'masks' in result:
                masks = result['masks']
                
                # Filter small platelets (remove noise)
                masks = self._filter_small_platelets(masks)
                
                # Refine mask boundaries
                masks = self._refine_boundaries(masks)
                
                result['masks'] = masks
        
        return results
    
    def _filter_small_platelets(self, masks: torch.Tensor, min_area: int = 10) -> torch.Tensor:
        """Filter out small objects that are likely not platelets."""
        if masks.ndim == 4:  # Batch of masks
            valid_masks = []
            for batch_mask in masks:
                batch_valid = []
                for mask in batch_mask:
                    area = mask.sum().item()
                    if area >= min_area:
                        batch_valid.append(mask)
                if batch_valid:
                    batch_valid = torch.stack(batch_valid)
                    valid_masks.append(batch_valid)
                else:
                    valid_masks.append(torch.empty(0, *mask.shape[1:]))
            return valid_masks
        else:
            # Single batch
            valid_masks = []
            for mask in masks:
                area = mask.sum().item()
                if area >= min_area:
                    valid_masks.append(mask)
            if valid_masks:
                return torch.stack(valid_masks)
            else:
                return torch.empty(0, *masks.shape[1:])
    
    def _refine_boundaries(self, masks: torch.Tensor) -> torch.Tensor:
        """Refine mask boundaries using morphological operations."""
        if masks.ndim == 4:
            refined = []
            for batch_mask in masks:
                batch_refined = []
                for mask in batch_mask:
                    # Apply dilation followed by erosion to smooth boundaries
                    mask = mask.unsqueeze(0).unsqueeze(0)  # Add batch and channel dims
                    mask = F.max_pool2d(mask, kernel_size=3, padding=1)
                    mask = F.avg_pool2d(mask, kernel_size=3, padding=1)
                    batch_refined.append(mask.squeeze())
                refined.append(torch.stack(batch_refined))
            return refined
        else:
            # Single batch
            refined = []
            for mask in masks:
                mask = mask.unsqueeze(0).unsqueeze(0)  # Add batch and channel dims
                mask = F.max_pool2d(mask, kernel_size=3, padding=1)
                mask = F.avg_pool2d(mask, kernel_size=3, padding=1)
                refined.append(mask.squeeze())
            return torch.stack(refined)
    
    def estimate_platelet_metrics(self, masks: torch.Tensor) -> Dict[str, float]:
        """
        Estimate platelet metrics from segmentation masks:
        - Platelet count
        - Average platelet area
        - Size distribution metrics
        """
        metrics = {
            "platelet_count": 0,
            "mean_area": 0.0,
            "median_area": 0.0,
            "area_std": 0.0
        }
        
        if masks is None or len(masks) == 0:
            return metrics
        
        # Flatten batch dimension
        if masks.ndim == 4:
            masks = masks.flatten(0, 1)
        
        # Calculate areas
        areas = []
        for mask in masks:
            area = mask.sum().item()
            if area > 0:
                areas.append(area)
        
        if areas:
            metrics["platelet_count"] = len(areas)
            metrics["mean_area"] = sum(areas) / len(areas)
            metrics["median_area"] = sorted(areas)[len(areas) // 2]
            metrics["area_std"] = np.std(areas)
        
        return metrics
    
    def detect_overlapping_platelets(self, masks: torch.Tensor, threshold: float = 0.2) -> List[Tuple[int, int, float]]:
        """
        Detect overlapping platelets and return pairs with overlap ratio.
        """
        overlapping_pairs = []
        
        if masks is None or len(masks) < 2:
            return overlapping_pairs
        
        # Flatten batch dimension
        if masks.ndim == 4:
            masks = masks.flatten(0, 1)
        
        # Check all pairs
        num_masks = len(masks)
        for i in range(num_masks):
            for j in range(i + 1, num_masks):
                # Calculate intersection over union (IoU)
                intersection = (masks[i] * masks[j]).sum().item()
                union = (masks[i] + masks[j]).sum().item()
                
                if union > 0:
                    iou = intersection / union
                    if iou > threshold:
                        overlapping_pairs.append((i, j, iou))
        
        return overlapping_pairs
    
    def process_overlapping_platelets(self, masks: torch.Tensor, boxes: torch.Tensor) -> torch.Tensor:
        """
        Process overlapping platelets to separate them using watershed-like technique.
        """
        if masks is None or len(masks) < 2:
            return masks
        
        # This is a simplified version of watershed for overlapping objects
        processed_masks = []
        
        for mask in masks:
            # Apply distance transform to find centers
            distance = F.conv2d(mask.unsqueeze(0).unsqueeze(0).float(), 
                              torch.ones(1, 1, 3, 3), padding=1)
            
            # Normalize distance map
            distance = (distance - distance.min()) / (distance.max() - distance.min() + 1e-6)
            
            # Threshold to find core regions
            core = distance > 0.7
            
            # Expand core to get separated regions
            separated = F.max_pool2d(core.float(), kernel_size=5, padding=2)
            
            processed_masks.append(separated.squeeze())
        
        if processed_masks:
            return torch.stack(processed_masks)
        else:
            return masks
    
    @property
    def task_map(self) -> dict[str, dict[str, Any]]:
        """Map head to model, trainer, validator, and predictor classes."""
        return {
            "segment": {
                "model": PlateletSegmentationModel,
                "trainer": yolo.segment.SegmentationTrainer,
                "validator": yolo.segment.SegmentationValidator,
                "predictor": yolo.segment.SegmentationPredictor,
            },
        }


class HuaWeiSegModelWorld(Model):
    """
    HuaWeiSegModelWorld is an open-vocabulary object detection model that can detect objects based on text descriptions
    without requiring training on specific classes. It extends the YOLO architecture to support real-time
    open-vocabulary detection.

    """

    def __init__(self, model: str | Path = "yolov8s-world.pt", verbose: bool = False) -> None:
        super().__init__(model=model, task="detect", verbose=verbose)

        # Assign default COCO class names when there are no custom names
        if not hasattr(self.model, "names"):
            self.model.names = YAML.load(ROOT / "cfg/datasets/coco8.yaml").get("names")

    @property
    def task_map(self) -> dict[str, dict[str, Any]]:
        """Map head to model, validator, and predictor classes."""
        return {
            "detect": {
                "model": WorldModel,
                "validator": yolo.detect.DetectionValidator,
                "predictor": yolo.detect.DetectionPredictor,
                "trainer": yolo.world.WorldTrainer,
            }
        }

    def set_classes(self, classes: list[str]) -> None:
        """
        Set the model's class names for detection.

        Args:
            classes (list[str]): A list of categories i.e. ["person"].
        """
        self.model.set_classes(classes)
        # Remove background if it's given
        background = " "
        if background in classes:
            classes.remove(background)
        self.model.names = classes

        # Reset method class names
        if self.predictor:
            self.predictor.model.names = classes