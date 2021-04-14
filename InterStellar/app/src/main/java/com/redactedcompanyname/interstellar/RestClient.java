package com.RedactedCompanyName.interstellar;

import android.util.Base64;
import android.util.Log;

import com.google.firebase.iid.FirebaseInstanceId;

import org.json.JSONObject;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class RestClient {

    private static final String TAG = "RestClientTag";
    private static final String BASE_URL = "http://10.0.0.13:3002/";

    public static OkHttpClient client;
    private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");

    //public RestClient() { client = new OkHttpClient(); }

    private static void post(Callback callback, String url, String json) {
        Log.d(TAG, "Posting to the following");
        Log.d(TAG, url);
        Log.d(TAG, json);
        RequestBody body = RequestBody.create(JSON, json);
        Request request = new Request.Builder()
                .url(url)
                .post(body)
                .build();

        Call call = client.newCall(request);
        call.enqueue(callback);
    }

    private static String getAbsoluteUrl(String relativeUrl) {
        return BASE_URL + relativeUrl + ".rcn";
    }

    static void test(Callback callback) {
        post(callback, getAbsoluteUrl("test.rcn"), "");
    }

    static void registerUser(Callback callback) {
        String name = "", fcm = "", uid = "", token = "";
        fcm = FirebaseInstanceId.getInstance().getToken();
        name = ZubinMeta.user.getDisplayName();

        JSONObject jsonParams = new JSONObject();
        try {
            jsonParams.put("token", ZubinMeta.token);
            jsonParams.put("fcm", ZubinMeta.fcm);
            jsonParams.put("name", ZubinMeta.name);
        } catch (Exception e) {
            Log.e(TAG, e.toString());
        }

        post(callback,getAbsoluteUrl("register_user"), jsonParams.toString());
    }

    static void addUserToMachine(Callback callback, String maid) {
        JSONObject jsonParams = new JSONObject();
        try {
            jsonParams.put("token", ZubinMeta.token);
            jsonParams.put("maid", maid);
        } catch (Exception e) {
            Log.e(TAG, e.toString());
        }

        post(callback,getAbsoluteUrl("add_user_to_station"), jsonParams.toString());
    }

    static void removeUserFromMachine(Callback callback, String maid) {
        JSONObject jsonParams = new JSONObject();
        try {
            jsonParams.put("token", ZubinMeta.token);
            jsonParams.put("maid", maid);
        } catch (Exception e) {
            Log.e(TAG, e.toString());
        }

        post(callback,getAbsoluteUrl("remove_user_from_station"), jsonParams.toString());
    }

    static void unlockRemote(Callback callback) {
        JSONObject jsonParams = new JSONObject();
        try {
            jsonParams.put("token", ZubinMeta.token);
            jsonParams.put("maid", ZubinMeta.machines.get(ZubinMeta.currentlyActive).maid);
        } catch (Exception e) {
            Log.e(TAG, e.toString());
        }

        post(callback,getAbsoluteUrl("unlock_remote"), jsonParams.toString());
    }

    static void uploadEnrolls(Callback callback, String data) {
        JSONObject jsonParams = new JSONObject();
        try {
            jsonParams.put("token", ZubinMeta.token);
            jsonParams.put("data", data);
        } catch (Exception e) {
            Log.e(TAG, e.toString());
        }

        post(callback,getAbsoluteUrl("override_user_enrolls"), jsonParams.toString());
    }

    static void getStreamImage(Callback callback) {
        JSONObject jsonParams = new JSONObject();
        try {
            jsonParams.put("token", ZubinMeta.token);
            jsonParams.put("maid", ZubinMeta.machines.get(ZubinMeta.currentlyActive).maid);
        } catch (Exception e) {
            Log.e(TAG, e.toString());
        }

        post(callback,getAbsoluteUrl("get_stream_image"), jsonParams.toString());
    }
}
