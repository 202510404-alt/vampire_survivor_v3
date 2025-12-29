@echo off
echo [1/3] 게임 빌드 시작 (pygbag)...
py -m pygbag --build --title vampire_v4 .

echo [2/3] vampire-web 리포지토리로 파일 배달 중...
:: 🚩 /y 옵션은 묻지도 따지지도 말고 덮어쓰라는 뜻!
xcopy /s /e /y "build\web\*" "..\vampire-web\"

echo [3/3] 깃허브로 전송 중...
cd ..\vampire-web
git add .
git commit -m "Auto Build: Supabase Ranking Version"
git push origin main

:: 🚩 다시 원래 폴더로 돌아오기
cd ..\vampire_survivor_v3
echo ==========================================
echo 드디어 끝났다! 링크 확인해봐 (1분 뒤 반영): 
echo https://202510404-alt.github.io/vampire-web/
echo ==========================================
pause