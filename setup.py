# -*- coding:utf-8 -*-
##############################################################
# Created Date: Tuesday, June 14th 2022
# Contact Info: luoxiangyong01@gmail.com
# Author/Copyright: Mr. Xiangyong Luo
##############################################################

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

try:
    # if have requirements.txt file inside the folder
    with open("requirements.txt", "r", encoding="utf-8") as f:
        modules_needed = [i.strip() for i in fh.readlines()]
except Exception:
    modules_needed = []

setuptools.setup(
    name="vissim2wgs1984",  # Replace with your own username
    version="1.1.0",
    author="Xiangyong Luo",
    author_email="luoxiangyong01@gamil.com",
    description="Convert vissim files(.inpx and .fzp to geojson, .fhz to csv). This tool help user to convert vissim files to wgs1984 and csv files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Xiangyongluo/vissim2wgs1984",


    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',

    install_requires=modules_needed,
    packages=setuptools.find_packages(),
    include_package_data=True,

    package_data={'': ['*.txt', '*.xls', '*.xlsx', '*.csv','*.png'],
                  "test_data": ['*.txt']}
)
