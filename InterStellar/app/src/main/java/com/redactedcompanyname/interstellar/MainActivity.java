package com.RedactedCompanyName.interstellar;

import androidx.annotation.NonNull;
import androidx.appcompat.app.ActionBar;
import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentTransaction;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.util.Log;
import android.view.MenuItem;
import android.widget.Toast;

import com.google.android.material.bottomnavigation.BottomNavigationView;
import com.google.firebase.database.annotations.NotNull;
import com.google.zxing.integration.android.IntentIntegrator;
import com.google.zxing.integration.android.IntentResult;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

import com.RedactedCompanyName.interstellar.pojo.Machine;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Response;

public class MainActivity extends AppCompatActivity implements
        ControlFragment.OnFragmentInteractionListener,
        ScannerFragment.OnFragmentInteractionListener,
        SettingsFragment.OnFragmentInteractionListener {

    private final static String TAG = "MainActivityTag";

    private ActionBar toolbar;
    private ControlFragment controlFragment;
    private SettingsFragment settingsFragment;
    private ScannerFragment scannerFragment;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        toolbar = getSupportActionBar();

        BottomNavigationView navigation = (BottomNavigationView) findViewById(R.id.navigation);
        navigation.setOnNavigationItemSelectedListener(mOnNavigationItemSelectedListener);

        toolbar.setTitle(getString(R.string.app_name));
        controlFragment = new ControlFragment();
        settingsFragment = new SettingsFragment();
        scannerFragment = new ScannerFragment();
        if (ZubinMeta.machines.size() > 0) loadFragment(controlFragment);
        else loadFragment(scannerFragment);
    }

    private BottomNavigationView.OnNavigationItemSelectedListener mOnNavigationItemSelectedListener
            = new BottomNavigationView.OnNavigationItemSelectedListener() {

        @Override
        public boolean onNavigationItemSelected(@NonNull MenuItem item) {
            Fragment fragment;
            switch (item.getItemId()) {
                case R.id.navigation_shop:
                    if (ZubinMeta.machines.size() == 0) return false;
                    loadFragment(controlFragment);
                    return true;
                case R.id.navigation_gifts:
                    if (ZubinMeta.machines.size() == 0) return false;
                    loadFragment(settingsFragment);
                    return true;
                case R.id.navigation_cart:
                    loadFragment(scannerFragment);
                    return true;
            }
            return false;
        }
    };

    private void loadFragment(Fragment fragment) {
        // load fragment
        FragmentTransaction transaction = getSupportFragmentManager().beginTransaction();
        transaction.replace(R.id.frame_container, fragment);
        transaction.addToBackStack(null);
        transaction.commit();
    }

    @Override
    public void onControlFragmentInteraction(Uri uri) {

    }

    @Override
    public void onSettingsFragmentInteraction(int action) {
        switch (action) {
            case 1: {
                loadFragment(scannerFragment);
                break;
            }
            default: {

            }
        }
    }

    @Override
    public void onScannerFragmentInteraction(int action) {
        switch (action) {
            case 1: {
                IntentIntegrator integrator = new IntentIntegrator(this);
                //integrator.setDesiredBarcodeFormats(IntentIntegrator.ONE_D_CODE_TYPES);
                integrator.setPrompt("Scan a barcode");
                integrator.setBeepEnabled(false);
                integrator.setOrientationLocked(true);
                integrator.initiateScan();
            }
            default: {

            }
        }
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent intent) {
        super.onActivityResult(requestCode, resultCode, intent);
        IntentResult scanResult = IntentIntegrator.parseActivityResult(requestCode, resultCode, intent);
        if (scanResult != null) {
            final String maid = scanResult.getContents();
            for (int i = 0; i < ZubinMeta.machines.size(); i++) {
                if (ZubinMeta.machines.get(i).maid.equals(maid)) return;
            }
            Toast.makeText(this, "Adding...", Toast.LENGTH_SHORT).show();
            RestClient.addUserToMachine(new Callback() {
                @Override
                public void onFailure(@NotNull Call call, @NotNull IOException e) {
                    Log.d(TAG, "Failed");
                    Log.d(TAG, e.toString());
                    Toast.makeText(getApplicationContext(), getString(R.string.cn_error), Toast.LENGTH_SHORT).show();
                }

                @Override
                public void onResponse(@NotNull Call call, @NotNull Response response) throws IOException {
                    String json = response.body().string();
                    Log.d(TAG, json);
                    JSONObject obj = null;
                    try {
                        obj = new JSONObject(json);
                    } catch (JSONException e) {
                        Log.e(TAG, "Too bad, so sad");
                        Log.e(TAG, json);
                    }
                    final boolean success = obj != null && !obj.has("ERROR");
                    String errorString = "";
                    try {
                        if (success) {
                            Machine machine = new Machine();
                            machine.maid = maid;
                            machine.name = (String)obj.get("name");
                            machine.expires = (Integer)obj.get("valid_until");
                            ZubinMeta.machines.add(machine);
                        }
                        errorString = (String)obj.get("ERROR");
                    } catch (JSONException e) {}
                    final String errorString2 = errorString;
                    MainActivity.this.runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            if (success) {
                                Toast.makeText(getApplicationContext(), getString(R.string.cn_restarting2), Toast.LENGTH_SHORT).show();
                            } else {
                                Toast.makeText(getApplicationContext(), getString(R.string.cn_error) + " " + errorString2, Toast.LENGTH_SHORT).show();
                            }
                        }
                    });
                }
            }, maid);
        }
        // else continue with any other code you need in the method
    }

}
