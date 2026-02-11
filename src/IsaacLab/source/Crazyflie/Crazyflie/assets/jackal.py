import os
import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg
from isaaclab.actuators import ImplicitActuatorCfg

JACKAL_ACTUATORS_LEFT_WHEEL = "left_wheel"
JACKAL_ACTUATORS_RIGHT_WHEEL = "right_wheel"

JACKAL_JOINTS_NAMES = {
    JACKAL_ACTUATORS_LEFT_WHEEL: "front_left_wheel|rear_left_wheel",
    JACKAL_ACTUATORS_RIGHT_WHEEL: "front_right_wheel|rear_right_wheel",
}

JACKAL_USD_PATH = os.path.join(
    os.path.dirname(__file__),
    "data/jackal/jackal.usd" 
)

JACKAL_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=JACKAL_USD_PATH,
        scale=(1.0, 1.0, 1.0),
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            retain_accelerations=False,
            linear_damping=0.0,
            angular_damping=0.0,
            max_linear_velocity=1000.0,
            max_angular_velocity=1000.0,
            max_depenetration_velocity=1.0,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.0),
        rot=(1.0, 0.0, 0.0, 0.0),
        joint_pos={".*": 0.0},
        joint_vel={".*": 0.0},
    ),
    actuators={
        JACKAL_ACTUATORS_LEFT_WHEEL: ImplicitActuatorCfg(
            joint_names_expr=JACKAL_JOINTS_NAMES[JACKAL_ACTUATORS_LEFT_WHEEL],
            effort_limit=500.0,
            velocity_limit=10.0,
            stiffness=0.0,
            damping=1000.0,
        ),
        JACKAL_ACTUATORS_RIGHT_WHEEL: ImplicitActuatorCfg(
            joint_names_expr=JACKAL_JOINTS_NAMES[JACKAL_ACTUATORS_RIGHT_WHEEL],
            effort_limit=500.0,
            velocity_limit=10.0,
            stiffness=0.0,
            damping=1000.0,
        ),
    },
    soft_joint_pos_limit_factor=1.0,
)
