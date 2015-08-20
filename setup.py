from cx_Freeze import setup, Executable

setup( name = "Asteros" , version = "0.1" , description = "text" , executables = [Executable("Asteros.py" ,base = "Win32GUI")] , )