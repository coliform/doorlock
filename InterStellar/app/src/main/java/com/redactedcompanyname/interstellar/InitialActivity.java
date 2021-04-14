package com.RedactedCompanyName.interstellar;

import androidx.annotation.NonNull;
import androidx.appcompat.app.ActionBar;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.Window;
import android.widget.TextView;

import com.firebase.ui.auth.AuthUI;
import com.firebase.ui.auth.IdpResponse;
import com.google.android.gms.tasks.OnCompleteListener;
import com.google.android.gms.tasks.OnSuccessListener;
import com.google.android.gms.tasks.Task;
import com.google.firebase.auth.FirebaseAuth;
import com.google.firebase.auth.GetTokenResult;
import com.google.firebase.iid.FirebaseInstanceId;
import com.google.firebase.iid.InstanceIdResult;
import com.RedactedCompanyName.sdk.RedactedCompanyNameSdk;

import org.jetbrains.annotations.NotNull;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;

import com.RedactedCompanyName.interstellar.pojo.Machine;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Response;

public class InitialActivity extends AppCompatActivity {

    private static final String TAG = "InitialActivityTag";

    private static final int RC_SIGN_IN = 123;
    private TextView tv_status;
    private SharedPreferences sharedPreferences;
    private SharedPreferences.Editor editor;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getSupportActionBar().hide();
        setContentView(R.layout.activity_initial);

        ZubinMeta.sdk = RedactedCompanyNameSdk.getInstance(this);
        ZubinMeta.sdk.init("RedactedLicense");
        ZubinMeta.sdk.initUser("local");

        ActionBar actionBar = getSupportActionBar();
        actionBar.setTitle(R.string.w_loading);

        sharedPreferences = getSharedPreferences("userConfig", 0);
        editor = sharedPreferences.edit();
        ZubinMeta.sharedPreferences = sharedPreferences;
        ZubinMeta.editor = editor;
        RestClient.client = new OkHttpClient();

        tv_status = findViewById(R.id.tv_loading);

        tv_status.setText(getString(R.string.w_loading));
        authenticate();
    }

    private void authenticate() {
        //ZubinMeta.client = new RestClient();
        List<AuthUI.IdpConfig> providers = Arrays.asList(
                new AuthUI.IdpConfig.EmailBuilder().build(),
                new AuthUI.IdpConfig.GoogleBuilder().build());

// Create and launch sign-in intent
        startActivityForResult(
                AuthUI.getInstance()
                        .createSignInIntentBuilder()
                        .setAvailableProviders(providers)
                        .build(),
                RC_SIGN_IN);
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == RC_SIGN_IN) {
            IdpResponse response = IdpResponse.fromResultIntent(data);

            if (resultCode == RESULT_OK) {
                // Successfully signed in
                ZubinMeta.user = FirebaseAuth.getInstance().getCurrentUser();
                ZubinMeta.name = ZubinMeta.user.getDisplayName();
                ZubinMeta.uid = ZubinMeta.user.getUid();
                if (true) {
                    //tv_status.setText("Fetching UID...");
                    ZubinMeta.user.getIdToken(true).addOnCompleteListener(new OnCompleteListener<GetTokenResult>() {
                        public void onComplete(@NonNull Task<GetTokenResult> task) {
                            if (task.isSuccessful()) {
                                ZubinMeta.token = task.getResult().getToken();
                                Log.d(TAG, "Token is " + ZubinMeta.token);
                                editor.putString("token", ZubinMeta.token);
                                editor.commit();
                                //tv_status.setText("Fetching FCM...");
                                FirebaseInstanceId.getInstance().getInstanceId().addOnSuccessListener(InitialActivity.this, new OnSuccessListener<InstanceIdResult>() {
                                    @Override
                                    public void onSuccess(InstanceIdResult instanceIdResult) {
                                        ZubinMeta.fcm = instanceIdResult.getToken();
                                        editor.putString("fcm", ZubinMeta.fcm);
                                        editor.commit();
                                        registerUser();
                                    }
                                });
                            } else {
                                // Handle error -> task.getException();
                            }
                        }
                    });
                } else {
                    ZubinMeta.token = sharedPreferences.getString("uid", "");
                    ZubinMeta.fcm = sharedPreferences.getString("fcm", "");
                    registerUser();
                }
            } else {
                // Sign in failed. If response is null the user canceled the
                // sign-in flow using the back button. Otherwise check
                // response.getError().getErrorCode() and handle the error.
                // ...
            }
        }
    }

    protected void registerUser() {
        //tv_status.setText("Registering...");
        RestClient.registerUser(new Callback() {
            @Override
            public void onFailure(@NotNull Call call, @NotNull IOException e) {
                //tv_status.setText("Registration failed");
                Log.d(TAG, "Failed");
                Log.d(TAG, e.toString());
            }

            @Override
            public void onResponse(@NotNull Call call, @NotNull Response response) throws IOException {
                String json = response.body().string();
                Log.d(TAG, json);
                JSONObject obj;
                try {
                    obj = new JSONObject(json);
                } catch (JSONException e) {
                    Log.e(TAG, "Too bad, so sad");
                    Log.e(TAG, json);
                    return;
                }
                Iterator<String> maids = obj.keys();
                ZubinMeta.machines = new ArrayList<>();
                while (maids.hasNext()) {
                    String maid = maids.next();
                    Log.d(TAG, "Maid " + maid);
                    Machine machine = new Machine();
                    try {
                        machine.maid = maid;
                        machine.name = (String)(((JSONObject)obj.get(maid)).get("name"));
                        machine.expires = (Integer)(((JSONObject)obj.get(maid)).get("valid_until"));
                    } catch (JSONException e) {
                        Log.e(TAG, "Corrupt machine");
                        Log.e(TAG, json);
                    }
                    ZubinMeta.machines.add(machine);
                }
                editor.putString("registerResponse", json);
                editor.commit();
                InitialActivity.this.runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        startActivity(new Intent(getApplicationContext(), MainActivity.class));
                        finish();
                    }
                });
            }
        });
    }
}
