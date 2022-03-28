import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="k8s-scheduler",
    version="0.0.13",
    author="Sai Kiran",
    author_email="neo2603@gmail.com",
    description="Basic Scheduler for k8s",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/saikiran2603/k8s-scheduler/",
    project_urls={
        "Bug Tracker": "https://github.com/saikiran2603/k8s-scheduler/issues",
        "homepage": "https://github.com/saikiran2603/k8s-scheduler/",
        "documentation": "https://github.com/saikiran2603/k8s-scheduler/blob/master/README.md",
        "source": "https://github.com/saikiran2603/k8s-scheduler/",
        "download": "https://github.com/saikiran2603/k8s-scheduler/releases",
        "tracker": "https://github.com/saikiran2603/k8s-scheduler/issues"
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries",
        "Topic :: Scientific/Engineering",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["setuptools>=42",
                      "pymongo>=4.0.2",
                      "croniter>=1.3.4",
                      "kubernetes>=23.3.0",
                      "python-dateutil>=2.8.2"],
)
