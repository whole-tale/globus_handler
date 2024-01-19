from setuptools import find_packages, setup

setup(
    name="girder-globus-handler",
    version="2.0.0",
    description="Whole Tale Girder plugin for handling Globus Transfers.",
    packages=find_packages(),
    include_package_data=True,
    license="Apache 2.0",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.10",
    setup_requires=["setuptools-git"],
    install_requires=["girder>=3", "girder-oauth", "globus-sdk~=3.3.1"],
    entry_points={
        "girder.plugin": [
            "girder_globus_handler = girder_globus_handler:GlobusHandlerPlugin"
        ]
    },
    zip_safe=False,
)
