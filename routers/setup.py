from setuptools import setup

setup(
    name="routers",
    description="Various packages for auto-configuring Linux routing daemons",
    author="Packethost",
    packages=["helpers", "bird", "frr"],
    install_requires=[
        "Jinja2 >= 2.11.1",
        "MarkupSafe >= 1.1.1",
        "requests >= 2.23.0",
        "urllib3 >= 1.25.8",
        "certifi >= 2019.11.28",
        "chardet >= 3.0.4",
        "idna >= 2.9",
    ],
)
