import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="k8s-scheduler",
    version="0.0.1",
    author="Sai Kiran",
    author_email="neo2603@gmail.com",
    description="Basic Scheduler for k8s",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/saikiran2603/k8s-scheduler/",
    project_urls={
        "Bug Tracker": "https://github.com/saikiran2603/k8s-scheduler//issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "k8s_scheduler"},
    packages=setuptools.find_packages(where="k8s_scheduler"),
    python_requires=">=3.6",
)