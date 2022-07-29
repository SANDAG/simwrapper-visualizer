call C:\Users\sxu\Anaconda3\Scripts\activate.bat %PYTHON_ENV%
call conda create -n simwrapper_testing python=3.9
call conda activate simwrapper_testing
call pip install simwrapper
call simwrapper here