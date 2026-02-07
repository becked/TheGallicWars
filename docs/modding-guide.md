# Old World C# Modding Guide

This guide explains how to create C# mods for Old World, the historical strategy game by Mohawk Games.

**Authoritative external resource**: [dales.world](https://dales.world) has excellent tutorials on Old World modding.

## Prerequisites

- **.NET SDK** (supports .NET Framework 4.7.2)
- **Old World** installed via Steam, Epic, or GOG
- **IDE** - Visual Studio, VS Code, or JetBrains Rider
- Basic C# knowledge

## Two Approaches to Modifying Game Behavior

Old World supports two approaches for modifying game logic with C#:

| Approach | Best For | Multi-Mod Compatible? |
|----------|----------|----------------------|
| **GameFactory Override** | Total conversion mods, scenarios | No - only one mod can use this |
| **Harmony Patching** | Targeted behavior changes | Yes - if mods patch different methods |

### Quick Decision Guide

- **Use GameFactory Override** if you're creating a scenario or total conversion and need to replace entire classes (Player, PlayerAI, City, etc.)
- **Use Harmony Patching** if you want to modify specific methods while remaining compatible with other mods

---

## Project Structure

A minimal Old World mod requires:

```
MyMod/
├── Source/
│   ├── MyMod.cs              # Mod entry point
│   └── Patches/              # Harmony patches (if using Harmony)
│       └── MyPatches.cs
├── MyMod.csproj              # Project file
├── ModInfo.xml               # Mod manifest (required)
└── .env                      # Local config (gitignored)
```

## Step 1: Create the Project File

Create `MyMod.csproj`:

```xml
<Project Sdk="Microsoft.NET.Sdk">

  <PropertyGroup>
    <TargetFramework>net472</TargetFramework>
    <AssemblyName>MyMod</AssemblyName>
    <RootNamespace>MyMod</RootNamespace>
    <LangVersion>9.0</LangVersion>
    <OutputType>Library</OutputType>
    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>
    <AppendTargetFrameworkToOutputPath>false</AppendTargetFrameworkToOutputPath>
    <OutputPath>bin/</OutputPath>
  </PropertyGroup>

  <!-- Platform-specific paths to game assemblies -->
  <PropertyGroup Condition="$([MSBuild]::IsOSPlatform('Windows'))">
    <OldWorldManagedPath>$(OldWorldPath)\OldWorld_Data\Managed</OldWorldManagedPath>
  </PropertyGroup>
  <PropertyGroup Condition="$([MSBuild]::IsOSPlatform('OSX'))">
    <OldWorldManagedPath>$(OldWorldPath)/OldWorld.app/Contents/Resources/Data/Managed</OldWorldManagedPath>
  </PropertyGroup>
  <PropertyGroup Condition="$([MSBuild]::IsOSPlatform('Linux'))">
    <OldWorldManagedPath>$(OldWorldPath)/OldWorld_Data/Managed</OldWorldManagedPath>
  </PropertyGroup>

  <ItemGroup>
    <Compile Include="Source/**/*.cs" />
  </ItemGroup>

  <!-- Harmony via NuGet (if using Harmony patching) -->
  <ItemGroup>
    <PackageReference Include="Lib.Harmony" Version="2.4.2" />
  </ItemGroup>

  <!-- Game assembly references -->
  <ItemGroup>
    <Reference Include="TenCrowns.GameCore">
      <HintPath>$(OldWorldManagedPath)/TenCrowns.GameCore.dll</HintPath>
      <Private>false</Private>
    </Reference>
    <Reference Include="UnityEngine">
      <HintPath>$(OldWorldManagedPath)/UnityEngine.dll</HintPath>
      <Private>false</Private>
    </Reference>
    <Reference Include="UnityEngine.CoreModule">
      <HintPath>$(OldWorldManagedPath)/UnityEngine.CoreModule.dll</HintPath>
      <Private>false</Private>
    </Reference>
  </ItemGroup>

</Project>
```

**Important**: The `OldWorldPath` environment variable must be set when building. See the build section below.

## Step 2: Create ModInfo.xml

Every mod needs a `ModInfo.xml` manifest:

```xml
<?xml version="1.0"?>
<ModInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <displayName>My Awesome Mod</displayName>
  <description>Description of what your mod does.</description>
  <modpicture>MyMod.png</modpicture>
  <author>YourName</author>
  <modversion>1.0.0</modversion>
  <modbuild>1.0.81098</modbuild>
  <tags>GameInfo</tags>
  <singlePlayer>true</singlePlayer>
  <multiplayer>false</multiplayer>
  <scenario>false</scenario>
  <scenarioToggle>false</scenarioToggle>
  <blocksMods>false</blocksMods>
  <modDependencies />
  <modIncompatibilities />
  <modWhitelist />
  <gameContentRequired>NONE</gameContentRequired>
</ModInfo>
```

### Key Fields

| Field | Description |
|-------|-------------|
| `displayName` | Shown in the Mod Manager |
| `description` | Supports Steam BBCode formatting |
| `modpicture` | Image file shown in Mod Manager (place in mod folder) |
| `modversion` | Semantic version (e.g., 1.0.0) |
| `modbuild` | Game version this was built for |
| `tags` | Category: GameInfo, Character, Map, etc. |
| `singlePlayer` | Enable for single-player games |
| `multiplayer` | Enable for multiplayer (requires careful design) |
| `blocksMods` | If true, prevents other mods from loading |

### Publishing Fields (added automatically by platforms)

When publishing to Steam Workshop or mod.io, these fields are added:

```xml
<modplatform>Modio</modplatform>
<modioID>1234567</modioID>
<modioFileID>0</modioFileID>
<workshopOwnerID>76561199012345678</workshopOwnerID>
<workshopFileID>1234567890</workshopFileID>
```

---

## Approach 1: GameFactory Override (Exclusive)

The GameFactory pattern lets you replace entire game classes. This is how official scenarios work.

**Limitation**: Only ONE mod can use this approach at a time.

### How It Works

1. Create a custom `GameFactory` that overrides creation methods
2. Create custom classes that inherit from base game classes
3. The game uses your factory to instantiate all objects

### Example: Custom PlayerAI

```csharp
using TenCrowns.GameCore;

namespace MyMod
{
    public class MyModGameFactory : GameFactory
    {
        public override Player.PlayerAI CreatePlayerAI()
        {
            return new MyModPlayerAI();
        }

        // Override other creation methods as needed:
        // CreatePlayer(), CreateCity(), CreateUnit(), CreateUnitAI(), etc.
    }

    public class MyModPlayerAI : Player.PlayerAI
    {
        public override int getWarOfferPercent(PlayerType eOtherPlayer,
            bool bDeclare = true, bool bPreparedOnly = false, bool bCurrentPlayer = true)
        {
            int basePercent = base.getWarOfferPercent(eOtherPlayer, bDeclare, bPreparedOnly, bCurrentPlayer);

            // Example: boost AI-vs-AI war chance
            Player pOtherPlayer = game.player(eOtherPlayer);
            if (!pOtherPlayer.isHuman() && basePercent > 0 && bDeclare)
            {
                basePercent = basePercent * 3 / 2;  // +50%
            }

            return infos.utils().range(basePercent, 0, 100);
        }
    }
}
```

### Registering Your Factory

In your mod entry point, set the factory on ModSettings:

```csharp
public override void Initialize(ModSettings modSettings)
{
    base.Initialize(modSettings);
    modSettings.Factory = new MyModGameFactory();
}
```

### Available Factory Methods

| Method | Creates |
|--------|---------|
| `CreateGame()` | Game instance |
| `CreatePlayer()` | Player instance |
| `CreatePlayerAI()` | Player.PlayerAI instance |
| `CreateCity()` | City instance |
| `CreateUnit()` | Unit instance |
| `CreateUnitAI()` | Unit.UnitAI instance |
| `CreateTile()` | Tile instance |
| `CreateClientUI()` | ClientUI instance |
| `CreateInfoHelpers()` | InfoHelpers instance |
| `CreateHelpText()` | HelpText instance |

See `Reference/Source/Mods/Greece3/` for a complete example.

---

## Approach 2: Harmony Patching (Recommended for Compatibility)

Harmony is a .NET library that patches methods at runtime without replacing entire classes. Multiple Harmony mods can coexist if they patch different methods.

**Reference**: See [dales.world/HarmonyDLLs.html](https://dales.world/HarmonyDLLs.html) for detailed tutorial.

### Basic Structure

```csharp
using System;
using HarmonyLib;
using TenCrowns.AppCore;
using TenCrowns.GameCore;
using UnityEngine;

namespace MyMod
{
    public class MyMod : ModEntryPointAdapter
    {
        private static Harmony _harmony;
        private const string HarmonyId = "com.yourname.mymod";

        public override void Initialize(ModSettings modSettings)
        {
            base.Initialize(modSettings);

            try
            {
                _harmony = new Harmony(HarmonyId);
                _harmony.PatchAll();
                Debug.Log("[MyMod] Harmony patches applied");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[MyMod] Failed to apply patches: {ex}");
            }
        }

        public override void Shutdown()
        {
            _harmony?.UnpatchAll(HarmonyId);
            base.Shutdown();
        }
    }
}
```

### Patch Types

#### Prefix - Runs BEFORE the original method

```csharp
[HarmonyPatch(typeof(Player.PlayerAI), nameof(Player.PlayerAI.getWarOfferPercent))]
public static class WarOfferPatch
{
    // Return false to skip the original method entirely
    // __instance is the object the method is called on
    static bool Prefix(Player.PlayerAI __instance, PlayerType eOtherPlayer, ref int __result)
    {
        // Example: Force 100% war chance against specific nation
        if (__instance.game.player(eOtherPlayer).getNation() == NationType.ROME)
        {
            __result = 100;
            return false;  // Skip original method
        }
        return true;  // Run original method
    }
}
```

#### Postfix - Runs AFTER the original method

```csharp
[HarmonyPatch(typeof(Player.PlayerAI), nameof(Player.PlayerAI.getWarOfferPercent))]
public static class WarOfferPatch
{
    // __result is the return value (use ref to modify it)
    static void Postfix(Player.PlayerAI __instance, PlayerType eOtherPlayer,
        bool bDeclare, ref int __result)
    {
        // Only modify AI-vs-AI, not AI-vs-human
        Player pOtherPlayer = __instance.game.player(eOtherPlayer);
        if (pOtherPlayer.isHuman())
            return;

        if (__result > 0 && bDeclare)
        {
            __result = __result * 3 / 2;
            __result = Math.Min(__result, 100);
        }
    }
}
```

### Patching Overloaded Methods

Specify parameter types to patch a specific overload:

```csharp
[HarmonyPatch(typeof(Player.PlayerAI),
    nameof(Player.PlayerAI.getWarOfferPercent),
    new Type[] { typeof(PlayerType), typeof(bool), typeof(bool), typeof(bool) })]
public static class WarOfferPlayerPatch
{
    static void Postfix(ref int __result) { /* ... */ }
}

[HarmonyPatch(typeof(Player.PlayerAI),
    nameof(Player.PlayerAI.getWarOfferPercent),
    new Type[] { typeof(TribeType) })]
public static class WarOfferTribePatch
{
    static void Postfix(ref int __result) { /* ... */ }
}
```

### Harmony Notes

- Only ONE mod can patch any specific method - conflicts occur otherwise
- Use liberal logging during development
- Always include null checks - Old World uses parallel processing

---

## Step 3: Create the Entry Point

Your mod must extend `ModEntryPointAdapter`. Create `Source/MyMod.cs`:

```csharp
using System;
using HarmonyLib;
using TenCrowns.AppCore;
using TenCrowns.GameCore;
using UnityEngine;

namespace MyMod
{
    public class MyMod : ModEntryPointAdapter
    {
        private static Harmony _harmony;
        private const string HarmonyId = "com.yourname.mymod";

        public override void Initialize(ModSettings modSettings)
        {
            base.Initialize(modSettings);

            try
            {
                _harmony = new Harmony(HarmonyId);
                _harmony.PatchAll();
                Debug.Log("[MyMod] Initialized");
            }
            catch (Exception ex)
            {
                Debug.LogError($"[MyMod] Failed to initialize: {ex}");
            }
        }

        public override void Shutdown()
        {
            _harmony?.UnpatchAll(HarmonyId);
            base.Shutdown();
        }

        public override void OnGameServerReady()
        {
            Debug.Log("[MyMod] Game started or loaded");
        }

        public override void OnNewTurnServer()
        {
            // Called when a turn ends
        }

        public override void OnClientUpdate()
        {
            // Called every frame - use sparingly!
        }
    }
}
```

## Available Lifecycle Hooks

| Method | When Called | Use Case |
|--------|-------------|----------|
| `Initialize()` | Mod loaded | Setup, Harmony patches, factory registration |
| `Shutdown()` | Mod unloaded | Cleanup, unpatch Harmony |
| `OnGameServerReady()` | Game starts/loads | Initialize game-dependent state |
| `OnNewTurnServer()` | Turn ends | React to game state changes |
| `OnClientUpdate()` | Every frame | Continuous processing (use sparingly) |

---

## Accessing Game Data

### The Assembly-CSharp Constraint

Old World blocks mods from directly referencing `Assembly-CSharp.dll`. You cannot access `AppMain.gApp.Client.Game` directly.

**Solution**: Use runtime reflection.

```csharp
using System;
using System.Reflection;
using TenCrowns.GameCore;
using UnityEngine;

public partial class MyMod : ModEntryPointAdapter
{
    private static Type _appMainType;
    private static FieldInfo _gAppField;
    private static PropertyInfo _clientProperty;
    private static PropertyInfo _gameProperty;
    private static bool _reflectionInitialized;

    private void InitializeReflection()
    {
        if (_reflectionInitialized) return;

        foreach (var assembly in AppDomain.CurrentDomain.GetAssemblies())
        {
            if (assembly.GetName().Name == "Assembly-CSharp")
            {
                _appMainType = assembly.GetType("AppMain");
                break;
            }
        }

        if (_appMainType != null)
        {
            _gAppField = _appMainType.GetField("gApp",
                BindingFlags.Public | BindingFlags.Static);
            _clientProperty = _appMainType.GetProperty("Client",
                BindingFlags.Public | BindingFlags.Instance);

            if (_clientProperty != null)
            {
                var clientType = _clientProperty.PropertyType;
                _gameProperty = clientType.GetProperty("Game",
                    BindingFlags.Public | BindingFlags.Instance);
            }
        }

        _reflectionInitialized = true;
    }

    private Game GetGame()
    {
        InitializeReflection();

        var appMain = _gAppField?.GetValue(null);
        if (appMain == null) return null;

        var client = _clientProperty?.GetValue(appMain);
        if (client == null) return null;

        return _gameProperty?.GetValue(client) as Game;
    }
}
```

### Working with Game Types

```csharp
public override void OnNewTurnServer()
{
    Game game = GetGame();
    if (game == null) return;

    int turn = game.getTurn();
    Infos infos = game.infos();

    foreach (Player player in game.getPlayers())
    {
        if (player == null) continue;

        // Use mzType for string identifiers (enums return numbers)
        string nation = infos.nation(player.getNation()).mzType;  // "NATION_ROME"

        int food = player.getYieldStockpileWhole(infos.Globals.YIELD_FOOD);
        int gold = player.getYieldStockpileWhole(infos.Globals.YIELD_MONEY);

        Debug.Log($"[MyMod] {nation}: Food={food}, Gold={gold}");
    }
}
```

---

## Building Your Mod

### Environment Setup

Create a `.env` file (don't commit this):

```bash
# macOS
OLDWORLD_PATH="$HOME/Library/Application Support/Steam/steamapps/common/Old World"
OLDWORLD_MODS_PATH="$HOME/Library/Application Support/OldWorld/Mods"

# Windows
OLDWORLD_PATH="C:\Program Files (x86)\Steam\steamapps\common\Old World"
OLDWORLD_MODS_PATH="%USERPROFILE%\Documents\My Games\OldWorld\Mods"

# Linux
OLDWORLD_PATH="$HOME/.steam/steam/steamapps/common/Old World"
OLDWORLD_MODS_PATH="$HOME/.local/share/OldWorld/Mods"
```

### Build Script (macOS/Linux)

Create `deploy.sh`:

```bash
#!/bin/bash
set -e

source .env

MOD_NAME="MyMod"
MOD_DIR="$OLDWORLD_MODS_PATH/$MOD_NAME"

echo "Building..."
export OldWorldPath="$OLDWORLD_PATH"
dotnet build -c Release

echo "Deploying to $MOD_DIR..."
mkdir -p "$MOD_DIR"
cp ModInfo.xml "$MOD_DIR/"
cp bin/$MOD_NAME.dll "$MOD_DIR/"

# Copy Harmony DLL from NuGet cache
HARMONY_DLL="$HOME/.nuget/packages/lib.harmony/2.4.2/lib/net472/0Harmony.dll"
if [ -f "$HARMONY_DLL" ]; then
    cp "$HARMONY_DLL" "$MOD_DIR/"
fi

echo "Done! Enable the mod in Old World's Mod Manager."
```

### Build Script (Windows PowerShell)

Create `deploy.ps1`:

```powershell
$ErrorActionPreference = "Stop"

# Load .env
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $name = $matches[1]
        $value = $matches[2] -replace '^"(.*)"$', '$1'
        $value = [Environment]::ExpandEnvironmentVariables($value)
        Set-Item -Path "Env:$name" -Value $value
    }
}

$ModName = "MyMod"
$ModDir = "$env:OLDWORLD_MODS_PATH\$ModName"

Write-Host "Building..."
$env:OldWorldPath = $env:OLDWORLD_PATH
dotnet build -c Release

Write-Host "Deploying to $ModDir..."
New-Item -ItemType Directory -Force -Path $ModDir | Out-Null
Copy-Item ModInfo.xml $ModDir
Copy-Item bin\$ModName.dll $ModDir

# Copy Harmony DLL from NuGet cache
$HarmonyDll = "$env:USERPROFILE\.nuget\packages\lib.harmony\2.4.2\lib\net472\0Harmony.dll"
if (Test-Path $HarmonyDll) {
    Copy-Item $HarmonyDll $ModDir
}

Write-Host "Done!"
```

---

## Testing Your Mod

### Manual Testing

1. Run `./deploy.sh` (or `.\deploy.ps1` on Windows)
2. Launch Old World
3. Go to **Mod Manager** and enable your mod
4. Start or load a game
5. Check the game log for your debug messages

### Log Location

- **Windows**: `%USERPROFILE%\AppData\LocalLow\Mohawk Games\Old World\Player.log`
- **macOS**: `~/Library/Logs/Mohawk Games/Old World/Player.log`
- **Linux**: `~/.config/unity3d/Mohawk Games/Old World/Player.log`

### Headless Mode Testing

Old World supports headless mode for automated testing:

```bash
# macOS
"$OLDWORLD_PATH/OldWorld.app/Contents/MacOS/OldWorld" \
    -batchmode -nographics \
    "/path/to/save.zip" \
    -turns 2

# Windows
"C:\path\to\Old World\OldWorld.exe" ^
    -batchmode -nographics ^
    "C:\path\to\save.zip" ^
    -turns 2
```

---

## Tips and Gotchas

1. **Never reference Assembly-CSharp directly** - Use reflection as shown above

2. **Game may be null** - During menus, loading screens, or between sessions

3. **Use mzType for strings** - Enum `.ToString()` returns numbers

4. **Null safety is critical** - Old World uses parallel processing; always check for null

5. **GameFactory is exclusive** - Only one mod can override it

6. **Harmony patches conflict** - Only one mod per method

7. **Check the game source** - `Reference/Source/` contains decompiled code for reference

8. **Harmony 2.4.2+** - Required for Apple Silicon Mac support

---

## Further Resources

- **[dales.world](https://dales.world)** - Authoritative Old World modding tutorials
  - [Putting It All Together](https://dales.world/PuttingAllTogether.html) - GameFactory approach
  - [Harmony DLLs](https://dales.world/HarmonyDLLs.html) - Harmony patching guide
- **Old World Discord** - Official modding support channel
- **Reference Source** - `Reference/Source/` in game folder contains decompiled code
- **Example Mods** - `Reference/Source/Mods/Greece3/` shows complete scenario mod
