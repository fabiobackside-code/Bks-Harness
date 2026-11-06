param(
    [switch]$Remove,
    [ValidateSet('User', 'Process')][string]$Scope = 'User',
    [string]$RegistrySubKey = 'Environment'
)
# Acrescenta (ou remove com -Remove) a pasta bin/ ao PATH do escopo informado.
$bin = $PSScriptRoot.TrimEnd('\')

function Get-NewPath([string]$current) {
    $parts = @($current -split ';' | Where-Object { $_ -and ($_.TrimEnd('\') -ne $bin) })
    if ($Remove) { return ($parts -join ';') }
    return (($parts + $bin) -join ';')
}

if ($Scope -eq 'Process') {
    $current = [Environment]::GetEnvironmentVariable('Path', 'Process')
    if (-not $current) { $current = '' }
    [Environment]::SetEnvironmentVariable('Path', (Get-NewPath $current), 'Process')
    if ($Remove) { Write-Host "PATH ($Scope): pasta removida" } else { Write-Host "PATH ($Scope): pasta acrescentada" }
    exit 0
}

# Escopo do usuário: lê e grava o valor cru do registro, sem expandir %VARIAVEL%.
$key = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($RegistrySubKey, $true)
if (-not $key) {
    Write-Host "erro: chave HKCU\$RegistrySubKey não encontrada"
    exit 1
}
try {
    $names = $key.GetValueNames()
    $exists = $names -contains 'Path'
    $current = [string]$key.GetValue('Path', '', [Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames)
    $kind = [Microsoft.Win32.RegistryValueKind]::ExpandString
    if ($exists -and $key.GetValueKind('Path') -eq [Microsoft.Win32.RegistryValueKind]::String) {
        $kind = [Microsoft.Win32.RegistryValueKind]::String
    }
    $new = Get-NewPath $current
    if ($new -eq $current -and ($exists -or $Remove)) {
        Write-Host "PATH ($Scope): nada a mudar"
        exit 0
    }
    $key.SetValue('Path', $new, $kind)
} finally {
    $key.Close()
}
if ($RegistrySubKey -eq 'Environment') {
    # Gravar e apagar uma variável pela API do .NET avisa os outros programas (WM_SETTINGCHANGE).
    [Environment]::SetEnvironmentVariable('BKHAR_PATH_REFRESH', '1', 'User')
    [Environment]::SetEnvironmentVariable('BKHAR_PATH_REFRESH', $null, 'User')
}
if ($Remove) { Write-Host "PATH ($Scope): pasta removida" } else { Write-Host "PATH ($Scope): pasta acrescentada; abra um novo terminal" }
