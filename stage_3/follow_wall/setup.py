from setuptools import find_packages, setup

package_name = 'follow_wall'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Gokul Edakke Puram',
    maintainer_email='gokul.edakkepuram@hs-weingarten.de',
    description='LiDAR wall following for the TurtleBot3: aligns the robot parallel to a wall and tracks it with a proportional controller.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'follow_wall_node = follow_wall.follow_wall_node:main'
        ],
    },
)
