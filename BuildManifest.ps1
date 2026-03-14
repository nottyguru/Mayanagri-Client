# =========================================================
# MAYANAGRI MANIFEST BUILDER (STRICT MIRROR)
# =========================================================

$baseUrl = "https://raw.githubusercontent.com/nottyguru/Mayanagri-Client/main/"
$outputJson = "manifest.json"

# Strict mirroring targets
$allowedFolders = @("mods", "config", "shaderpacks", "resourcepacks")
$allowedFiles = @("options.txt")

Write-Host "Building Mayanagri Manifest..." -ForegroundColor Cyan

$manifestFiles = @()

foreach ($folder in $allowedFolders) {
    if (Test-Path $folder) {
        $files = Get-ChildItem -Path $folder -File -Recurse
        foreach ($file in $files) {
            $relativePath = (Resolve-Path -Relative $file.FullName).TrimStart('.\').Replace('\', '/')
            Write-Host "Hashing: $relativePath"
            $hash = (Get-FileHash $file.FullName -Algorithm SHA256).Hash.ToLower()
            
            $fileObj = @{
                path = $relativePath
                hash = $hash
                url  = $baseUrl + $relativePath.Replace(" ", "%20")
            }
            $manifestFiles += $fileObj
        }
    }
}

foreach ($file in $allowedFiles) {
    if (Test-Path $file) {
        Write-Host "Hashing: $file"
        $hash = (Get-FileHash $file -Algorithm SHA256).Hash.ToLower()
        
        $fileObj = @{
            path = $file
            hash = $hash
            url  = $baseUrl + $file.Replace(" ", "%20")
        }
        $manifestFiles += $fileObj
    }
}

$manifestData = @{
    minecraft_version = "1.21.11"
    fabric_version    = "0.18.4"
    jvm_flags         = @(
        "-XX:+UseG1GC",
        "-XX:+UnlockExperimentalVMOptions"
    )
    files             = $manifestFiles
}

$manifestData | ConvertTo-Json -Depth 10 | Out-File $outputJson -Encoding UTF8

Write-Host "Done! manifest.json generated successfully." -ForegroundColor Green
Pause