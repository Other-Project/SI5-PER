from setuptools import find_packages, setup

package_name = 'crazyflie_landing'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Evan Galli',
    maintainer_email='evan.galli@etu.univ-cotedazur.fr',
    description='Runs anc AI model to manage the Crazyflie trajectory in order to land',
    license='MIT',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
        'rl_model = crazyflie_landing.rl_model:main',
        ],
    },
)
