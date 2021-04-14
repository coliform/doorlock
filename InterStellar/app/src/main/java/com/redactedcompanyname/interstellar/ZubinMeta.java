package com.RedactedCompanyName.interstellar;

import android.content.SharedPreferences;

import com.google.firebase.auth.FirebaseUser;

import java.util.List;

import com.RedactedCompanyName.interstellar.pojo.Machine;

import com.RedactedCompanyName.sdk.RedactedCompanyNameSdk;

public class ZubinMeta {
    static FirebaseUser user = null;
    static String uid = "";
    static String token = "";
    static String fcm = "";
    static String name = "";
    static List<Machine> machines;
    static RestClient client;
    static int currentlyActive = 0;
    static SharedPreferences sharedPreferences;
    static SharedPreferences.Editor editor;
    static RedactedCompanyNameSdk sdk;

    static void saveZubin() {

    }
}
