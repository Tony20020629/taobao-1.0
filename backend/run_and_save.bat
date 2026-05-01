@echo off
cd /d e:\NewProject\taobao\backend
echo Starting test...
python test.py > test_output.txt 2>&1
echo Test completed!
type test_output.txt
pause
