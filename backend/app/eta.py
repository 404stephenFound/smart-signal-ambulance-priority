from typing import Tuple

def calculate_eta(distance_m: float, speed_kmh_smoothed: float, min_speed_kmh: float = 5.0) -> Tuple[float, bool]:
    """
    Calculates ETA in seconds with stopped vehicle detection.
    
    Returns:
        (eta_seconds, is_stopped)
    """
    is_stopped = speed_kmh_smoothed < 2.0
    effective_speed = max(speed_kmh_smoothed, min_speed_kmh)
    v_ms = effective_speed / 3.6  # km/h to m/s
    
    if distance_m <= 0.0:
        return 0.0, is_stopped
        
    eta_s = distance_m / v_ms
    return round(eta_s, 1), is_stopped

def compute_eta_error_s(predicted_eta_s: float, t_request_sec: float, t_crossing_sec: float) -> float:
    """
    Computes absolute error between predicted ETA and actual elapsed time to crossing.
    """
    actual_elapsed_s = t_crossing_sec - t_request_sec
    return round(abs(predicted_eta_s - actual_elapsed_s), 2)
