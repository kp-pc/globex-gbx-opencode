package com.globex.gbx;

import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.KeyEvent;
import android.view.View;
import android.view.WindowManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ProgressBar;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.biometric.BiometricPrompt;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.google.zxing.integration.android.IntentIntegrator;
import com.google.zxing.integration.android.IntentResult;

import org.json.JSONObject;

public class MainActivity extends AppCompatActivity {

    private WebView webView;
    private SwipeRefreshLayout swipeRefresh;
    private ProgressBar progressBar;
    private FrameLayout loadingOverlay;
    private SecureKeyStore secureKeyStore;
    private PinManager pinManager;
    private BiometricHelper biometricHelper;
    private boolean screenshotProtectionEnabled = false;

    private static final String PREFS_NAME = "globex_prefs";
    private static final String KEY_NODE_URL = "node_url";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webView);
        swipeRefresh = findViewById(R.id.swipeRefresh);
        progressBar = findViewById(R.id.progressBar);
        loadingOverlay = findViewById(R.id.loadingOverlay);

        secureKeyStore = new SecureKeyStore(this);
        pinManager = new PinManager(this);
        biometricHelper = new BiometricHelper(this);

        setupWebView();
        checkAppLock();
    }

    private void checkAppLock() {
        if (pinManager.isEnabled() && !pinManager.isLockedOut()) {
            if (biometricHelper.isEnabled() && biometricHelper.canAuthenticate()) {
                biometricHelper.authenticateForSensitive(this, new BiometricPrompt.AuthenticationCallback() {
                    @Override
                    public void onAuthenticationSucceeded(BiometricPrompt.AuthenticationResult result) {
                        loadNodeUrl();
                    }

                    @Override
                    public void onAuthenticationError(int errorCode, CharSequence errString) {
                        if (errorCode != BiometricPrompt.BIOMETRIC_ERROR_USER_CANCELED) {
                            finish();
                        } else {
                            showPinDialog();
                        }
                    }

                    @Override
                    public void onAuthenticationFailed() {
                        Toast.makeText(MainActivity.this, "Authentication failed", Toast.LENGTH_SHORT).show();
                    }
                });
            } else {
                showPinDialog();
            }
        } else if (pinManager.isLockedOut()) {
            Toast.makeText(this, "App locked. Too many failed PIN attempts.", Toast.LENGTH_LONG).show();
            finish();
        } else {
            loadNodeUrl();
        }
    }

    private void showPinDialog() {
        EditText input = new EditText(this);
        input.setInputType(android.text.InputType.TYPE_CLASS_NUMBER |
                android.text.InputType.TYPE_NUMBER_VARIATION_PASSWORD);

        new AlertDialog.Builder(this, android.R.style.Theme_Material_Dialog_Alert)
                .setTitle("Enter PIN")
                .setMessage("Enter your app lock PIN")
                .setView(input)
                .setPositiveButton("Unlock", (dialog, which) -> {
                    String pin = input.getText().toString();
                    if (pinManager.verifyPin(pin)) {
                        pinManager.resetPinAttempts();
                        loadNodeUrl();
                    } else {
                        pinManager.incrementPinAttempts();
                        if (pinManager.isLockedOut()) {
                            Toast.makeText(this, "Too many attempts. App locked.", Toast.LENGTH_LONG).show();
                            finish();
                        } else {
                            Toast.makeText(this, "Wrong PIN. Attempts remaining: " +
                                    (5 - pinManager.getPinAttempts()), Toast.LENGTH_SHORT).show();
                            showPinDialog();
                        }
                    }
                })
                .setNegativeButton("Exit", (dialog, which) -> finish())
                .setCancelable(false)
                .show();
    }

    private void setupWebView() {
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setDomStorageEnabled(true);
        webView.getSettings().setLoadWithOverviewMode(true);
        webView.getSettings().setUseWideViewPort(true);
        webView.getSettings().setBuiltInZoomControls(true);
        webView.getSettings().setDisplayZoomControls(false);
        webView.getSettings().setCacheMode(android.webkit.WebSettings.LOAD_NO_CACHE);
        webView.getSettings().setMixedContentMode(
                android.webkit.WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
        );

        webView.addJavascriptInterface(new SecurityBridge(), "Android");

        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                loadingOverlay.setVisibility(View.VISIBLE);
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                loadingOverlay.setVisibility(View.GONE);
                swipeRefresh.setRefreshing(false);
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                return false;
            }
        });

        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                progressBar.setProgress(newProgress);
                progressBar.setVisibility(newProgress < 100 ? View.VISIBLE : View.GONE);
            }
        });

        swipeRefresh.setOnRefreshListener(() -> webView.reload());
    }

    private void loadNodeUrl() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        String savedUrl = prefs.getString(KEY_NODE_URL, null);

        if (savedUrl != null) {
            webView.loadUrl(savedUrl);
        } else {
            showUrlDialog();
        }
    }

    private void showUrlDialog() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        String defaultUrl = prefs.getString(KEY_NODE_URL,
                getString(R.string.default_node_url));

        EditText input = new EditText(this);
        input.setText(defaultUrl);
        input.setSelectAllOnFocus(true);

        new AlertDialog.Builder(this)
                .setTitle("Connect to Node")
                .setMessage("Enter your Globex node URL:")
                .setView(input)
                .setPositiveButton("Connect", (dialog, which) -> {
                    String url = input.getText().toString().trim();
                    if (!url.isEmpty()) {
                        prefs.edit().putString(KEY_NODE_URL, url).apply();
                        webView.loadUrl(url);
                    }
                })
                .setNegativeButton("Cancel", (dialog, which) -> finish())
                .setCancelable(false)
                .show();
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
            webView.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        IntentResult result = IntentIntegrator.parseActivityResult(requestCode, resultCode, data);
        if (result != null) {
            if (result.getContents() != null) {
                String qrContent = result.getContents();
                webView.evaluateJavascript(
                        "javascript:window.onQRScanned('" + qrContent.replace("'", "\\'") + "')",
                        null
                );
            }
        } else {
            super.onActivityResult(requestCode, resultCode, data);
        }
    }

    // --- JavaScript Bridge ---

    private class SecurityBridge {

        // --- Screenshot Protection ---

        @JavascriptInterface
        public void enableScreenshotProtection() {
            runOnUiThread(() -> {
                screenshotProtectionEnabled = true;
                getWindow().setFlags(
                        WindowManager.LayoutParams.FLAG_SECURE,
                        WindowManager.LayoutParams.FLAG_SECURE
                );
            });
        }

        @JavascriptInterface
        public void disableScreenshotProtection() {
            runOnUiThread(() -> {
                screenshotProtectionEnabled = false;
                getWindow().clearFlags(WindowManager.LayoutParams.FLAG_SECURE);
            });
        }

        @JavascriptInterface
        public boolean isScreenshotProtected() {
            return screenshotProtectionEnabled;
        }

        // --- Secure Key Storage ---

        @JavascriptInterface
        public String storePrivateKey(String keyId, String privateKeyHex) {
            try {
                secureKeyStore.store("privkey_" + keyId, privateKeyHex);
                return "ok";
            } catch (Exception e) {
                return "error: " + e.getMessage();
            }
        }

        @JavascriptInterface
        public String getPrivateKey(String keyId) {
            try {
                String key = secureKeyStore.retrieve("privkey_" + keyId);
                return key != null ? key : "not_found";
            } catch (Exception e) {
                return "error: " + e.getMessage();
            }
        }

        @JavascriptInterface
        public boolean hasPrivateKey(String keyId) {
            return secureKeyStore.has("privkey_" + keyId);
        }

        @JavascriptInterface
        public void deletePrivateKey(String keyId) {
            secureKeyStore.delete("privkey_" + keyId);
        }

        // --- PIN Management ---

        @JavascriptInterface
        public boolean isPinEnabled() {
            return pinManager.isEnabled() && !pinManager.isLockedOut();
        }

        @JavascriptInterface
        public boolean isPinLockedOut() {
            return pinManager.isLockedOut();
        }

        @JavascriptInterface
        public int getPinAttempts() {
            return pinManager.getPinAttempts();
        }

        @JavascriptInterface
        public String setPin(String pin) {
            if (pin == null || pin.length() < 4 || pin.length() > 12) {
                return "error: PIN must be 4-12 digits";
            }
            if (!pin.matches("\\d+")) {
                return "error: PIN must contain only digits";
            }
            pinManager.setPin(pin);
            return "ok";
        }

        @JavascriptInterface
        public boolean verifyPin(String pin) {
            boolean valid = pinManager.verifyPin(pin);
            if (valid) {
                pinManager.resetPinAttempts();
            } else {
                pinManager.incrementPinAttempts();
            }
            return valid;
        }

        @JavascriptInterface
        public void disablePin() {
            pinManager.disable();
        }

        // --- Biometric Authentication ---

        @JavascriptInterface
        public boolean isBiometricAvailable() {
            return biometricHelper.isHardwareAvailable() && biometricHelper.canAuthenticate();
        }

        @JavascriptInterface
        public boolean isBiometricEnabled() {
            return biometricHelper.isEnabled();
        }

        @JavascriptInterface
        public void enableBiometric(boolean enabled) {
            biometricHelper.setEnabled(enabled);
        }

        @JavascriptInterface
        public void authenticateWithBiometric(final String callbackId) {
            runOnUiThread(() -> {
                if (!biometricHelper.canAuthenticate()) {
                    webView.evaluateJavascript(
                            "javascript:window.onBiometricResult('" + callbackId + "', false, 'Biometric not available')",
                            null
                    );
                    return;
                }
                biometricHelper.authenticateForSensitive(MainActivity.this,
                        new BiometricPrompt.AuthenticationCallback() {
                            @Override
                            public void onAuthenticationSucceeded(BiometricPrompt.AuthenticationResult result) {
                                webView.evaluateJavascript(
                                        "javascript:window.onBiometricResult('" + callbackId + "', true, '')",
                                        null
                                );
                            }

                            @Override
                            public void onAuthenticationError(int errorCode, CharSequence errString) {
                                webView.evaluateJavascript(
                                        "javascript:window.onBiometricResult('" + callbackId + "', false, '" +
                                                errString.toString().replace("'", "\\'") + "')",
                                        null
                                );
                            }

                            @Override
                            public void onAuthenticationFailed() {
                                webView.evaluateJavascript(
                                        "javascript:window.onBiometricResult('" + callbackId + "', false, 'Authentication failed')",
                                        null
                                );
                            }
                        });
            });
        }
    }
}
