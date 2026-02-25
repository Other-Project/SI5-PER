from setuptools import find_packages, setup

package_name = "crazyflie_reset"

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
    description="Reset position node for crazyflie",
    license="MIT",
    extras_require={
        "test": [
            "pytest",
        ],
    },
    entry_points={
        "console_scripts": ["reset_pos = crazyflie_reset.reset_pos:main"],
    },
)
