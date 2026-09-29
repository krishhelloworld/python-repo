"""Robot type catalogue. Must stay identical to the rows seeded in schemas/sql/001_core_schema.sql
(a test enforces this). Only types introduced by the current stage are defined."""
from .models import RobotType

SMALL_FAST_ROBOT = RobotType(
    robot_type="small_fast_robot",
    description="Small, quick, low-payload grid robot (Stage 0 reference type)",
    introduced_in_stage=0,
    max_speed_mps=1.0, battery_capacity_wh=100.0, payload_capacity_kg=20.0,
    length_m=0.6, width_m=0.5, turning_radius_m=0.0,
    operating_cost_per_hour=4.0, communication_range_m=50.0,
    sensor_reliability=1.0, failure_probability_per_hour=0.0,
    energy_per_meter_wh=0.05, idle_power_w=5.0,
)
ROBOT_TYPES = {SMALL_FAST_ROBOT.robot_type: SMALL_FAST_ROBOT}
