from distutils.core import setup, Extension

pico_module = Extension('pico_module', 
                        extra_compile_args = ["-std=c99", "-g"],
                        include_dirs = ['/opt/picoscope/include/'],
                        libraries = ['ps2000a'],
                        library_dirs = ['/opt/picoscope/lib/'],
                        sources=['pico_module.c'])

setup(ext_modules=[pico_module])
