#!/bin/bash
# usage: build_apk.sh <update_base_url> <version_code> <version_name>
set -e
BASE="$1"; VC="${2:-1}"; VN="${3:-1.0}"
A=/home/claude/app; B=$A/build; AJ=/usr/lib/android-sdk/platforms/android-23/android.jar
rm -rf $B && mkdir -p $B/src $B/classes $B/assets
cp -r $A/android/src/* $B/src/
sed -i "s#__UPDATE_BASE__#$BASE#; s#__VERSION_CODE__#$VC#; s#__VERSION_NAME__#$VN#" $B/src/my/riyadussalihin/melayu/MainActivity.java
sed "s#android:versionCode=\"[0-9]*\"#android:versionCode=\"$VC\"#; s#android:versionName=\"[^\"]*\"#android:versionName=\"$VN\"#" $A/android/AndroidManifest.xml > $B/AndroidManifest.xml
cp $A/app.html $B/assets/app.html; cp /home/claude/reader/VERSION $B/assets/version.txt
javac -nowarn -source 8 -target 8 -bootclasspath $AJ -cp $AJ -d $B/classes $(find $B/src -name '*.java') 2>&1 | grep -v "warning\|^Picked up\|bootstrap" || true
dalvik-exchange --dex --min-sdk-version=21 --output=$B/classes.dex $B/classes
aapt package -f -M $B/AndroidManifest.xml -S $A/android/res -A $B/assets -I $AJ -F $B/unsigned.apk 
(cd $B && aapt add unsigned.apk classes.dex >/dev/null)
zipalign -f -p 4 $B/unsigned.apk $B/aligned.apk
apksigner sign --ks $A/keys/release.jks --ks-pass "pass:$(cat $A/keys/pass.txt)" --key-pass "pass:$(cat $A/keys/pass.txt)" --out $A/riyadus-salihin.apk $B/aligned.apk
apksigner verify --print-certs $A/riyadus-salihin.apk | head -3
ls -la $A/riyadus-salihin.apk
