package com.globex.gbx;

import android.content.Context;
import android.content.SharedPreferences;

import androidx.biometric.BiometricManager;
import androidx.biometric.BiometricPrompt;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.FragmentActivity;

public class BiometricHelper {
    private static final String PREFS_NAME = "globex_biometric_prefs";
    private static final String KEY_BIOMETRIC_ENABLED = "biometric_enabled";

    private final Context context;
    private final SharedPreferences prefs;

    public BiometricHelper(Context context) {
        this.context = context.getApplicationContext();
        this.prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
    }

    public boolean isHardwareAvailable() {
        BiometricManager bm = BiometricManager.from(context);
        int result = bm.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG |
                BiometricManager.Authenticators.BIOMETRIC_WEAK);
        return result == BiometricManager.BIOMETRIC_SUCCESS;
    }

    public boolean canAuthenticate() {
        BiometricManager bm = BiometricManager.from(context);
        int result = bm.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG |
                BiometricManager.Authenticators.DEVICE_CREDENTIAL);
        return result == BiometricManager.BIOMETRIC_SUCCESS;
    }

    public boolean isEnabled() {
        return prefs.getBoolean(KEY_BIOMETRIC_ENABLED, false);
    }

    public void setEnabled(boolean enabled) {
        prefs.edit().putBoolean(KEY_BIOMETRIC_ENABLED, enabled).apply();
    }

    public void authenticate(FragmentActivity activity, String title, String subtitle,
                             BiometricPrompt.AuthenticationCallback callback) {
        BiometricPrompt.PromptInfo promptInfo = new BiometricPrompt.PromptInfo.Builder()
                .setTitle(title != null ? title : "Authenticate")
                .setSubtitle(subtitle != null ? subtitle : "Verify your identity")
                .setAllowedAuthenticators(
                        BiometricManager.Authenticators.BIOMETRIC_STRONG |
                                BiometricManager.Authenticators.DEVICE_CREDENTIAL)
                .build();

        BiometricPrompt prompt = new BiometricPrompt(activity,
                ContextCompat.getMainExecutor(activity), callback);
        prompt.authenticate(promptInfo);
    }

    public void authenticateForSensitive(FragmentActivity activity,
                                         BiometricPrompt.AuthenticationCallback callback) {
        authenticate(activity, "Wallet Access", "Authenticate to access your wallet", callback);
    }

    public void authenticateForSend(FragmentActivity activity,
                                    BiometricPrompt.AuthenticationCallback callback) {
        authenticate(activity, "Confirm Transaction", "Authenticate to send GBX", callback);
    }
}
