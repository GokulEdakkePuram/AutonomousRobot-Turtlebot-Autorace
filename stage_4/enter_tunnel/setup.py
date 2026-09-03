from setuptools import find_packages, setup

package_name = 'enter_tunnel'

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
    description='Detects a red triangular tunnel sign with OpenCV and drives the TurtleBot3 into the tunnel.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'enter_tunnel = enter_tunnel.enter_tunnel:main'
        ],
    },
)
