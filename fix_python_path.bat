@echo off
:: 查找Python安装路径并添加到PATH

echo 正在查找Python安装路径...

:: 尝试常见位置
set PYTHON_PATH=

if exist "C:\Python*" (
    for /d %%i in (C:\Python*) do (
        if exist "%%i\python.exe" (
            set PYTHON_PATH=%%i
            set PYTHON_SCRIPTS=%%i\Scripts
        )
    )
)

if exist "C:\Program Files\Python*" (
    for /d %%i in ("C:\Program Files\Python*") do (
        if exist "%%i\python.exe" (
            set PYTHON_PATH=%%i
            set PYTHON_SCRIPTS=%%i\Scripts
        )
    )
)

if exist "%LOCALAPPDATA%\Programs\Python" (
    for /d %%i in ("%LOCALAPPDATA%\Programs\Python\*") do (
        if exist "%%i\python.exe" (
            set PYTHON_PATH=%%i
            set PYTHON_SCRIPTS=%%i\Scripts
        )
    )
)

:: 如果找到Python
if not "%PYTHON_PATH%"=="" (
    echo 找到Python: %PYTHON_PATH%

    :: 检查是否已添加到PATH
    echo %PATH% | findstr /i "%PYTHON_PATH%" >nul
    if errorlevel 1 (
        echo 正在添加到系统PATH...
        setx PATH "%PATH%;%PYTHON_PATH%;%PYTHON_SCRIPTS%" /M
        echo 完成！请重新打开终端窗口
    ) else (
        echo Python路径已存在，无需添加
    )
) else (
    echo 未找到Python安装，请先安装Python
)

echo.
echo 按任意键退出...
pause >nul
