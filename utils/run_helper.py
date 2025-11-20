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
        logs_dir = Path(f"./logs/{folder}/quadcopter_direct")

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

        extras = questionary.text("Extra args:", default="").ask()
        if extras:
            cmd += extras.split()
    elif mode == "train":
        cmd.append("--export_onnx")

    print(" ".join(cmd))
    subprocess.run(cmd)


if __name__ == "__main__":
    main()
