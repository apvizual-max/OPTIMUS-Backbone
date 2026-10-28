# git-scratch.ps1
# Shared resolver for the scratch root used by the self-check gates.
#
# WHY THIS EXISTS
# Every self-check builds throwaway git repositories: a bare remote, a clone,
# a conflict copy. Each of those carries its own .git directory. When the
# fixture root was <project>\state\tmp\..., it sat INSIDE the Google Drive
# mirror (E:\Google\GDrive\...), the tree DriveFS administers while it
# synchronises. DriveFS may materialise, replace or remove files underneath
# a live git repository: the laboratory was standing in the battlefield.
#
# MEASURED 2026-10-27: 90+ .git directories inside the mirrored tree, every
# one of them a test fixture. The real repositories were already outside
# (E:\Google\GitData-Optimus-CI, -CD, -PKMS); the fixtures were not.
#
# The scratch root is derived from the repository's OWN gitdir, which lives
# outside the mirror (E:\Google\GitData-Optimus-CI\repo). The laboratory
# follows the repository instead of hard-coding a machine path: the gitdir's
# parent IS the single root of this project's git data, and the scratch lives
# beside the repositories inside it.
#
#   E:\Google\GitData-Optimus-CI\
#     repo\                    gitdir of the project repo
#     clone-MAVIS-CLOUD\        gitdir of the Cloud clone
#     clone-MAVIS-OPTIMUS-CI\   gitdir of the CI clone
#     scratch\                 <- this
#
# Override with the environment variable MAVIS_CI_SCRATCH.
#
# MAVIS_GITDIR: in containerul Mavis-Optimus-CI, pointerul .git din arbore
# contine o cale Windows (E:/...), pe care git linux nu o poate rezolva.
# Containerul transmite gitdir-ul direct, ca sa existe O singura
# implementare a rezolvarii, valida in ambele medii.
#
# ASCII ONLY: executed by Windows PowerShell 5.1.

function Get-GitScratchRoot {
    param(
        [Parameter(Mandatory = $true)][string]$ProjectRoot,
        [string]$Name = 'scratch'
    )

    $override = [Environment]::GetEnvironmentVariable('MAVIS_CI_SCRATCH')
    if ($override -and $override.Trim()) { return $override.Trim() }

    $gitDir = ''
    $envGitDir = [Environment]::GetEnvironmentVariable('MAVIS_GITDIR')
    if ($envGitDir -and $envGitDir.Trim()) {
        $gitDir = $envGitDir.Trim()
    } else {
        $prev = $ErrorActionPreference
        $ErrorActionPreference = 'Continue'
        try {
            $gitDir = ((& git -C $ProjectRoot rev-parse --absolute-git-dir 2>$null) -join '').Trim()
        } catch {
            $gitDir = ''
        }
        $ErrorActionPreference = $prev
    }

    if (-not $gitDir) {
        # Guessing a root would break the invariant this script exists to
        # protect: the scratch MUST live outside the mirrored tree.
        throw ('GITDIR_UNRESOLVED for ' + $ProjectRoot + ' - cannot derive the scratch root')
    }

    $base = Split-Path -Parent $gitDir
    if (-not $base) {
        throw ('GITDIR_HAS_NO_PARENT: ' + $gitDir)
    }

    return (Join-Path $base $Name)
}

# The DriveFS mirror root, found by walking up from the project. On this
# machine the mirror is E:\Google\GDrive and the project lives under it.
function Get-DriveMirrorRoot {
    param([Parameter(Mandatory = $true)][string]$Path)

    $cur = [System.IO.Path]::GetFullPath($Path).TrimEnd('\','/')
    while ($cur) {
        if ((Split-Path -Leaf $cur) -eq 'GDrive') { return $cur }
        $parent = Split-Path -Parent $cur
        if (-not $parent -or $parent -eq $cur) { break }
        $cur = $parent
    }
    return ''
}

# A fixture root inside the mirror is a defect, not a style choice: DriveFS
# administers that space while it synchronises. Refuse loudly rather than
# quietly building the laboratory in the battlefield again.
function Assert-ScratchOutsideMirror {
    param(
        [Parameter(Mandatory = $true)][string]$ScratchRoot,
        [Parameter(Mandatory = $true)][string]$ProjectRoot
    )

    $sep = [System.IO.Path]::DirectorySeparatorChar
    $s = [System.IO.Path]::GetFullPath($ScratchRoot).TrimEnd('\','/')
    $p = [System.IO.Path]::GetFullPath($ProjectRoot).TrimEnd('\','/')

    $boundaries = @($p)
    $mirror = Get-DriveMirrorRoot -Path $p
    if ($mirror) { $boundaries += $mirror }

    foreach ($b in $boundaries) {
        if ($s.Equals($b, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw ('SCRATCH_ROOT_ON_BOUNDARY=' + $s)
        }
        if ($s.StartsWith($b + $sep, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw ('SCRATCH_ROOT_INSIDE_MIRROR=' + $s + ' boundary=' + $b)
        }
    }

    return $s
}
