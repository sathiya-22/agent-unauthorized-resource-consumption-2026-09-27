from setuptools import setup, find_packages

setup(
    name='agent_resource_guard',
    version='0.1.0',
    packages=find_packages(),
    description='A resource guard for agentic AI systems to prevent unauthorized resource consumption.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='AutoScout',
    url='https://github.com/autoscout-prototype/agent-resource-guard', # Placeholder
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring',
    ],
    python_requires='>=3.7',
)
