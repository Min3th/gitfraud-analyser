from setuptools import setup,find_packages

with open("README.md","r",encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt","r",encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name='gitfraud',
    version= '0.01',
    author= 'John Doe',
    author_email = "mmm@gmail.com",
    license='MIT', # text indicating the license covering the package
    description = 'A CLI tool to deteck fake Github commits', 
    long_description = long_description,
    long_description_content_type="text/markdown",
    url='github url of tool code',
    py_modules=['main'],
    packages=find_packages(),
    install_requires = [], # add 'requirements' in the future
    python_requires = '>=3.7',
    classifiers=[
        "Programming Language :: Python :: 3.13.0",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        'console_scripts':[
            'gitfraud=main:analyze' # checks for analyze function in main.py
        ]
    }
)
