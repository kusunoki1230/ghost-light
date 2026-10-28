// Adjusts the generated Android project: microphone + speech permissions, fixed signing key,
// version number from the CI run so each new APK installs over the old one.
import fs from "node:fs";

const manifestPath = "android/app/src/main/AndroidManifest.xml";
let m = fs.readFileSync(manifestPath, "utf8");
if (!m.includes("RECORD_AUDIO")) {
  m = m.replace("</manifest>", `    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <queries>
        <intent><action android:name="android.speech.RecognitionService" /></intent>
        <intent><action android:name="android.intent.action.TTS_SERVICE" /></intent>
    </queries>
</manifest>`);
  fs.writeFileSync(manifestPath, m);
}

const gradlePath = "android/app/build.gradle";
let g = fs.readFileSync(gradlePath, "utf8");
const run = parseInt(process.env.GITHUB_RUN_NUMBER || "1", 10);
g = g.replace(/versionCode \d+/, `versionCode ${run}`).replace(/versionName "[^"]*"/, `versionName "1.0.${run}"`);
if (!g.includes("signingConfigs")) {
  g = g.replace(/buildTypes \{/, `signingConfigs {
        release {
            storeFile file("../../signing/ghostlight.keystore")
            storePassword "ghostlight"
            keyAlias "ghostlight"
            keyPassword "ghostlight"
        }
    }
    buildTypes {`);
  g = g.replace(/release \{\n(\s*)minifyEnabled false/, (s, sp) => `release {\n${sp}signingConfig signingConfigs.release\n${sp}minifyEnabled false`);
}
fs.writeFileSync(gradlePath, g);
console.log("android patched, versionCode", run, g.includes("signingConfig signingConfigs.release") ? "signed" : "WARNING: signing not applied");
