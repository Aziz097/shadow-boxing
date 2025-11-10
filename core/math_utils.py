import numpy as np
import math

def calculate_angle(a, b, c):
    """Calculate angle at point b given points a, b, c"""
    ba = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b)
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)

def distance(point1, point2):
    """Calculate Euclidean distance between two points"""
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def is_point_in_rect(point, rect):
    """
    Check if point is inside rectangle
    rect: (x, y, width, height)
    """
    x, y, w, h = rect
    px, py = point
    return x <= px <= x + w and y <= py <= y + h

def calculate_velocity(prev_pos, curr_pos, time_delta):
    """Calculate velocity vector and magnitude"""
    if time_delta <= 0 or prev_pos is None or curr_pos is None:
        return np.array([0, 0]), 0
    
    displacement = np.array(curr_pos) - np.array(prev_pos)
    velocity_vec = displacement / time_delta
    velocity_mag = np.linalg.norm(velocity_vec)
    
    return velocity_vec, velocity_mag