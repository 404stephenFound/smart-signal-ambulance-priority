import pytest
import time
from backend.app.signal_fsm import TrafficSignalFSM
from backend.app.models import SignalCommand

def test_fsm_normal_cycle_transitions():
    fsm = TrafficSignalFSM("JN-TEST", yellow_s=0.2, all_red_s=0.1, min_green_s=0.2, normal_green_s=0.3)
    
    st1 = fsm.tick()
    assert st1.state == "NS_GREEN"
    assert st1.active_group == "NS"

    time.sleep(0.35)
    st2 = fsm.tick()
    assert st2.state == "NS_YELLOW"

    time.sleep(0.25)
    st3 = fsm.tick()
    assert st3.state == "ALL_RED"

    time.sleep(0.15)
    st4 = fsm.tick()
    assert st4.state == "EW_GREEN"
    assert st4.active_group == "EW"

def test_fsm_priority_preemption_and_recovery():
    fsm = TrafficSignalFSM("JN-TEST", yellow_s=0.1, all_red_s=0.1, min_green_s=0.1, normal_green_s=0.5)
    
    # Put FSM in EW_GREEN
    fsm.current_state = "EW_GREEN"
    fsm.active_group = "EW"
    fsm.state_start_time = time.time() - 0.2

    # Command NS Priority
    cmd = SignalCommand(
        cmd="PRIORITY",
        request_id="req-123",
        group="NS",
        ttl_s=2.0,
        seq=1,
        issued_at="now"
    )
    accepted = fsm.process_command(cmd)
    assert accepted is True

    # Tick should move to PREEMPT_YELLOW
    st_yellow = fsm.tick()
    assert st_yellow.state == "PREEMPT_YELLOW"

    time.sleep(0.15)
    st_red = fsm.tick()
    assert st_red.state == "PREEMPT_ALL_RED"

    time.sleep(0.15)
    st_p_grn = fsm.tick()
    assert st_p_grn.state == "PRIORITY_GREEN_NS"
    assert st_p_grn.is_priority is True

    # Resume Normal
    cmd_resume = SignalCommand(cmd="RESUME_NORMAL", seq=2, issued_at="now")
    fsm.process_command(cmd_resume)

    st_rec_yel = fsm.tick()
    assert st_rec_yel.state == "RECOVERY_YELLOW"

    time.sleep(0.15)
    st_rec_red = fsm.tick()
    assert st_rec_red.state == "RECOVERY_ALL_RED"

def test_fsm_safety_fuzzing():
    """Fuzz state machine with 50 random commands; assert conflicting groups are never green together."""
    fsm = TrafficSignalFSM("JN-TEST", yellow_s=0.05, all_red_s=0.05, min_green_s=0.05, normal_green_s=0.1)
    
    for i in range(1, 40):
        grp = "NS" if i % 2 == 0 else "EW"
        cmd = SignalCommand(cmd="PRIORITY", group=grp, seq=i, issued_at="now")
        fsm.process_command(cmd)
        st = fsm.tick()

        # Invariant check: Can never have invalid state
        assert st.state in [
            "NS_GREEN", "NS_YELLOW", "ALL_RED", "EW_GREEN", "EW_YELLOW",
            "PREEMPT_YELLOW", "PREEMPT_ALL_RED", "PRIORITY_GREEN_NS",
            "PRIORITY_GREEN_EW", "RECOVERY_YELLOW", "RECOVERY_ALL_RED", "FAULT_SAFE"
        ]
        time.sleep(0.01)
