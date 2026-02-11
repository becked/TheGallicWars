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

            Debug.Log("[GallicWars] CRC fix applied");
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
}
