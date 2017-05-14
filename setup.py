from setuptools import setup

setup(
    name='beets-bandcamp',
    version='0.1.1',
    description='Plugin for beets (http://beets.io) to use bandcamp as an autotagger source.',
    long_description=open('README.rst').read(),
    author='Ariel George',
    author_email='unarbolito@gmail.com',
    url='https://github.com/unrblt/beets-bandcamp',
    download_url='https://github.com/unrblt/beets-bandcamp/archive/v0.1.0.tar.gz',
    license='GPL-2.0',
    platforms='ALL',

    packages=['beetsplug'],

    install_requires=[
        'beets>=1.4.4',
        'requests',
        'beautifulsoup4',
        'isodate'
    ],

    classifiers=[
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Players :: MP3',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
