"""Convert source texts into Ghost Light script packs (JSON).

Pack format (version 1):
{
  "id", "title", "titleZh", "author", "authorZh", "year", "kind", "level",
  "blurb", "source", "license",
  "cast": {"ROMEO": "罗密欧", ...},            # Chinese names for main characters
  "acts": [{"title": "Act I", "scenes": [{"title": "...", "items": [
        ["d", "stage direction"],
        ["s", "SPEAKER", ["verse line", ...]]
  ]}]}],
  "study": [...]                                # curated scenes, filled by build_study.py
}
"""
import json, re, sys, os
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "raw")
SRC = os.path.join(HERE, "sources")
os.makedirs(OUT, exist_ok=True)

META = {
  "romeo-juliet": dict(src="r_and_j.xml", title="Romeo and Juliet", titleZh="罗密欧与朱丽叶",
      author="William Shakespeare", authorZh="莎士比亚", year=1597, kind="莎士比亚 · 悲剧", level="中",
      blurb="维罗纳两大世仇家族的少男少女一见钟情。语言最抒情，名句最多，适合入门莎剧。",
      cast={"ROMEO":"罗密欧","JULIET":"朱丽叶","Nurse":"奶妈","NURSE":"奶妈","MERCUTIO":"茂丘西奥","BENVOLIO":"班伏里奥",
            "TYBALT":"提伯尔特","FRIAR LAURENCE":"劳伦斯神父","CAPULET":"凯普莱特","LADY CAPULET":"凯普莱特夫人",
            "MONTAGUE":"蒙太古","LADY MONTAGUE":"蒙太古夫人","PARIS":"帕里斯","PRINCE":"亲王","Chorus":"致辞者","CHORUS":"致辞者",
            "SAMPSON":"桑普森","GREGORY":"葛莱古里","BALTHASAR":"鲍尔萨泽","PETER":"彼得"}),
  "hamlet": dict(src="hamlet.xml", title="Hamlet", titleZh="哈姆雷特",
      author="William Shakespeare", authorZh="莎士比亚", year=1601, kind="莎士比亚 · 悲剧", level="高",
      blurb="丹麦王子发现叔父弑父篡位，在复仇与犹豫之间挣扎。独白最多，是演员必修。",
      cast={"HAMLET":"哈姆雷特","KING CLAUDIUS":"克劳狄斯","QUEEN GERTRUDE":"乔特鲁德","GERTRUDE":"乔特鲁德","CLAUDIUS":"克劳狄斯",
            "OPHELIA":"奥菲利娅","POLONIUS":"波洛涅斯","LORD POLONIUS":"波洛涅斯","LAERTES":"雷欧提斯","HORATIO":"霍拉旭","Ghost":"鬼魂","GHOST":"鬼魂",
            "ROSENCRANTZ":"罗森格兰兹","GUILDENSTERN":"吉尔登斯吞","MARCELLUS":"马西勒斯","BERNARDO":"勃那多","FRANCISCO":"弗兰西斯科",
            "First Clown":"掘墓人甲","Second Clown":"掘墓人乙","OSRIC":"奥斯里克","FORTINBRAS":"福丁布拉斯"}),
  "macbeth": dict(src="macbeth.xml", title="Macbeth", titleZh="麦克白",
      author="William Shakespeare", authorZh="莎士比亚", year=1606, kind="莎士比亚 · 悲剧", level="中",
      blurb="苏格兰将军听信女巫预言，与妻子谋杀国王，最终被野心吞噬。莎翁最短的悲剧，节奏紧。",
      cast={"MACBETH":"麦克白","LADY MACBETH":"麦克白夫人","BANQUO":"班柯","DUNCAN":"邓肯","MACDUFF":"麦克德夫",
            "MALCOLM":"马尔康","First Witch":"女巫甲","Second Witch":"女巫乙","Third Witch":"女巫丙","ALL":"众人",
            "ROSS":"洛斯","LENNOX":"列诺克斯","Porter":"门房","FLEANCE":"弗里恩斯","LADY MACDUFF":"麦克德夫夫人","Doctor":"医生","Gentlewoman":"侍女","First Murderer":"刺客甲","Son":"小麦克德夫","SEYTON":"西登"}),
  "midsummer": dict(src="dream.xml", title="A Midsummer Night's Dream", titleZh="仲夏夜之梦",
      author="William Shakespeare", authorZh="莎士比亚", year=1595, kind="莎士比亚 · 喜剧", level="中",
      blurb="雅典森林里，恋人、仙王仙后和一群业余演员被小精灵的魔法搅成一团。轻松好笑，还有戏中戏。",
      cast={"PUCK":"迫克","OBERON":"奥布朗","TITANIA":"提泰妮娅","HELENA":"海伦娜","HERMIA":"赫米娅","LYSANDER":"拉山德",
            "DEMETRIUS":"狄米特律斯","THESEUS":"忒修斯","HIPPOLYTA":"希波吕忒","EGEUS":"伊吉斯","BOTTOM":"波顿",
            "QUINCE":"昆斯","FLUTE":"弗鲁特","SNOUT":"斯诺特","SNUG":"斯纳格","STARVELING":"斯塔佛林","PHILOSTRATE":"菲劳斯特莱特","Pyramus":"皮拉摩斯","Thisbe":"提斯柏","Wall":"墙","Lion":"狮子","Moonshine":"月光","Fairy":"小仙"}),
}

def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()

def shakespeare(pid, m):
    root = ET.parse(f"{SRC}/shakespeare/{m['src']}").getroot()
    acts = []
    for act in root.findall("ACT"):
        a = {"title": "Act " + clean(act.findtext("TITLE")).split()[-1], "scenes": []}
        for sc in act:
            if sc.tag not in ("SCENE", "PROLOGUE"):
                continue
            items = []
            for el in sc:
                if el.tag == "STAGEDIR":
                    items.append(["d", clean(el.text)])
                elif el.tag == "SPEECH":
                    who = " & ".join(clean(s.text) for s in el.findall("SPEAKER"))
                    lines = []
                    for ln in el:
                        if ln.tag == "LINE":
                            parts = [ln.text or ""]
                            for ch in ln:
                                parts.append(("[" + clean(ch.text) + "] ") if ch.tag == "STAGEDIR" else "".join(ch.itertext()))
                                parts.append(ch.tail or "")
                            txt = clean("".join(parts))
                            if txt:
                                lines.append(txt)
                        elif ln.tag == "STAGEDIR":
                            # direction inside a speech: close the speech, emit direction, reopen
                            if lines:
                                items.append(["s", who, lines]); lines = []
                            items.append(["d", clean(ln.text)])
                    if lines:
                        items.append(["s", who, lines])
            title = clean(sc.findtext("TITLE"))
            if sc.tag == "PROLOGUE":
                title = "Prologue"
            a["scenes"].append({"title": title, "items": items})
        acts.append(a)
    return acts

def seagull():
    raw = open(f"{SRC}/seagull.txt", encoding="utf-8", errors="replace").read()
    body = raw[raw.index("\nACT I\n"):raw.index("*** END OF")]
    paras = [clean(p) for p in re.split(r"\n\s*\n", body)]
    acts, cur = [], None
    roman = {"I": "Act I", "II": "Act II", "III": "Act III", "IV": "Act IV"}
    sp = re.compile(r"^([A-Z][A-Z'\- ]{1,30})\.\s+(.*)$")
    for p in paras:
        if not p:
            continue
        if re.fullmatch(r"ACT (I|II|III|IV)", p):
            cur = {"title": roman[p.split()[1]], "scenes": [{"title": roman[p.split()[1]], "items": []}]}
            acts.append(cur); continue
        if p in ("THE CURTAIN FALLS", "CURTAIN", "THE END") or cur is None:
            if cur: cur["scenes"][0]["items"].append(["d", p.title()])
            continue
        m = sp.match(p)
        items = cur["scenes"][0]["items"]
        if m:
            items.append(["s", m.group(1).strip(), [m.group(2)]])
        else:
            items.append(["d", p.strip("_ ").replace("_", "")])
    return acts

def stats(acts):
    sp = sum(1 for a in acts for s in a["scenes"] for i in s["items"] if i[0] == "s")
    return sp

catalog = []
for pid, m in META.items():
    acts = shakespeare(pid, m)
    pack = {k: v for k, v in m.items() if k != "src"}
    pack.update(id=pid, source="The Bosak XML edition of Shakespeare (via NLTK corpus)", license="公有领域 Public domain", acts=acts, study=[])
    json.dump(pack, open(f"{OUT}/{pid}.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print(pid, len(acts), "acts", stats(acts), "speeches")

pack = dict(id="seagull", title="The Seagull", titleZh="海鸥", author="Anton Chekhov", authorZh="契诃夫", year=1896,
    kind="契诃夫 · 现代戏剧", level="初中", source="Project Gutenberg eBook #1754 (early English translation)",
    license="公有领域 Public domain",
    blurb="湖边庄园里，想当作家的年轻人、想当演员的少女和一位成名女演员纠缠在爱与艺术之间。现代戏剧的开山之作，语言是日常口语。",
    cast={"TREPLIEFF":"特里波列夫","NINA":"妮娜","MADAME ARKADINA":"阿尔卡金娜","ARKADINA":"阿尔卡金娜","TRIGORIN":"特里果林",
          "SORIN":"索林","MASHA":"玛莎","DORN":"多恩","MEDVIEDENKO":"梅德维坚科","SHAMRAEFF":"沙姆拉耶夫","PAULINA":"波琳娜","JACOB":"雅科夫"},
    acts=seagull(), study=[])
json.dump(pack, open(f"{OUT}/seagull.json", "w"), ensure_ascii=False, separators=(",", ":"))
print("seagull", len(pack["acts"]), stats(pack["acts"]))
from collections import Counter
print(Counter(i[1] for a in pack["acts"] for s in a["scenes"] for i in s["items"] if i[0]=="s").most_common(20))
