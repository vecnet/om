Psycopg2 Virtual Environment Installation Notes (Windows)
http://www.stickpeople.com/projects/python/win-psycopg/

Method 1
Do not double-click the package to run. Instead, use easy_install from either setuptools or distribute.
Assuming the installer is downloaded to C:\ and the virtual environment is in C:\virtualenv,
the command would look something like:

C:\> C:\virtualenv\Scripts\activate.bat
(virtualenv) C:\> easy_install psycopg2-2.6.1.win32-py2.7-pg9.4.4-release.exe

Method 2
Extract the binaries and place them in the <venv_dir>\Lib\site-packages\ directory.