import glob

# 1. Исправляем AndroidManifest.xml для перехвата "Поделиться"
manifest_path = "android/app/src/main/AndroidManifest.xml"
with open(manifest_path, "r") as f:
    content = f.read()

intent_filter = """
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:mimeType="text/plain" />
    </intent-filter>
"""
if "action.SEND" not in content:
    content = content.replace("</activity>", intent_filter + "\n            </activity>", 1)
    with open(manifest_path, "w") as f:
        f.write(content)

# 2. Обновляем MainActivity.java для передачи ссылки в WebView
files = glob.glob("android/app/src/main/java/**/MainActivity.java", recursive=True)
if files:
    with open(files[0], "w") as f:
        f.write("""package com.tvremote.app;

import android.content.Intent;
import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        handleIntent(getIntent());
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        handleIntent(intent);
    }

    private void handleIntent(Intent intent) {
        String action = intent.getAction();
        String type = intent.getType();
        if (Intent.ACTION_SEND.equals(action) && type != null) {
            if ("text/plain".equals(type)) {
                String sharedText = intent.getStringExtra(Intent.EXTRA_TEXT);
                if (sharedText != null && bridge != null && bridge.getWebView() != null) {
                    final String url = "file:///android_asset/public/index.html?url=" + android.net.Uri.encode(sharedText);
                    runOnUiThread(() -> bridge.getWebView().loadUrl(url));
                }
            }
        }
    }
}
""")
