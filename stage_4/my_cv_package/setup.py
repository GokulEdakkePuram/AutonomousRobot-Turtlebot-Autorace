from setuptools import find_packages, setup

package_name = 'my_cv_package'

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
    description='Camera-based lane following for the TurtleBot3 using HSV masking and ROI centroid tracking.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'cv_view = my_cv_package.cv_view:main',
            'cv_color_detect = my_cv_package.cv_color_detect:main'
        ],
    },
)
