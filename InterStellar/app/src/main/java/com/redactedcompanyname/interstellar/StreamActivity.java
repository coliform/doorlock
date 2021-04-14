package com.RedactedCompanyName.interstellar;

import androidx.appcompat.app.AppCompatActivity;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.AsyncTask;
import android.os.Bundle;
import android.util.Base64;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;

import com.google.firebase.database.annotations.NotNull;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Response;

public class StreamActivity extends AppCompatActivity {

    private Button bt_unlock_stream;
    private ImageView im_stream;

    private final static String TAG = "StreamActivityTag";

    private boolean keep_going = true;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_stream);

        bt_unlock_stream = findViewById(R.id.bt_unlock_stream);
        im_stream = findViewById(R.id.im_stream);
        bt_unlock_stream.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                RestClient.unlockRemote(new Callback() {
                    @Override
                    public void onFailure(@NotNull Call call, @NotNull IOException e) {
                        Log.d(TAG, "Failed");
                        Log.d(TAG, e.toString());
                    }

                    @Override
                    public void onResponse(@NotNull Call call, @NotNull Response response) throws IOException {
                    }
                });
            }
        });

        AsyncTask.execute(new Runnable() {
            @Override
            public void run() {
                while (keep_going) {
                    RestClient.getStreamImage(new Callback() {
                        @Override
                        public void onFailure(@NotNull Call call, @NotNull IOException e) {
                            Log.d(TAG, "Failed");
                            Log.d(TAG, e.toString());
                            keep_going = false;
                        }

                        @Override
                        public void onResponse(@NotNull Call call, @NotNull Response response) throws IOException {
                            String json = response.body().string();
                            Log.d(TAG, json);
                            String picture_str="";
                            JSONObject obj = null;
                            try {
                                obj = new JSONObject(json);
                                picture_str = (String)obj.get("picture");
                            } catch (JSONException e) {
                                Log.e(TAG, "Too bad, so sad");
                                Log.e(TAG, e.toString());
                            }
                            byte[] image = Base64.decode(picture_str, Base64.URL_SAFE);
                            final Bitmap bitmap = BitmapFactory.decodeByteArray(image, 0, image.length);
                            StreamActivity.this.runOnUiThread(new Runnable() {
                                @Override
                                public void run() {
                                    if (bitmap != null) {
                                        im_stream.setImageBitmap(bitmap);
                                        Log.d(TAG, "Updating bitmap");
                                    }
                                }
                            });
                        }
                    });
                    try { Thread.sleep(1000); } catch (InterruptedException e) {}
                }
            }
        });
    }

    @Override
    protected void onStop() {
        super.onStop();
        keep_going = false;
    }

    @Override
    protected void onPause() {
        super.onPause();
        keep_going = false;
    }

    @Override
    protected void onResume() {
        super.onResume();
        keep_going = true;
    }
}
