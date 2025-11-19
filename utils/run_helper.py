import os
import subprocess
import sys
from pathlib import Path

import questionary


def main():
    mode = questionary.select(
        "Select mode:",
        choices=["train", "play"]
    ).ask()

    folder = questionary.select(
        "Select RL library:",
        choices=["rsl_rl", "rl_games", "skrl"],
        default="rsl_rl"
    ).ask()

    task = questionary.text(
        "Task name:",
        default="Template-Crazyflie-Direct-v0"
    ).ask()

    headless = questionary.confirm("Headless?", default=True).ask()

    cmd = [sys.executable, f"./src/IsaacLab/scripts/{folder}/{mode}.py", f"--task={task}"]

    if headless:
        cmd.append("--headless")

    if mode == "play":
        logs_dir = Path(f"./logs/{folder}")
        checkpoints = sorted(logs_dir.glob("**/checkpoints/*.pt"), key=os.path.getmtime, reverse=True)

        if checkpoints:
            checkpoint = questionary.select(
                "Select checkpoint:",
                choices=[str(c) for c in checkpoints[:10]]
            ).ask()
        else:
            checkpoint = questionary.text("Checkpoint path:").ask()

        cmd.append(f"--checkpoint={checkpoint}")

        extras = questionary.text("Extra args:", default="").ask()
        if extras:
            cmd += extras.split()
    elif mode == "train":
        cmd.append("--export_onnx")

    print(" ".join(cmd))
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
