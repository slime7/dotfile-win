[CmdletBinding()]
param(
    [Alias('d')]
    [string]$Destination
)

$ErrorActionPreference = 'Stop'

function Show-Usage {
    Write-Host 'Usage: linkto -d <destination>'
}

if ([string]::IsNullOrWhiteSpace($Destination)) {
    Show-Usage
    exit 1
}

$skillsRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$resolvedDestination = [System.IO.Path]::GetFullPath($Destination)

if (-not (Test-Path -LiteralPath $resolvedDestination)) {
    New-Item -ItemType Directory -Path $resolvedDestination | Out-Null
}

$skillDirs = Get-ChildItem -LiteralPath $skillsRoot -Directory | Where-Object {
    Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md')
}

foreach ($skillDir in $skillDirs) {
    $linkPath = Join-Path $resolvedDestination $skillDir.Name

    if (Test-Path -LiteralPath $linkPath) {
        $existingItem = Get-Item -LiteralPath $linkPath -Force

        if ($existingItem.LinkType -eq 'SymbolicLink') {
            $existingTarget = $existingItem.Target
            if ($existingTarget -is [System.Array]) {
                $existingTarget = $existingTarget[0]
            }

            if (-not [string]::IsNullOrWhiteSpace($existingTarget)) {
                $existingTarget = [System.IO.Path]::GetFullPath(
                    [System.IO.Path]::Combine($existingItem.DirectoryName, $existingTarget)
                )
            }

            if ($existingTarget -eq $skillDir.FullName) {
                Write-Host "Skip $($skillDir.Name): already linked"
                continue
            }
        }

        Write-Error "Target already exists and cannot be replaced: $linkPath"
    }

    New-Item -ItemType SymbolicLink -Path $linkPath -Target $skillDir.FullName | Out-Null
    Write-Host "Linked $($skillDir.Name) -> $linkPath"
}
