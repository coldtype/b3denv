import setuptools

long_description = """
# b3denv

### Help with setting up bpy/blender/blender addons

More info available at: [coldtype.xyz]
"""

setuptools.setup(
    name="b3denv",
    version="0.0.1",
    author="Rob Stenson / Coldtype",
    author_email="rob@goodhertz.com",
    description="Help with blender python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/coldtype/b3denv",
    packages=[
        "b3denv",
    ],
    entry_points={
        'console_scripts': [
            'b3denv = b3denv:main'
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 2",
        "Operating System :: OS Independent",
    ],
)
