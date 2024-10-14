from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in delivery_trip_customization/__init__.py
from delivery_trip_customization import __version__ as version

setup(
	name="delivery_trip_customization",
	version=version,
	description="Delivery Trip Customization",
	author="Smart Solution",
	author_email="info@smartsoleg.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
