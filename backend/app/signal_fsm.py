import time
from typing import Dict, Any, Optional, Literal, Tuple
from .models import SignalState, SignalCommand

class TrafficSignalFSM:
    """
    Deterministic Safety-Interlocked Traffic Signal Finite State Machine.
    Shared reference logic implemented identically in Python backend and ESP32 firmware.
    """
    def __init__(
        self,
        junction_id: str,
        yellow_s: float = 3.0,
        all_red_s: float = 2.0,
        min_green_s: float = 5.0,
        normal_green_s: float = 15.0,
        priority_ttl_s: float = 30.0,
        heartbeat_timeout_s: float = 6.0
    ):
        self.junction_id = junction_id
        self.yellow_s = yellow_s
        self.all_red_s = all_red_s
        self.min_green_s = min_green_s
        self.normal_green_s = normal_green_s
        self.priority_ttl_s = priority_ttl_s
        self.heartbeat_timeout_s = heartbeat_timeout_s

        # State tracking
        self.current_state: str = "NS_GREEN"
        self.active_group: Optional[Literal["NS", "EW"]] = "NS"
        self.state_start_time: float = time.time()
        self.target_duration_s: float = self.normal_green_s

        # Priority tracking
        self.is_priority: bool = False
        self.active_request_id: Optional[str] = None
        self.priority_group: Optional[Literal["NS", "EW"]] = None
        self.priority_start_time: Optional[float] = None
        self.pending_command: Optional[SignalCommand] = None

        # Sequence and heartbeat
        self.last_seq: int = 0
        self.last_heartbeat_time: float = time.time()
        self.is_healthy: bool = True
        self.resume_phase: str = "EW_GREEN"

    def update_heartbeat(self):
        """Record received heartbeat from controller/virtual simulator."""
        self.last_heartbeat_time = time.time()
        if not self.is_healthy:
            self.is_healthy = True

    def process_command(self, cmd: SignalCommand) -> bool:
        """
        Accept and validate external signal command.
        Enforces command sequence monotonicity and TTL sanity.
        """
        now = time.time()
        self.update_heartbeat()

        if cmd.seq <= self.last_seq and self.last_seq != 0:
            return False  # Reject stale / duplicate sequence
        self.last_seq = cmd.seq

        if cmd.cmd == "PRIORITY":
            if not cmd.group or cmd.group not in ["NS", "EW"]:
                return False
            self.pending_command = cmd
            return True

        elif cmd.cmd == "CANCEL_PRIORITY" or cmd.cmd == "RESUME_NORMAL":
            if self.is_priority:
                self._trigger_recovery()
            self.pending_command = None
            return True

        elif cmd.cmd == "FAULT_SAFE":
            self.current_state = "FAULT_SAFE"
            self.active_group = None
            self.is_priority = False
            self.pending_command = None
            return True

        return False

    def _change_state(self, new_state: str, duration_s: float):
        self.current_state = new_state
        self.target_duration_s = duration_s
        self.state_start_time = time.time()
        
        # Set active group immediately upon state change
        if new_state.startswith("NS_") or new_state == "PRIORITY_GREEN_NS":
            self.active_group = "NS"
        elif new_state.startswith("EW_") or new_state == "PRIORITY_GREEN_EW":
            self.active_group = "EW"
        elif "ALL_RED" in new_state or new_state == "FAULT_SAFE":
            self.active_group = None

    def tick(self, dt: float = 0.1) -> SignalState:
        """
        State Machine Execution Step. Called periodically.
        """
        now = time.time()
        elapsed = now - self.state_start_time

        # 1. Heartbeat Watchdog
        if now - self.last_heartbeat_time > self.heartbeat_timeout_s:
            if self.is_healthy:
                self.is_healthy = False
                if self.is_priority:
                    self._trigger_recovery()

        # 2. Priority TTL Expiration Guard
        if self.is_priority and self.priority_start_time:
            if now - self.priority_start_time > self.priority_ttl_s:
                self._trigger_recovery()

        # 3. Handle Pending Priority Command
        if self.pending_command and not self.is_priority:
            req_group = self.pending_command.group
            # If current active green group matches requested group and min_green passed:
            if (self.current_state == f"{req_group}_GREEN" or self.current_state == f"PRIORITY_GREEN_{req_group}"):
                # Hold / extend green immediately
                self.is_priority = True
                self.priority_group = req_group
                self.active_request_id = self.pending_command.request_id
                self.priority_start_time = now
                self._change_state(f"PRIORITY_GREEN_{req_group}", self.priority_ttl_s)
                self.pending_command = None
            elif self.current_state.endswith("_GREEN"):
                # Conflicting green: verify min_green satisfied before yellow transition
                if elapsed >= self.min_green_s:
                    self._transition_to_preempt_yellow(req_group)
                    self.pending_command = None
            elif "ALL_RED" in self.current_state:
                # If already in all-red, can transition directly to priority green
                self._activate_priority_green(req_group, self.pending_command.request_id)
                self.pending_command = None

        # 4. State Transitions (Only trigger when elapsed time satisfies target duration)
        elif self.current_state == "NS_GREEN":
            if elapsed >= self.target_duration_s:
                self._change_state("NS_YELLOW", self.yellow_s)

        elif self.current_state == "NS_YELLOW":
            if elapsed >= self.target_duration_s:
                self.resume_phase = "EW_GREEN"
                self._change_state("ALL_RED", self.all_red_s)

        elif self.current_state == "ALL_RED":
            if elapsed >= self.target_duration_s:
                if self.pending_command:
                    req_group = self.pending_command.group
                    self._activate_priority_green(req_group, self.pending_command.request_id)
                    self.pending_command = None
                else:
                    self._change_state(self.resume_phase, self.normal_green_s)

        elif self.current_state == "EW_GREEN":
            if elapsed >= self.target_duration_s:
                self._change_state("EW_YELLOW", self.yellow_s)

        elif self.current_state == "EW_YELLOW":
            if elapsed >= self.target_duration_s:
                self.resume_phase = "NS_GREEN"
                self._change_state("ALL_RED", self.all_red_s)

        # Preemption sequence
        elif self.current_state == "PREEMPT_YELLOW":
            if elapsed >= self.target_duration_s:
                self._change_state("PREEMPT_ALL_RED", self.all_red_s)

        elif self.current_state == "PREEMPT_ALL_RED":
            if elapsed >= self.target_duration_s:
                self._activate_priority_green(self.priority_group, self.active_request_id)

        # Priority Green
        elif self.current_state.startswith("PRIORITY_GREEN_"):
            self.active_group = self.priority_group
            # Priority holds indefinitely until crossing, cancel, or TTL

        # Recovery sequence
        elif self.current_state == "RECOVERY_YELLOW":
            if elapsed >= self.target_duration_s:
                self._change_state("RECOVERY_ALL_RED", self.all_red_s)

        elif self.current_state == "RECOVERY_ALL_RED":
            if elapsed >= self.target_duration_s:
                self.is_priority = False
                self.active_request_id = None
                self.priority_group = None
                self._change_state(self.resume_phase, self.normal_green_s)

        elif self.current_state == "FAULT_SAFE":
            self.active_group = None

        # Build state representation
        now_after = time.time()
        elapsed_now = now_after - self.state_start_time
        remaining = max(0.0, round(self.target_duration_s - elapsed_now, 1))
        return SignalState(
            junction_id=self.junction_id,
            state=self.current_state,
            active_group=self.active_group,
            is_priority=self.is_priority,
            active_request_id=self.active_request_id,
            remaining_s=remaining,
            elapsed_s=round(elapsed_now, 1),
            seq=self.last_seq,
            healthy=self.is_healthy
        )

    def _transition_to_preempt_yellow(self, target_group: Literal["NS", "EW"]):
        self.is_priority = True
        self.priority_group = target_group
        self.active_request_id = self.pending_command.request_id if self.pending_command else None
        self._change_state("PREEMPT_YELLOW", self.yellow_s)

    def _activate_priority_green(self, group: Literal["NS", "EW"], request_id: Optional[str]):
        self.is_priority = True
        self.priority_group = group
        self.active_request_id = request_id
        self.priority_start_time = time.time()
        self._change_state(f"PRIORITY_GREEN_{group}", self.priority_ttl_s)

    def _trigger_recovery(self):
        """Initiate safe recovery yellow and all-red clearance before returning to normal cycle."""
        if not self.current_state.startswith("RECOVERY_"):
            self._change_state("RECOVERY_YELLOW", self.yellow_s)
            self.resume_phase = "EW_GREEN" if self.priority_group == "NS" else "NS_GREEN"
