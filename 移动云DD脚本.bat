@echo off
REM 关闭 Windows Defender 实时保护
powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"

REM 下载 reinstall.bat 脚本
certutil -urlcache -f -split https://www.ghproxy.cc/https://raw.githubusercontent.com/bin456789/reinstall/main/reinstall.bat

REM 运行 reinstall.bat 脚本来安装 Windows Server 2022
.\reinstall.bat windows --iso='https://drive.massgrave.dev/zh-cn_windows_server_2022_updated_oct_2024_x64_dvd_d1a47ecc.iso' --image-name='Windows Server 2022 SERVERDATACENTER'

pause