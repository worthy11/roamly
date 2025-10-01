Get-Content ".env" | ForEach-Object {
    if ($_ -match "^\s*#") { return }
    if ($_ -match "^\s*$") { return }
    $parts = $_ -split "=", 2
    $name = $parts[0].Trim()
    $value = $parts[1].Trim()
    Set-Item -Path "env:$name" -Value $value
}
$RESOURCE_GROUP = $env:RESOURCE_GROUP
$APP_NAME = $env:APP_NAME

Push-Location frontend
npm run build
Pop-Location

Copy-Item -Path "./frontend/dist/*" -Destination ./static/ -Recurse -Force
& "C:\Program Files\7-Zip\7z.exe" a -tzip roamly.zip ./main.py ./requirements.txt ./static/* ./db/* ./app/* "-xr!__pycache__" -spf
az webapp deploy --resource-group $RESOURCE_GROUP --name $APP_NAME --src-path roamly.zip --type zip
Remove-Item roamly.zip