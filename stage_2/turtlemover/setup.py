from setuptools import find_packages, setup

package_name = 'turtlemover'

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
    description='Turtlesim motion nodes: drive in circles, count completed laps from pose, and stop after a commanded number of circles.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'move_turtle = turtlemover.move_turtle:main',
            'circle_counter = turtlemover.count_circles:main',
            'move_turtle_topic = turtlemover.move_turtle_topic:main'
        ],
    },
)
