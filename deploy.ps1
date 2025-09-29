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

& "C:\Program Files\7-Zip\7z.exe" a -tzip hackyeah2025.zip ./static/* ./main.py ./requirements.txt -spf
az webapp deploy --resource-group $RESOURCE_GROUP --name $APP_NAME --src-path hackyeah2025.zip --type zip
Remove-Item hackyeah2025.zip