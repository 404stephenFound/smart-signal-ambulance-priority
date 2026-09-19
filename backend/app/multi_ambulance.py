from typing import List, Dict, Any, Optional
from .models import PriorityRequestModel

SEVERITY_WEIGHTS = {
    "critical": 3,
    "urgent": 2,
    "standard": 1
}

class MultiAmbulanceCoordinator:
    """
    Coordinates priority resolution when multiple emergency vehicles approach the same junction.
    Documented heuristic balancing patient triage severity, ETA, and traffic disruption.
    """
    def __init__(self, max_hold_s: float = 45.0):
        self.max_hold_s = max_hold_s

    def resolve_priority_order(
        self,
        active_requests: List[PriorityRequestModel],
        severities: Optional[Dict[str, str]] = None,
        current_active_group: Optional[str] = None
    ) -> List[PriorityRequestModel]:
        """
        Orders pending requests deterministically:
        1. Compatible requests in current green group merged.
        2. Triage severity (critical > urgent > standard).
        3. Earlier ETA.
        4. Least disruption (active green group gets tie-break preference).
        5. Deterministic ambulance ID tie-break.
        """
        if not active_requests:
            return []

        severities = severities or {}

        def sort_key(req: PriorityRequestModel):
            # 1. Severity weight (higher is better, so negate for ascending sort)
            sev = severities.get(req.ambulance_id, "urgent").lower()
            sev_score = -SEVERITY_WEIGHTS.get(sev, 2)

            # 2. ETA (lower is sooner)
            eta = req.eta_s

            # 3. Disruption (0 if already matches active group, 1 if requires signal change)
            # Need to infer green group from approach_id or assume NS/EW from approach
            is_same_group = 0 if (current_active_group and req.approach_id.endswith(current_active_group[0])) else 1

            # 4. Tie-break ID
            return (sev_score, eta, is_same_group, req.ambulance_id)

        sorted_reqs = sorted(active_requests, key=sort_key)
        return sorted_reqs

    def should_merge_window(self, req1: PriorityRequestModel, req2: PriorityRequestModel, green_group1: str, green_group2: str) -> bool:
        """Checks if two requests share the same conflict group and can be served concurrently."""
        return green_group1 == green_group2
