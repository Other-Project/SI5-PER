from setuptools import find_packages, setup

package_name = "crazyflie_position"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Evan Galli",
    maintainer_email="evan.galli@etu.univ-cotedazur.fr",
    description="Position reporting node for Crazyflie",
    license="MIT",
    entry_points={
        "console_scripts": [
            "position = crazyflie_position.position:main",
        ],
    },
)
