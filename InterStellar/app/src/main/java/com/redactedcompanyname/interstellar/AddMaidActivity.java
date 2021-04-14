package com.RedactedCompanyName.interstellar;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.google.firebase.database.annotations.NotNull;

import org.json.JSONException;
import org.json.JSONObject;
import org.w3c.dom.Text;

import java.io.IOException;

import com.RedactedCompanyName.interstellar.pojo.Machine;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Response;

public class AddMaidActivity extends AppCompatActivity {

    public final static String TAG = "AddMaidActivityTag";

    private Button bt_add_maid_finish;
    private TextView tv_add_maid_status;
    private EditText et_maid;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_add_maid);

        tv_add_maid_status = findViewById(R.id.tv_add_maid_status);
        bt_add_maid_finish = findViewById(R.id.bt_add_maid_finish);
        et_maid            = findViewById(R.id.et_maid);
        bt_add_maid_finish.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                final String maid = et_maid.getText().toString();
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
                        AddMaidActivity.this.runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                if (success) {
                                    Toast.makeText(getApplicationContext(), getString(R.string.cn_restarting2), Toast.LENGTH_SHORT).show();
                                    finish();
                                } else {
                                    Toast.makeText(getApplicationContext(), getString(R.string.cn_error) + " " + errorString2, Toast.LENGTH_SHORT).show();
                                }
                            }
                        });
                    }
                }, maid);
            }
        });
    }
}
