from setuptools import setup

import omnilog

setup(
    name="omnilog",
    version=omnilog.__version__,
    download_url="https://github.com/sandboxwebs/omnilog/" + omnilog.__version__,
    url="https://github.com/sandboxwebs/omnilog",
    license="GPLV3",
    author="Eloy (sbw)",
    install_requires=['paramiko', 'notify2'],
    author_email="eloy@sandboxwebs.com",
    description="A daemon remote log watcher that uses ssh, and multithreaded design.",
    packages=["omnilog"],
    include_package_data=True,
    platforms="any",
    scripts="omnilog.py"
)
