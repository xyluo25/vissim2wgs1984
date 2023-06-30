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
    name="vissim2geojson",  # Replace with your own username
    version="1.5.1",
    author="Xiangyong Luo",
    author_email="luoxiangyong01@gamil.com",
    description="Convert VISSIM files: .inpx to .geojson, .fzp and .fhz to csv.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Xiangyongluo/vissim2wgs1984",


    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',

    install_requires=modules_needed,
    packages=setuptools.find_packages(),
    include_package_data=True,

    package_data={'': ['*.txt', '*.xls', '*.xlsx', '*.csv', '*.png',
                       "*.inpx", "*.fhz", "*.fzp", "*.db", "*.geojson",
                       "*.err", "*.knr", "*.lsa", "*.mer", "*.ovw", "*.rsr", "*.inp0", "*.layx", "*.sig"],
                  "test_data": ['*.txt', '*.png', "*.inpx", "*.fhz", "*.fzp"]},
    # data_files=[("vissim_data", ["vissim_data/*"])]
)
