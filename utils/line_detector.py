"""Module for detecting line crossings in video frames"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .geometry import Point

@dataclass
class LineCrossing:
    track_id: int
    class_name: str
    direction: str
    position: Point

class LineDetector:
    def __init__(self, line_position: float = 0.5):
        self.line_position = line_position
        self.previous_positions: Dict[int, Point] = {}
        
    def detect_crossings(self, detections: List[Dict]) -> List[LineCrossing]:
        """Detect objects crossing the vertical line"""
        crossings = []
        
        for detection in detections:
            if not self._is_valid_detection(detection):
                continue
                
            track_id = detection['track_id']
            current_pos = self._get_detection_center(detection['box'])
            
            if track_id in self.previous_positions:
                prev_pos = self.previous_positions[track_id]
                if self._has_crossed_line(prev_pos, current_pos):
                    direction = 'right' if current_pos.x > prev_pos.x else 'left'
                    crossings.append(LineCrossing(
                        track_id=track_id,
                        class_name=detection['class_name'],
                        direction=direction,
                        position=current_pos
                    ))
            
            self.previous_positions[track_id] = current_pos
            
        return crossings
    
    def _is_valid_detection(self, detection: Dict) -> bool:
        """Validate detection data"""
        return all(key in detection for key in ['track_id', 'box', 'class_name'])
    
    def _get_detection_center(self, box: List[int]) -> Point:
        """Calculate center point of detection box"""
        x1, y1, x2, y2 = box
        return Point((x1 + x2) / 2, (y1 + y2) / 2)
    
    def _has_crossed_line(self, prev_pos: Point, current_pos: Point) -> bool:
        """Check if movement between points crosses the counting line"""
        line_x = self.line_position
        return (prev_pos.x < line_x and current_pos.x >= line_x) or \
               (prev_pos.x > line_x and current_pos.x <= line_x)
    
    def reset(self):
        """Reset tracking state"""
        self.previous_positions.clear()