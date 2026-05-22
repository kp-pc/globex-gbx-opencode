package com.globex.gbx;

import android.content.Context;
import android.content.SharedPreferences;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;

import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.security.MessageDigest;
import java.security.SecureRandom;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

public class PinManager {
    private static final String PREFS_NAME = "globex_pin_store";
    private static final String KEY_PIN_HASH = "pin_hash";
    private static final String KEY_PIN_SALT = "pin_salt";
    private static final String KEY_PIN_ENABLED = "pin_enabled";

    private final SharedPreferences prefs;

    public PinManager(Context context) {
        this.prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
    }

    public void setPin(String pin) {
        byte[] salt = new byte[16];
        new SecureRandom().nextBytes(salt);
        String hash = hashPin(pin, salt);
        prefs.edit()
                .putString(KEY_PIN_HASH, hash)
                .putString(KEY_PIN_SALT, Base64.encodeToString(salt, Base64.NO_WRAP))
                .putBoolean(KEY_PIN_ENABLED, true)
                .apply();
    }

    public boolean verifyPin(String pin) {
        String storedHash = prefs.getString(KEY_PIN_HASH, null);
        String storedSalt = prefs.getString(KEY_PIN_SALT, null);
        if (storedHash == null || storedSalt == null) return false;
        byte[] salt = Base64.decode(storedSalt, Base64.NO_WRAP);
        return hashPin(pin, salt).equals(storedHash);
    }

    public boolean isEnabled() {
        return prefs.getBoolean(KEY_PIN_ENABLED, false);
    }

    public void disable() {
        prefs.edit()
                .remove(KEY_PIN_HASH)
                .remove(KEY_PIN_SALT)
                .putBoolean(KEY_PIN_ENABLED, false)
                .apply();
    }

    public int getPinAttempts() {
        return prefs.getInt("pin_attempts", 0);
    }

    public void incrementPinAttempts() {
        int attempts = getPinAttempts() + 1;
        prefs.edit().putInt("pin_attempts", attempts).apply();
    }

    public void resetPinAttempts() {
        prefs.edit().putInt("pin_attempts", 0).apply();
    }

    public boolean isLockedOut() {
        return getPinAttempts() >= 5;
    }

    private String hashPin(String pin, byte[] salt) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            md.update(salt);
            byte[] hash = md.digest(pin.getBytes(StandardCharsets.UTF_8));
            for (int i = 0; i < 1000; i++) {
                md.update(hash);
                hash = md.digest(pin.getBytes(StandardCharsets.UTF_8));
            }
            return Base64.encodeToString(hash, Base64.NO_WRAP);
        } catch (Exception e) {
            throw new RuntimeException("PIN hashing failed", e);
        }
    }
}
