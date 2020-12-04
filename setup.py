import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pso2-color-picker",
    version="0.1.2",
    author="The Renegade Coder",
    author_email="jeremy.grifski@therenegadecoder.com",
    description="A color matching tool for PSO2.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jrg94/color-picker",
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            'color-picker = color_picker.color_picker:main',
        ],
        "gui_scripts": [
            'image-titler-gui = imagetitler.gui:main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pillow>=6.0.0',
        'numpy==1.19.3',
    ],
)
