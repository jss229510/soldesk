param([switch]$Mail, [switch]$Settings)

$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    if ($Settings -or [string]::IsNullOrWhiteSpace($env:SPRING_DATASOURCE_URL)) {
        $dbUrl = Read-Host 'Oracle JDBC URL (Enter: jdbc:oracle:thin:@localhost:1521:xe)'
        if ([string]::IsNullOrWhiteSpace($dbUrl)) { $dbUrl = 'jdbc:oracle:thin:@localhost:1521:xe' }
        $env:SPRING_DATASOURCE_URL = $dbUrl
    }
    if ($Settings -or [string]::IsNullOrWhiteSpace($env:SPRING_DATASOURCE_USERNAME) -or [string]::IsNullOrWhiteSpace($env:SPRING_DATASOURCE_PASSWORD)) {
        $dbUser = Read-Host 'Oracle username (Enter: soldesk)'
        if ([string]::IsNullOrWhiteSpace($dbUser)) { $dbUser = 'soldesk' }
        $dbAccount = Get-Credential -UserName $dbUser -Message 'Enter your Oracle password'
        if ($null -eq $dbAccount -or $dbAccount.Password.Length -eq 0) { throw 'Oracle password was not entered.' }
        $env:SPRING_DATASOURCE_USERNAME = $dbAccount.UserName
        $env:SPRING_DATASOURCE_PASSWORD = $dbAccount.GetNetworkCredential().Password
    }
    if ([string]::IsNullOrWhiteSpace($env:JWT_SECRET)) {
        $key = New-Object byte[] 32
        $random = [System.Security.Cryptography.RandomNumberGenerator]::Create()
        try { $random.GetBytes($key) } finally { $random.Dispose() }
        $env:JWT_SECRET = [Convert]::ToBase64String($key)
    }
    if ($Mail) {
        $env:MAIL_HOST = 'smtp.naver.com'
        $env:MAIL_PORT = '587'
        if ($Settings -or [string]::IsNullOrWhiteSpace($env:MAIL_USERNAME) -or [string]::IsNullOrWhiteSpace($env:MAIL_PASSWORD)) {
            $mailAddress = Read-Host 'Sending Naver email address'
            if ($mailAddress -notmatch '^[^\s@]+@naver\.com$') { throw 'Enter a full Naver email address.' }
            $mailAccount = Get-Credential -UserName $mailAddress -Message 'Enter your Naver APPLICATION password'
            if ($null -eq $mailAccount -or $mailAccount.Password.Length -eq 0) { throw 'Application password was not entered.' }
            $env:MAIL_USERNAME = $mailAccount.UserName
            $env:MAIL_PASSWORD = $mailAccount.GetNetworkCredential().Password
        }
        $env:MAIL_FROM = $env:MAIL_USERNAME
    }
    if ([string]::IsNullOrWhiteSpace($env:FRONTEND_URL)) { $env:FRONTEND_URL = 'http://localhost:5173' }

    # 사용자별 빌드 위치. 실행 중인 이전 파일의 잠금 방지
    $localFolder = Join-Path $PSScriptRoot '.local'
    New-Item -ItemType Directory -Path $localFolder -Force | Out-Null
    $buildFolder = Join-Path $env:LOCALAPPDATA ('soldesk\builds\' + [guid]::NewGuid().ToString())
    $gradlePath = $buildFolder.Replace('\', '/').Replace("'", "\'")
    $initFile = Join-Path $localFolder ('run-' + [guid]::NewGuid().ToString() + '.gradle')
    [System.IO.File]::WriteAllText($initFile, "allprojects { layout.buildDirectory.set(file('$gradlePath')) }", (New-Object System.Text.UTF8Encoding($false)))
    & .\gradlew.bat -g (Join-Path $env:USERPROFILE '.gradle') -I $initFile bootRun
    if ($LASTEXITCODE -ne 0) { throw 'Backend startup failed. Check the error above.' }
} finally {
    if ($initFile -and (Test-Path -LiteralPath $initFile)) { Remove-Item -LiteralPath $initFile }
    Pop-Location
}
