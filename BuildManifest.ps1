# =========================================================
# MAYANAGRI MANIFEST BUILDER (POLICY ENGINE v1.1.0)
# =========================================================

$baseUrl = "https://raw.githubusercontent.com/nottyguru/Mayanagri-Client/main/"
$outputJson = "manifest.json"

# =========================================================
# 1. SERVER CONFIGURATION
# =========================================================
$minecraftVersion = "1.21.11"
$fabricVersion = "0.18.4"
$serverIp = "127.0.0.1"   # Change this to play.mayanagri.in when ready!
$serverPort = 25565

# =========================================================
# 2. POLICY RULES
# =========================================================
# Strict: Deletes anything the player adds manually here.
$strictFolders = @("mods", "config")

# Lenient: Downloads updates, but NEVER deletes player's custom files.
$lenientFolders = @("resourcepacks", "shaderpacks")

# Initial Only: Downloads once, but NEVER overwrites if it exists.
$initialOnlyFiles = @("options.txt", "servers.dat")

# Ignored: Specific files inside strict folders to never delete.
$ignoredPaths = @() # e.g., @("mods/OptiFine.jar")

# =========================================================
# 3. BUILD ENGINE
# =========================================================
Write-Host "Building Mayanagri Policy Manifest..." -ForegroundColor Cyan

$manifestFiles = @()
$allFoldersToScan = $strictFolders + $lenientFolders

# Scan all folders (Strict + Lenient)
foreach ($folder in $allFoldersToScan) {
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

# Scan specific root files (Initial Only)
foreach ($file in $initialOnlyFiles) {
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

# Construct the Master JSON Object
$manifestData = @{
    minecraft_version = $minecraftVersion
    fabric_version    = $fabricVersion
    server_ip         = $serverIp
    server_port       = $serverPort
    jvm_flags         = @(
        "-XX:+UseG1GC",
        "-XX:+UnlockExperimentalVMOptions",
        "-XX:G1NewSizePercent=20",
        "-XX:G1ReservePercent=20",
        "-XX:MaxGCPauseMillis=50",
        "-XX:G1HeapRegionSize=32M"
    )
    policies          = @{
        strict_folders     = $strictFolders
        lenient_folders    = $lenientFolders
        initial_only_files = $initialOnlyFiles
        ignored_paths      = $ignoredPaths
    }
    files             = $manifestFiles
}

# Export and beautifully format
$manifestData | ConvertTo-Json -Depth 10 | Out-File $outputJson -Encoding UTF8

Write-Host "Done! manifest.json generated successfully with Policy Rules." -ForegroundColor Green
Pause