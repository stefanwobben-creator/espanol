import io, re
PAD="index.html"; PADV="versie.txt"; NIEUW="v23.85"
src=io.open(PAD,encoding="utf-8").read()
if NIEUW in src:
    print("al toegepast"); raise SystemExit
def rep(a,n,c=1):
    global src
    g=src.count(a); assert g==c, "anker %dx ipv %dx:\n%s"%(g,c,a[:160])
    src=src.replace(a,n,c)

# 1. "que Mi jefe" -> "que mi jefe": in het Spaans hoort mi klein midden in de zin.
rep('''function gcKlein(p){
  var n = String((p && p.nl) || "");
  return /^Mi /.test(String((p && p.es) || "")) ? n.charAt(0).toLowerCase() + n.slice(1) : n;
}''','''function gcKlein(p){
  var n = String((p && p.nl) || "");
  return /^Mi /.test(String((p && p.es) || "")) ? n.charAt(0).toLowerCase() + n.slice(1) : n;
}
/* v23.85: en hetzelfde voor het Spaans, want daar stond "Marta es mas rubia que Mi hermano" met
   een hoofdletter midden in de zin. Dat is de taal die geleerd wordt, dus daar telt het dubbel. */
function gcKleinEs(p){
  var n = String((p && p.es) || "");
  return /^Mi /.test(n) ? "mi" + n.slice(2) : n;
}''')
for a,n in [('+" que "+q.es+". ("+p.nl+" is "+gcVergroot(a)+" dan "+gcKlein(q)+")"',
             '+" que "+gcKleinEs(q)+". ("+p.nl+" is "+gcVergroot(a)+" dan "+gcKlein(q)+")"'),
            ('+" que "+q.es+". ("+p.en+" is more "+a.en+" than "+gcKleinEn(q)+")"',
             '+" que "+gcKleinEs(q)+". ("+p.en+" is more "+a.en+" than "+gcKleinEn(q)+")"'),
            ('+" ___ "+q.es+". (net zo "+a.nl+" als "+gcKlein(q)+")"',
             '+" ___ "+gcKleinEs(q)+". (net zo "+a.nl+" als "+gcKlein(q)+")"'),
            ('+" ___ "+q.es+". (just as "+a.en+" as "+gcKleinEn(q)+")"',
             '+" ___ "+gcKleinEs(q)+". (just as "+a.en+" as "+gcKleinEn(q)+")"')]:
    rep(a,n)

# 2. demostrativo: "en la mano" hield maar een zelfstandig naamwoord over. "que esta aqui" werkt
#    voor alles en zegt hetzelfde: dit hier, dichtbij.
rep('gcKies(gcInHand())','gcKies(GC_SUST)')
rep('''     return {v:"___ "+s.es+" que tengo en la mano. (dit/deze "+s.nl+" hier bij mij)",
             vEn:"___ "+s.es+" que tengo en la mano. (this "+s.en+" here in my hand)",''',
    '''     /* v23.85: "que tengo en la mano" kon maar bij een boek, en met de hand-filter van v23.84
        hield dit patroon precies een zin over. "Que esta aqui" zegt hetzelfde (dit hier, dichtbij)
        en past bij alles. */
     return {v:"___ "+s.es+" que est\\u00e1 aqu\\u00ed. (dit/deze "+s.nl+" hier vlakbij)",
             vEn:"___ "+s.es+" que est\\u00e1 aqu\\u00ed. (this "+s.en+" right here)",''')

src=re.sub(r'var APP_VERSIE = "[^"]+";','var APP_VERSIE = "%s";'%NIEUW,src,count=1)
io.open(PAD,"w",encoding="utf-8").write(src)
io.open(PADV,"w",encoding="utf-8").write(NIEUW+"\n")
print("gepatcht naar",NIEUW)
