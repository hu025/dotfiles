@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

:: ============================================================
:: Hermes USB Launcher — Windows 即插即用版 v2
:: 双击即可，首次自动初始化，之后直接使用
:: ============================================================

set "USB_DIR=%~dp0"
set "USB_DIR=%USB_DIR:~0,-1%"

set "PORTABLE_PY=%USB_DIR%\portable\python"
set "PORTABLE_NODE=%USB_DIR%\portable\node"
set "HERMES_HOME=%USB_DIR%\hermes-home"
set "PYTHON=%PORTABLE_PY%\python.exe"
set "NODE=%PORTABLE_NODE%\node.exe"
set "NPM=%PORTABLE_NODE%\npm.cmd"
set "LOG=%HERMES_HOME%\logs\usb-launcher.log"

if not exist "%HERMES_HOME%\logs" mkdir "%HERMES_HOME%\logs" 2>nul

:: ── 初始化 ──────────────────────────────────────────────
if not exist "%PORTABLE_PY%\python.exe" (
    echo [首次运行] 正在下载 Python embeddable (~20MB)...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.13.0/python-3.13.0-embed-amd64.zip' -OutFile '%TEMP%\python-embed.zip'"
    powershell -Command "Expand-Archive -Path '%TEMP%\python-embed.zip' -DestinationPath '%PORTABLE_PY%' -Force"
    del /f /q "%TEMP%\python-embed.zip" 2>nul
    :: 启用 site 模块
    (
        echo python313.zip
        echo .
        echo import site
    ) > "%PORTABLE_PY%\python313._pth"
    :: 下载 get-pip.py
    powershell -Command "Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PORTABLE_PY%\get-pip.py'"
    cd /d "%PORTABLE_PY%" ^&^& python.exe get-pip.py --no-warn-script-location --quiet
    del /f /q "%PORTABLE_PY%\get-pip.py" 2>nul
    echo [Python 初始化完成]
    echo.
)

if not exist "%PORTABLE_NODE%\node.exe" (
    echo [首次运行] 正在下载 Node.js (~40MB)...
    powershell -Command "Invoke-WebRequest -Uri 'https://nodejs.org/dist/v22.16.0/node-v22.16.0-win-x64.zip' -OutFile '%TEMP%\node.zip'"
    powershell -Command "Expand-Archive -Path '%TEMP%\node.zip' -DestinationPath '%PORTABLE_NODE%' -Force"
    del /f /q "%TEMP%\node.zip" 2>nul
    :: 提亮嵌套目录
    move "%PORTABLE_NODE%\node-v22.16.0-win-x64\*" "%PORTABLE_NODE%\" 2>nul
    rmdir "%PORTABLE_NODE%\node-v22.16.0-win-x64" 2>nul
    echo [Node.js 初始化完成]
    echo.
)

:: ── 路径 ──────────────────────────────────────────────
set "PATH=%PORTABLE_PY%;%PORTABLE_PY%\Scripts;%PORTABLE_NODE%;%PATH%"
set "HERMES_HOME=%USB_DIR%\hermes-home"
set "PYTHONPATH=%PORTABLE_PY%\Lib\site-packages"
set "HERMES_HOME=%HERMES_HOME%"

:: ── 主菜单 ─────────────────────────────────────────────
:menu
cls
echo ============================================================
echo  Hermes USB Launcher  ^(Windows^)
echo  HERMES_HOME: %HERMES_HOME%
echo ============================================================
echo.
echo  [1] 安装 hermes-agent ^(首次必选，耗时 ~2分钟^)
echo  [2] 启动 Hermes Chat ^(`hermes chat`^)
echo  [3] 启动 Hermes Gateway ^(后台，含看门狗^)
echo  [4] 启动 OpenClaw ^(`openclaw` QQ Bot^)
echo  [5] 查看状态
echo  [6] 停止所有服务
echo  [0] 退出
echo.
set /p CHOICE="请选择 [0-6]: "

if "%CHOICE%"=="1" goto install
if "%CHOICE%"=="2" goto chat
if "%CHOICE%"=="3" goto gateway
if "%CHOICE%"=="4" goto openclaw
if "%CHOICE%"=="5" goto status
if "%CHOICE%"=="6" goto stop
goto menu

:install
cls
echo.
echo [安装 hermes-agent (~150MB)...]
echo 首次安装耗时约 2 分钟，请耐心等待...
echo.
"%PYTHON%" -m pip install hermes-agent --upgrade --no-warn-script-location
if errorlevel 1 (
    echo.
    echo [错误] 安装失败！请检查网络连接后重试。
) else (
    echo.
    echo [成功] hermes-agent 安装完成！
    echo.
)
pause
goto menu

:chat
cls
if not exist "%PORTABLE_PY%\Scripts\hermes.exe" (
    echo [错误] hermes 未安装，请先运行 [1] 安装
    echo.
    pause
    goto menu
)
echo [启动 Hermes Chat...]
"%PYTHON%" -m hermes.cli.main chat
goto menu

:gateway
cls
if not exist "%PORTABLE_PY%\Scripts\hermes.exe" (
    echo [错误] hermes 未安装，请先运行 [1] 安装
    echo.
    pause
    goto menu
)
echo [启动 Hermes Gateway ^(带看门狗，自动重启)^]...

:: 检查是否已在运行
for /f "tokens=2" %%a in ('tasklist /FI "WINDOWTITLE eq Hermes Gateway*" /FO LIST 2^>nul ^| find "PID"') do (
    echo [提示] Hermes Gateway 已在运行 ^(PID: %%a^)
    echo.
    pause
    goto menu
)

:: 看门狗循环：任何退出都 5 秒后重启
set "GATEWAY_LOG=%HERMES_HOME%\logs\gateway-watchdog.log"
echo [%date% %time%] Starting hermes gateway... >> "%GATEWAY_LOG%"

:GWLOOP
"%PYTHON%" -m hermes_cli.main gateway run >> "%GATEWAY_LOG%" 2>&1
set "EXIT_CODE=%ERRORLEVEL%"
echo [%date% %time%] Gateway exited ^(code %EXIT_CODE%^), restarting in 5s... >> "%GATEWAY_LOG%"
timeout /t 5 /nobreak >nul
goto GWLOOP

:openclaw
cls
if not exist "%USB_DIR%\openclaw\openclaw.mjs" (
    echo [错误] openclaw 未找到！
    echo 请确认 openclaw 目录已复制到 U 盘根目录
    echo.
    pause
    goto menu
)
echo [启动 OpenClaw ^(QQ Bot^)...]
cd /d "%USB_DIR%\openclaw"
start "OpenClaw" cmd /k "node openclaw.mjs"
goto menu

:status
cls
echo === Hermes USB 状态 ===
echo.
if exist "%PORTABLE_PY%\python.exe" (
    for /f "tokens=*" %%v in ('"%PYTHON%" --version 2^>^&1') do echo Python: %%v
) else (
    echo Python: 未安装
)
if exist "%PORTABLE_NODE%\node.exe" (
    for /f "tokens=*" %%v in ('"%NODE%" --version 2^>^&1') do echo Node.js: %%v
) else (
    echo Node.js: 未安装
)
if exist "%PORTABLE_PY%\Scripts\hermes.exe" (
    for /f "tokens=*" %%v in ('"%PYTHON%" -m hermes --version 2^>^&1') do echo hermes-agent: %%v
) else (
    echo hermes-agent: 未安装 ^(请运行 [1]^)
)
echo.
echo 磁盘空间:
wmic logicaldisk where "DeviceID='%USB_DIR:~0,2%'" get DeviceID,Size,FreeSpace /format:list 2>nul
echo.
tasklist /FI "IMAGENAME eq python.exe" 2>nul
tasklist /FI "IMAGENAME eq node.exe" 2>nul
echo.
pause
goto menu

:stop
cls
echo [停止所有服务...]
taskkill /F /IM python.exe 2>nul ^|^| echo 没有 python 进程
taskkill /F /IM node.exe 2>nul ^|^| echo 没有 node 进程
taskkill /F /IM openclaw.exe 2>nul ^|^| echo 没有 openclaw 进程
echo [完成]
echo.
pause
goto menu