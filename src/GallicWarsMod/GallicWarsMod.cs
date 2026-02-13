using System.Collections.Generic;
using System.Reflection;
using HarmonyLib;
using TenCrowns.AppCore;
using TenCrowns.GameCore;
using UnityEngine;

namespace GallicWars
{
    /// <summary>
    /// Harmony patch that fixes a game bug where AppMain.StartGame() copies the
    /// controller's CRC to the server BEFORE Infos.PreCreateGame() runs. PreCreateGame
    /// then fixes the CRC on the controller's ModPath (canceling the StrictModeDeferred
    /// asymmetry), but the server's copy is already stale. This patch re-copies the
    /// controller's CRC after PreCreateGame has run.
    /// </summary>
    public class GallicWarsMod : ModEntryPointAdapter
    {
        private static Harmony _harmony;
        private const string HarmonyId = "com.gallicwars.crcfix";

        public override void Initialize(ModSettings modSettings)
        {
            base.Initialize(modSettings);

            if (_harmony != null) return; // Already patched (DLL loaded multiple times)

            _harmony = new Harmony(HarmonyId);

            // Postfix on ModSettings.CreateServerGame (TenCrowns.GameCore — direct reference)
            // After PreCreateGame has updated the controller's CRC, re-copy it to the server.
            _harmony.Patch(
                AccessTools.Method(typeof(ModSettings), nameof(ModSettings.CreateServerGame)),
                postfix: new HarmonyMethod(AccessTools.Method(
                    typeof(CreateServerGamePatch), nameof(CreateServerGamePatch.Postfix)))
            );

            // Postfix on Tile.setImprovement: check fort pings and complete goal
            _harmony.Patch(
                AccessTools.Method(typeof(Tile), "setImprovement"),
                postfix: new HarmonyMethod(AccessTools.Method(
                    typeof(FortPingPatch), nameof(FortPingPatch.Postfix)))
            );

            Debug.Log("[GallicWars] CRC fix and fort ping tracking applied");
        }

        public override void Shutdown()
        {
            _harmony?.UnpatchAll(HarmonyId);
            _harmony = null;
            base.Shutdown();
        }
    }

    /// <summary>
    /// Postfix on ModSettings.CreateServerGame().
    ///
    /// When a scenario mod is loaded, the Infos object is created by the controller's
    /// ModSettings (strict mode ON). AppMain.StartGame() reuses this Infos for the
    /// server but copies the controller's CRC BEFORE calling CreateServerGame.
    ///
    /// Inside CreateServerGame, Infos.PreCreateGame() runs and XORs deferred file CRCs
    /// into the controller's ModPath (via the Infos's internal mModSettings reference).
    /// This cancels the asymmetry from ReadInfoListTypes. But the server's ModPath still
    /// has the stale pre-PreCreateGame CRC.
    ///
    /// This postfix re-copies the controller's (now-fixed) CRC to the server's ModPath.
    /// </summary>
    public static class CreateServerGamePatch
    {
        private static readonly FieldInfo InfosModSettingsField =
            typeof(Infos).GetField("mModSettings", BindingFlags.NonPublic | BindingFlags.Instance);

        public static void Postfix(ModSettings __instance)
        {
            try
            {
                if (InfosModSettingsField == null)
                {
                    Debug.LogError("[GallicWars] Could not find Infos.mModSettings field");
                    return;
                }

                // Get the controller's ModSettings from the reused Infos object
                var controllerModSettings = InfosModSettingsField.GetValue(__instance.Infos) as ModSettings;
                if (controllerModSettings == null || controllerModSettings == __instance)
                    return; // Not reusing Infos, nothing to fix

                int controllerCrc = controllerModSettings.ModPath.GetCRC();
                int serverCrc = __instance.ModPath.GetCRC();

                if (controllerCrc == serverCrc)
                    return; // Already in sync

                // Copy the controller's updated CRC to the server's ModPath via reflection
                // (IModPath doesn't expose a CRC setter, only the concrete ModPath class does)
                var crcProperty = __instance.ModPath.GetType().GetProperty("CRC");
                if (crcProperty == null)
                {
                    Debug.LogError("[GallicWars] Could not find ModPath.CRC property");
                    return;
                }

                crcProperty.SetValue(__instance.ModPath, controllerCrc);
                Debug.Log("[GallicWars] Synced server CRC: " + serverCrc + " -> " + controllerCrc);
            }
            catch (System.Exception ex)
            {
                Debug.LogError("[GallicWars] CreateServerGame postfix error: " + ex.Message);
            }
        }
    }

    /// <summary>
    /// Postfix on Tile.setImprovement. Completes the "Fortify the Rhone" goal
    /// when all 4 target tiles along the Rhone have active forts.
    ///
    /// Target tiles are computed from coordinates using the runtime map width,
    /// matching the FORT_PING_TILES in generate_scenario.py.
    /// </summary>
    public static class FortPingPatch
    {
        // Fort target coordinates — must match FORT_PING_TILES in generate_scenario.py
        private static readonly int[][] FortCoords = new int[][] {
            new int[] { 13, 14 },
            new int[] { 14, 15 },
            new int[] { 15, 15 },
            new int[] { 15, 16 },
        };

        private static Game _cachedGame;
        private static HashSet<int> _targetTiles;
        private static HashSet<int> _fortedTargets;
        private static ImprovementType _fortType;
        private static GoalType _goalType;

        public static void Postfix(Tile __instance, ImprovementType eNewImprovement)
        {
            try
            {
                var game = __instance.game();

                // Initialize or re-initialize on game change
                if (game != _cachedGame)
                {
                    _cachedGame = game;
                    _fortType = game.infos().getType<ImprovementType>("IMPROVEMENT_FORT");
                    _goalType = game.infos().getType<GoalType>("GOAL_GW1_FORTIFY_RHONE");

                    int mapWidth = game.getWidth();
                    _targetTiles = new HashSet<int>();
                    foreach (var coord in FortCoords)
                        _targetTiles.Add(coord[1] * mapWidth + coord[0]);
                    _fortedTargets = new HashSet<int>();

                    Debug.Log("[GallicWars] Fort targets: " + _targetTiles.Count
                        + " tiles (width=" + mapWidth + ")");
                }

                // Quick exit: not a fort or not on a target tile
                if (eNewImprovement != _fortType) return;
                if (!_targetTiles.Contains(__instance.getID())) return;

                // Track this target as having a fort placed
                _fortedTargets.Add(__instance.getID());
                Debug.Log("[GallicWars] Fort placed on target " + __instance.getID()
                    + " (" + _fortedTargets.Count + "/" + _targetTiles.Count + ")");

                if (_fortedTargets.Count < _targetTiles.Count) return;

                // All target tiles have forts — complete the goal
                Player player = game.player((PlayerType)0);
                if (player != null)
                {
                    player.finishGoalType(_goalType, PlayerType.NONE, TribeType.NONE, null, false);
                    Debug.Log("[GallicWars] Fortify Rhone goal completed!");
                }
            }
            catch (System.Exception ex)
            {
                Debug.LogError("[GallicWars] FortPingPatch error: " + ex.Message);
            }
        }
    }
}
