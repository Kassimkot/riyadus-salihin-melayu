package my.riyadussalihin.melayu;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.Window;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.security.MessageDigest;

/**
 * Riyadus Salihin (Melayu) — a WebView shell around the reader page.
 * On every start it checks UPDATE_BASE/version.json; if the published content is newer
 * it downloads the new page, verifies it, swaps it in and reloads.
 */
public class MainActivity extends Activity {
    static final String UPDATE_BASE = "__UPDATE_BASE__";
    static final String ORIGIN = "https://riyadus-salihin.app/";
    static final int APP_VERSION_CODE = __VERSION_CODE__;
    static final String APP_VERSION_NAME = "__VERSION_NAME__";
    static final int REQ_SAVE = 11, REQ_OPEN = 12;
    static final long RECHECK_MS = 6L * 60 * 60 * 1000;

    WebView web;
    long loadedVersion = 0, lastCheck = 0, openedAt = 0;
    boolean checking = false;
    String pendingSave = null;
    ValueCallback<Uri[]> fileCallback = null;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        Window w = getWindow();
        w.setStatusBarColor(Color.parseColor("#0e6b58"));
        web = new WebView(this);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(true);
        s.setTextZoom(100);
        web.addJavascriptInterface(new Bridge(), "RSApp");
        web.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView v, String url) { return openExternal(url); }
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) { return openExternal(r.getUrl().toString()); }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> cb, FileChooserParams p) {
                if (fileCallback != null) fileCallback.onReceiveValue(null);
                fileCallback = cb;
                Intent i = new Intent(Intent.ACTION_GET_CONTENT);
                i.addCategory(Intent.CATEGORY_OPENABLE);
                i.setType("*/*");
                try { startActivityForResult(Intent.createChooser(i, "Pilih fail nota"), REQ_OPEN); }
                catch (ActivityNotFoundException e) { fileCallback = null; return false; }
                return true;
            }
        });
        final android.widget.FrameLayout root = new android.widget.FrameLayout(this);
        root.addView(web, new android.widget.FrameLayout.LayoutParams(-1, -1));
        setContentView(root);
        // Android 15+ draws apps edge-to-edge: keep the page clear of the status and navigation bars (and the keyboard).
        w.getDecorView().setBackgroundColor(Color.parseColor("#0e6b58"));
        if (android.os.Build.VERSION.SDK_INT >= 35) {
            root.setOnApplyWindowInsetsListener(new android.view.View.OnApplyWindowInsetsListener() {
                public android.view.WindowInsets onApplyWindowInsets(android.view.View v, android.view.WindowInsets in) {
                    v.setPadding(in.getSystemWindowInsetLeft(), in.getSystemWindowInsetTop(), in.getSystemWindowInsetRight(), in.getSystemWindowInsetBottom());
                    return in;
                }
            });
        }
        openedAt = System.currentTimeMillis();
        loadPage();
        checkForUpdate(false);
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (apkReady && !canSilent() && canInstall() && prefs().getBoolean("askedPerm", false)) { prefs().edit().putBoolean("askedPerm", false).apply(); commitInstall(); }
        if (lastCheck > 0 && System.currentTimeMillis() - lastCheck > RECHECK_MS) checkForUpdate(false);
    }

    boolean openExternal(String url) {
        if (url.startsWith(ORIGIN) || url.startsWith("about:") || url.startsWith("data:") || url.startsWith("blob:")) return false;
        try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))); } catch (Exception ignored) { }
        return true;
    }

    /* ---------- content: bundled asset vs. downloaded update ---------- */

    File updFile() { return new File(getFilesDir(), "app.html"); }
    SharedPreferences prefs() { return getSharedPreferences("rs", MODE_PRIVATE); }

    long bundledVersion() {
        try { return Long.parseLong(new String(readAll(getAssets().open("version.txt")), "UTF-8").trim()); }
        catch (Exception e) { return 0; }
    }

    void loadPage() {
        String html = null;
        long bv = bundledVersion(), dv = prefs().getLong("ver", 0);
        File f = updFile();
        if (dv > bv && f.exists()) {
            try { html = new String(readAll(new FileInputStream(f)), "UTF-8"); loadedVersion = dv; }
            catch (Exception e) { html = null; }
        }
        if (html == null) {
            try { html = new String(readAll(getAssets().open("app.html")), "UTF-8"); loadedVersion = bv; }
            catch (Exception e) { html = "<p>Tidak dapat membuka kandungan.</p>"; }
        }
        web.loadDataWithBaseURL(ORIGIN, html, "text/html", "UTF-8", null);
    }

    void checkForUpdate(final boolean manual) {
        if (checking || UPDATE_BASE.startsWith("__")) return;
        checking = true;
        new Thread(new Runnable() { public void run() {
            try {
                JSONObject j = new JSONObject(new String(get(UPDATE_BASE + "version.json?t=" + System.currentTimeMillis(), 15000), "UTF-8"));
                lastCheck = System.currentTimeMillis();
                final long v = j.getLong("version");
                boolean updated = false;
                if (v > loadedVersion) {
                    byte[] page = get(UPDATE_BASE + j.optString("page", "app.html") + "?v=" + v, 60000);
                    String sha = j.optString("sha256", "");
                    if (!sha.isEmpty() && !sha.equalsIgnoreCase(sha256(page))) throw new Exception("checksum");
                    if (page.length < 50000 || !new String(page, "UTF-8").contains("RS_VERSION")) throw new Exception("invalid page");
                    File tmp = new File(getFilesDir(), "app.html.tmp");
                    OutputStream o = new FileOutputStream(tmp); o.write(page); o.close();
                    if (!tmp.renameTo(updFile())) throw new Exception("rename");
                    prefs().edit().putLong("ver", v).apply();
                    updated = true;
                }
                final boolean didUpdate = updated;
                final int apkVer = j.optInt("apk_version", 0);
                final String apkUrl = j.optString("apk", "");
                final String apkSha = j.optString("apk_sha256", "");
                runOnUiThread(new Runnable() { public void run() {
                    if (didUpdate && (manual || System.currentTimeMillis() - openedAt < 5000)) {
                        // just opened (or asked): swap in quietly; otherwise it is used next time the app opens
                        loadPage();
                        if (manual) Toast.makeText(MainActivity.this, "Kandungan dikemas kini", Toast.LENGTH_SHORT).show();
                    } else if (manual) {
                        Toast.makeText(MainActivity.this, "Sudah versi terkini", Toast.LENGTH_SHORT).show();
                    }
                    if (apkVer > APP_VERSION_CODE && !apkUrl.isEmpty()) fetchApk(apkVer, apkUrl, apkSha);
                }});
            } catch (final Exception e) {
                if (manual) runOnUiThread(new Runnable() { public void run() {
                    Toast.makeText(MainActivity.this, "Tidak dapat menyemak kemas kini", Toast.LENGTH_SHORT).show();
                }});
            } finally { checking = false; }
        }}).start();
    }

    /* ---------- in-app APK update (PackageInstaller) ---------- */

    File apkFile() { return new File(getCacheDir(), "update.apk"); }
    boolean apkReady = false;

    /** Download the new APK in the background, then install: quietly when Android allows, otherwise with one confirmation. */
    void fetchApk(final int ver, final String url, final String sha) {
        if (prefs().getInt("apkReady", 0) == ver && apkFile().exists()) { apkReady = true; installReady(ver); return; }
        new Thread(new Runnable() { public void run() {
            try {
                byte[] apk = get(url + "?v=" + ver, 120000);
                if (!sha.isEmpty() && !sha.equalsIgnoreCase(sha256(apk))) throw new Exception("checksum");
                OutputStream o = new FileOutputStream(apkFile()); o.write(apk); o.close();
                prefs().edit().putInt("apkReady", ver).apply();
                runOnUiThread(new Runnable() { public void run() { apkReady = true; installReady(ver); } });
            } catch (Exception ignored) { }
        }}).start();
    }

    boolean canSilent() {
        if (android.os.Build.VERSION.SDK_INT < 31) return false;
        try { return getPackageName().equals(getPackageManager().getInstallerPackageName(getPackageName())); }
        catch (Exception e) { return false; }
    }

    boolean canInstall() {
        if (android.os.Build.VERSION.SDK_INT < 26) return true;
        try { return (Boolean) getPackageManager().getClass().getMethod("canRequestPackageInstalls").invoke(getPackageManager()); }
        catch (Exception e) { return true; }
    }

    void installReady(int ver) {
        if (canSilent()) return; // installed quietly when the app goes to the background (onStop)
        if (isFinishing()) return;
        if (!canInstall()) {
            new AlertDialog.Builder(this)
                .setTitle("Kemas kini aplikasi")
                .setMessage("Versi baharu aplikasi sudah dimuat turun. Sekali sahaja, benarkan aplikasi ini memasang kemas kini: tekan Benarkan, hidupkan pilihan itu, kemudian kembali ke sini.\n\nSelepas ini kemas kini akan dipasang secara automatik.")
                .setPositiveButton("Benarkan", new android.content.DialogInterface.OnClickListener() { public void onClick(android.content.DialogInterface d, int x) {
                    prefs().edit().putBoolean("askedPerm", true).apply();
                    try { startActivity(new Intent("android.settings.MANAGE_UNKNOWN_APP_SOURCES", Uri.parse("package:" + getPackageName()))); } catch (Exception ignored) { }
                } })
                .setNegativeButton("Nanti", null)
                .show();
            return;
        }
        commitInstall();
    }

    @Override
    protected void onStop() {
        super.onStop();
        if (apkReady && canSilent()) commitInstall();
    }

    void commitInstall() {
        if (!apkFile().exists()) return;
        try {
            android.content.pm.PackageInstaller pi = getPackageManager().getPackageInstaller();
            android.content.pm.PackageInstaller.SessionParams sp = new android.content.pm.PackageInstaller.SessionParams(android.content.pm.PackageInstaller.SessionParams.MODE_FULL_INSTALL);
            sp.setAppPackageName(getPackageName());
            if (android.os.Build.VERSION.SDK_INT >= 31) {
                try { sp.getClass().getMethod("setRequireUserAction", int.class).invoke(sp, 2 /* USER_ACTION_NOT_REQUIRED */); } catch (Exception ignored) { }
            }
            int id = pi.createSession(sp);
            android.content.pm.PackageInstaller.Session ses = pi.openSession(id);
            OutputStream out = ses.openWrite("update.apk", 0, apkFile().length());
            InputStream in = new FileInputStream(apkFile());
            byte[] buf = new byte[65536]; int n;
            while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
            in.close(); ses.fsync(out); out.close();
            Intent cb = new Intent(this, InstallReceiver.class);
            int flags = android.app.PendingIntent.FLAG_UPDATE_CURRENT | (android.os.Build.VERSION.SDK_INT >= 31 ? 0x02000000 /* FLAG_MUTABLE */ : 0);
            ses.commit(android.app.PendingIntent.getBroadcast(this, id, cb, flags).getIntentSender());
            ses.close();
            apkReady = false;
        } catch (Exception e) {
            Toast.makeText(this, "Tidak dapat memasang kemas kini", Toast.LENGTH_SHORT).show();
        }
    }

    /* ---------- helpers ---------- */

    static byte[] get(String url, int timeout) throws Exception {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setConnectTimeout(timeout); c.setReadTimeout(timeout);
        c.setUseCaches(false);
        c.setRequestProperty("Cache-Control", "no-cache");
        try {
            if (c.getResponseCode() != 200) throw new Exception("HTTP " + c.getResponseCode());
            return readAll(c.getInputStream());
        } finally { c.disconnect(); }
    }

    static byte[] readAll(InputStream in) throws Exception {
        ByteArrayOutputStream b = new ByteArrayOutputStream();
        byte[] buf = new byte[16384]; int n;
        try { while ((n = in.read(buf)) > 0) b.write(buf, 0, n); } finally { in.close(); }
        return b.toByteArray();
    }

    static String sha256(byte[] d) throws Exception {
        byte[] h = MessageDigest.getInstance("SHA-256").digest(d);
        StringBuilder sb = new StringBuilder();
        for (byte x : h) sb.append(String.format("%02x", x));
        return sb.toString();
    }

    @Override
    public void onBackPressed() {
        web.evaluateJavascript("(window.rsBack && rsBack()) ? 'y' : 'n'", new ValueCallback<String>() { public void onReceiveValue(String v) { if (v == null || !v.contains("y")) MainActivity.super.onBackPressed(); } });
    }

    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        if (req == REQ_OPEN) {
            if (fileCallback != null) fileCallback.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(res, data));
            fileCallback = null;
        } else if (req == REQ_SAVE) {
            if (res == RESULT_OK && data != null && data.getData() != null && pendingSave != null) {
                try {
                    OutputStream o = getContentResolver().openOutputStream(data.getData());
                    o.write(pendingSave.getBytes("UTF-8")); o.close();
                    Toast.makeText(this, "Nota disimpan", Toast.LENGTH_SHORT).show();
                } catch (Exception e) { Toast.makeText(this, "Tidak dapat menyimpan fail", Toast.LENGTH_SHORT).show(); }
            }
            pendingSave = null;
        }
    }

    class Bridge {
        @JavascriptInterface public String appVersion() { return APP_VERSION_NAME; }
        @JavascriptInterface public void checkUpdate() { runOnUiThread(new Runnable() { public void run() { checkForUpdate(true); } }); }
        @JavascriptInterface public void shareText(final String subject, final String text) {
            runOnUiThread(new Runnable() { public void run() {
                Intent sh = new Intent(Intent.ACTION_SEND);
                sh.setType("text/plain");
                sh.putExtra(Intent.EXTRA_SUBJECT, subject);
                sh.putExtra(Intent.EXTRA_TEXT, text);
                try { startActivity(Intent.createChooser(sh, "Kongsi hadis")); } catch (Exception ignored) { }
            }});
        }
        @JavascriptInterface public void shareImage(final String name, final String base64) {
            runOnUiThread(new Runnable() { public void run() {
                try {
                    File dir = new File(getCacheDir(), "share"); dir.mkdirs();
                    File[] old = dir.listFiles(); if (old != null) for (File o : old) o.delete();
                    String safe = name.replaceAll("[^A-Za-z0-9._-]", "_");
                    File f = new File(dir, safe);
                    OutputStream o = new FileOutputStream(f); o.write(android.util.Base64.decode(base64, android.util.Base64.DEFAULT)); o.close();
                    Uri uri = Uri.parse("content://" + ShareProvider.AUTH + "/" + safe);
                    Intent sh = new Intent(Intent.ACTION_SEND);
                    sh.setType("image/png");
                    sh.putExtra(Intent.EXTRA_STREAM, uri);
                    sh.setClipData(android.content.ClipData.newRawUri("", uri));
                    sh.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                    startActivity(Intent.createChooser(sh, "Kongsi gambar hadis"));
                } catch (Exception e) { Toast.makeText(MainActivity.this, "Tidak dapat berkongsi gambar", Toast.LENGTH_SHORT).show(); }
            }});
        }
        @JavascriptInterface public void shareFile(final String name, final String content) {
            runOnUiThread(new Runnable() { public void run() {
                pendingSave = content;
                Intent i = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                i.addCategory(Intent.CATEGORY_OPENABLE);
                i.setType("application/json");
                i.putExtra(Intent.EXTRA_TITLE, name);
                try { startActivityForResult(i, REQ_SAVE); }
                catch (ActivityNotFoundException e) {
                    Intent sh = new Intent(Intent.ACTION_SEND);
                    sh.setType("text/plain"); sh.putExtra(Intent.EXTRA_SUBJECT, name); sh.putExtra(Intent.EXTRA_TEXT, content);
                    startActivity(Intent.createChooser(sh, "Kongsi nota"));
                    pendingSave = null;
                }
            }});
        }
    }
}
