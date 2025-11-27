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
        choices=["rsl_rl"],
        default="rsl_rl"
    ).ask()

    task = questionary.text(
        "Task name:",
        default="Template-Crazyflie-Direct-v0"
    ).ask()

    headless = questionary.confirm("Headless?", default=True).ask()

    cmd = [sys.executable, f"{get_root_path()}/src/IsaacLab/scripts/{folder}/{mode}.py", f"--task={task}"]

    if headless:
        cmd.append("--headless")

    if mode == "play":
        logs_dir = Path(f"{get_root_path()}/src/IsaacLab/logs/{folder}/quadcopter_direct")

        date_folders = sorted(
            [f for f in logs_dir.glob("*/") if f.is_dir()],
            key=os.path.getmtime,
            reverse=True
        )

        if date_folders:
            selected_date = questionary.select(
                "Select training run:",
                choices=[str(f.name) for f in date_folders],
                use_indicator=True
            ).ask()
            selected_folder = logs_dir / selected_date
        else:
            selected_folder = Path(questionary.text("Training folder path:").ask())

        checkpoints = sorted(selected_folder.glob("*.pt"), key=os.path.getmtime, reverse=True)

        if checkpoints:
            checkpoint = questionary.select(
                "Select checkpoint:",
                choices=[str(c.name) for c in checkpoints],
                use_indicator=True
            ).ask()
            checkpoint_path = selected_folder / checkpoint
        else:
            checkpoint = questionary.text("Checkpoint path:").ask()
            checkpoint_path = Path(checkpoint)

        cmd.append(f"--checkpoint={checkpoint_path}")

        num_envs = questionary.text("Number of environment:", default="1").ask()

        cmd.append(f"--num_envs={num_envs}")

        extras = questionary.text("Extra args:", default="").ask()
        if extras:
            cmd += extras.split()
    elif mode == "train":
        cmd.append(f"--logs_dir={get_root_path()}/src/IsaacLab/logs/")
        cmd.append("--export_onnx")

    print(" ".join(cmd))
    subprocess.run(cmd)


def get_root_path():
    return os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), "..")


if __name__ == "__main__":
    main()
