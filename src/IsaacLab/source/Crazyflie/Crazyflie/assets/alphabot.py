import os

import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg
from isaaclab_assets import ANYDRIVE_3_SIMPLE_ACTUATOR_CFG

ACTUATORS_LEFT_WHEEL = "left_wheel"
ACTUATORS_RIGHT_WHEEL = "right_wheel"

ALPHABOT_JOINTS_NAMES = {
    ACTUATORS_LEFT_WHEEL: "wheel_left_joint",
    ACTUATORS_RIGHT_WHEEL: "wheel_right_joint"
}

ALPHABOT_USD_PATH = os.path.join(
    os.path.dirname(__file__),
    "data/alphabot/alphabot2.usd"
)

ALPHABOT_CFG = ArticulationCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=ALPHABOT_USD_PATH,
        scale=(1.0, 1.0, 1.0),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.0),
        rot=(1.0, 0.0, 0.0, 0.0),
    ),
    actuators={
        ACTUATORS_LEFT_WHEEL: ANYDRIVE_3_SIMPLE_ACTUATOR_CFG.replace(
            joint_names_expr=ALPHABOT_JOINTS_NAMES[ACTUATORS_LEFT_WHEEL],
        ),
        ACTUATORS_RIGHT_WHEEL: ANYDRIVE_3_SIMPLE_ACTUATOR_CFG.replace(
            joint_names_expr=ALPHABOT_JOINTS_NAMES[ACTUATORS_RIGHT_WHEEL],
        ),
    }
)
