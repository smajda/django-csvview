from setuptools import setup

setup(
    name="django-csvview",
    author="Jon Smajda",
    author_email="jon@smajda.com",
    description="A CSVView mixin for Django views using tablib",
    version="0.1",
    packages=['csvview'],
    install_requires=[
        "django >= 1.4",
        "tablib",
    ],
)
