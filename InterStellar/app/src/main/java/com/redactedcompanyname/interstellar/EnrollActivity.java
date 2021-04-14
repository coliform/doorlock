package com.RedactedCompanyName.interstellar;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;

import android.content.Context;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.Toast;

import com.google.firebase.database.annotations.NotNull;
import com.RedactedCompanyName.sdk.RedactedCompanyNameConstants;
import com.otaliastudios.cameraview.CameraException;
import com.otaliastudios.cameraview.CameraListener;
import com.otaliastudios.cameraview.CameraOptions;
import com.otaliastudios.cameraview.CameraView;
import com.otaliastudios.cameraview.PictureResult;
import com.otaliastudios.cameraview.controls.Facing;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Response;

public class EnrollActivity extends AppCompatActivity {

    private static final String TAG = "EnrollActivityTag";

    CameraView cv_enroll;
    Button bt_enroll_finish;
    Context context;
    Toast toast;

    private void Toaster(String text) {
        if (toast != null) toast.cancel();
        toast = Toast.makeText(context, text, Toast.LENGTH_SHORT);
        toast.show();
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_enroll);
        context = this;

        cv_enroll = findViewById(R.id.cv_enroll);
        cv_enroll.setFacing(Facing.FRONT);
        cv_enroll.setLifecycleOwner(this);
        cv_enroll.addCameraListener(new CustomCameraListener());

        bt_enroll_finish = findViewById(R.id.bt_enroll_finish);
        bt_enroll_finish.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                cv_enroll.takePicture();
            }
        });
    }

    private class CustomCameraListener extends CameraListener {
        @Override
        public void onCameraOpened(@NonNull CameraOptions options) {
            super.onCameraOpened(options);
            Log.d(TAG, "Camera opened");
        }

        @Override
        public void onCameraClosed() {
            super.onCameraClosed();
        }

        @Override
        public void onCameraError(@NonNull CameraException exception) {
            super.onCameraError(exception);
        }

        @Override
        public void onPictureTaken(@NonNull PictureResult result) {
            super.onPictureTaken(result);
            Toaster("Processing...");
            byte[] image = result.getData();
            int res = ZubinMeta.sdk.saveEnrollment(image, 2);
            if (res != 1) {
                Toaster("Try again, code " + String.valueOf(res));
                return;
            }
            Toaster("Success, sending to server");
            String path = RedactedCompanyNameConstants.FILE_STORAGE + "/enrolls.json";
            File file = new File(path);
            StringBuilder text = new StringBuilder();
            try {
                BufferedReader br = new BufferedReader(new FileReader(file));
                String line;

                while ((line = br.readLine()) != null) {
                    text.append(line);
                    text.append('\n');
                }
                br.close();
            }
            catch (IOException e) {
                //You'll need to add proper error handling here
            }
            String enrolls = text.toString();

            RestClient.uploadEnrolls(new Callback() {
                @Override
                public void onFailure(@NotNull Call call, @NotNull IOException e) {
                    Log.d(TAG, "Failed");
                    Log.d(TAG, e.toString());
                    EnrollActivity.this.runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            Toaster("Failed");
                        }
                    });
                }

                @Override
                public void onResponse(@NotNull Call call, @NotNull Response response) throws IOException {
                    EnrollActivity.this.runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            Toaster("Success");
                            finish();
                        }
                    });
                }
            }, enrolls);
        }
    }
}
