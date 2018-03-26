from setuptools import setup

setup(name='teleftp',
    version='0.1',
    description='FTP client with Telegram interface',
    keywords='ftp telegram',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: File Transfer Protocol (FTP)',
        'Topic :: Communications :: Chat',
    ],
    url='http://github.com/iharthi/teleftp',
    author='Sergey Kovalskiy',
    author_email='sergey@kovalskiy.net',
    license='BSD 3-clause',
    packages=['teleftp'],
    install_requires=[
        'python-telegram-bot',
    ],
    zip_safe=False)
