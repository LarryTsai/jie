from pathlib import Path
import json,re,hashlib
base=Path(__file__).resolve().parent
sources=json.loads((base/'來源清單.json').read_text(encoding='utf-8-sig'))
sources={int(x['id']):x for x in sources}
# Portable source inventory keeps only repository-relative paths.
for entry in sources.values():
    entry['path']=str(base.parents[1]/'大綱'/entry['source'])
rows=[]
def rel(i): return '../../大綱/'+sources[i]['source']
def proof(path, start, end):
    lines=Path(path).read_text(encoding='utf-8-sig').splitlines()
    candidates=[(n+1,s) for n,s in enumerate(lines[start:end],start) if s.strip() and not s.startswith('#')]
    hit=next(((n,s) for n,s in candidates if any(w in s for w in ['厄','指骨','伴命'])),None)
    n,s=hit or (candidates[0] if candidates else (start+1,lines[start]))
    if any(w in s for w in ['厄','指骨','伴命']):
        k=min(s.find(w) for w in ['厄','指骨','伴命'] if w in s)
        s=s[max(0,k-8):k+38]
    else:s=s[:44]
    return n,s.replace('|','／').replace('\n',' ')
fixes={
65:{1:('P1','U01：给厄一个自己的撤退位置，不把它派给下界雷身'),2:('P3','三层土反制属于陸；厄可在本尊指骨口安静观察'),3:('P3','不让断处感知读出婁直未发动的下一击'),4:('P3','青璃／封胜场完整，厄不兼任救孩子的复制体'),5:('P1','U02：厄劫吼真失效，退回指骨口养力，不破仙法'),6:('P3','西极实场无厄；它在陸本尊处，鉴月不能代它传记忆'),7:('P3','长亭灭身实场无厄，只有本源强震可传痛非全经过'),8:('P3','望归七家实场无厄，不随分身过界'),9:('P3','活根由陸生封留下；厄不给新复生术'),10:('P3','原唯一伴命与自主不走完整，保全不再添一次'),11:('P3','睡在空骨，无雷吼、指路与仙力护体'),12:('P3','三雷胎不唤醒厄、不给答案'),13:('P3','骨实物随行、沉睡无应，不立即进未成劫藏')},
67:{1:('P3','原喚厄无声完整，保留其沉睡空位'),2:('P1','U03：故人重逢与问龙，第一访仅口述／纸绘'),3:('P3','睡厄不替他辨自己的回声'),4:('P3','箏真胜，睡厄不示警偷赢'),5:('P3','赤翎自己的地方生活不让厄代进池心'),6:('P3','古痕由陸实读，不让睡厄播古史'),7:('P3','睡厄不知池底阴谋，不提前预测工程'),8:('P3','一份列力永久耗，不由厄补回或救池心'),9:('P3','赤翎真死，无吞燼／进藏／厄复活'),10:('P3','睡期来信与实路，生自主来不是厄召唤'),11:('P3','公告实件、厄无远程神识'),12:('P3','辨睡厄非死节原场完整，保医生三败'),13:('P1','U04：移藏给骨实物/承睡位置交接，不让它醒说谢谢'),14:('P3','雷鯨是新天地，睡厄不任罗盘解三筋'),15:('P3','賀第一胜不被睡厄追音化解'),16:('P3','本人撤活禁不剪厄/毁本源'),17:('P3','细雷本人收尾，睡厄不吞其练法代价'),18:('P3','辛自己得盾，不由厄守护赐材'),19:('P3','形魂本人识别；劫藏非厄记忆播放'),20:('P3','賀真第二胜、睡厄无补场'),21:('P3','既有无间/流光边界，不由厄抹肩伤'),22:('P3','归墟只有限吞，睡厄不追加无限垃圾桶'),23:('P3','辛自主离界不让睡厄替主角挽留'),24:('P3','本尊九雷轮用，没有睡厄第十种反制'),25:('P3','賀毁鼓/陸舍筋真得失，无厄代杀'),26:('P3','筋片耗裂与源伤保留，睡厄不提前成熟'),27:('P3','箏离石突破归她，本人辨声自己过'),28:('P3','约33尊者不是至尊，厄继续睡到24尾')},
68:{1:('P3','新籍不洗旧罪，厄仍劫藏沉睡'),2:('P3','不借睡厄替他判材料道德'),3:('P3','本地根归本地，厄不能隔睡识全部地脉'),4:('P3','韓同境真胜，不由厄吞反震抵消'),5:('P3','母禁容量主权真属公孫，睡厄不加容量'),6:('P3','至尊敌由公孫抗，陸与厄不低境越墙'),7:('P3','战前合身只活源与真疲，不带回一只新厄'),8:('P3','錦自主焚锦伤损，不由厄吞变无损'),9:('P3','本人八伤可被追，睡厄不报敌完整图'),10:('P3','仙王截掌真救，不给厄第二伴命'),11:('P3','拓印交易实口供，睡厄不识凶手'),12:('P3','陸等仙光全褪，睡厄不吞王/仙力'),13:('P3','本人先恢复至尊九主首合，厄仍不先醒'),14:('P3','还重断阵本人胜，公孫季损保'),15:('P3','噤本人撕裂代价，厄不先龙身稳气免伤'),16:('P3','邵家责任/錦誓不靠厄裁真心'),17:('P1','U05：原尾成熟再现扩成认人和自选靠近，古殼不回')},
71:{1:('P1','U06：成熟厄选择劫域外等，不入命图/代承共同劫'),2:('P3','厄在上端本尊处不随封下界'),3:('P3','山影只传力，厄不借影到另一界'),4:('P3','商兄弟真战不让厄抢山痕'),5:('P3','本人真败收术，厄不能吞化全部同源反冲'),6:('P3','星羅目伤属于本人，不让厄吞干净'),7:('P3','撤形/收同活源重损不借厄刷新'),8:('P3','第四失敗六日才成，厄不吐一口雷替它凝形'),9:('P3','辨收本源练成，厄不播放古史'),10:('P3','三人缺劫亦无厄同场，厄在上端'),11:('P3','应琮自己带法出潭，与厄无已建交来源'),12:('P3','祖谱疑问属公冶与应琮，不给厄答案'),13:('P3','孤石来源由实验器核，厄不识八万年前供力者'),14:('P3','陸真实肩伤，厄不挡第二致命仙击'),15:('P3','后手空到真触发，厄不提前发古战原句'),16:('P3','两王保根隔力，厄不分担王力'),17:('P1','U07：厄对当下同源断口反应，非历史证人'),18:('P3','应琮掌时斩令，厄不知将来第三轮'),19:('P3','各身短承仍共伤，厄不吸全部'),20:('P3','封残痕真裂，厄不保护朋友所有负荷'),21:('P3','保根退身王交换，不让厄自己抓真仙补漏洞'),22:('P3','摘项实简证据，厄不辨申屠内心'),23:('P3','各人独立所得，厄只当在本尊处可安静同行')},
72:{1:('P3','上端厄可本尊同行，蒼梧自己旧约不交给厄解'),2:('P3','剥界屑帝道场真作，不靠厄吞'),3:('P3','本人想养弱声新器，厄不当弱声万能接收器'),4:('P3','成熟果真握空，厄不预知藏叶位置'),5:('P3','技艺亲历接木，不由厄播源头'),6:('P3','巡碑七千年是巫自己的法，厄不识全碑'),7:('P3','仙王识压真退，劫吼不破王法'),8:('P3','晏自己寄识枝不是厄替她发声'),9:('P3','小器真碎，厄不保住当成无损宝'),10:('P3','巫自己听碑，本源指向不等厄判断谁有罪'),11:('P3','巫真损笔与识伤，厄不吞回其代价'),12:('P3','半寸准许不因厄飞过禁门扩大'),13:('P3','技艺＋私称双钥实得，厄非第三钥'),14:('P1','U08：遗念不是厄父魂，它不认识长子；关係由当下陸回答'),15:('P3','阌册/巫见证是实件，厄不把魂吼变全部证词'),16:('P3','木络一近弱声，厄不让其成跨界网'),17:('P3','婁直不即时投誠，厄不能读心代和解'),18:('P1','U09：第三访前厄留守自主场，空骨本尊带走')},
73:{5:('P1','U09：留伏雷坳有自己的理由，非被命令宠兽驻守'),7:('P3','厄不在圣土；走潮者不是它复制体，不通话'),8:('P3','老友可问厄今况，本人亲口报，不见当场厄'),18:('P3','原明指骨空实物；没有厄躲骨护列身'),29:('P3','厄留九界不走回縫，走潮者另实体'),30:('P3','厄九界原位；上端陸只由实递得下界伤录')},
75:{1:('P3','厄九界不在上端雷身旁，不预测漏樁'),2:('P3','封首次唯一本人完成，不借厄感知成必胜'),3:('P3','侧路误断真失手，厄无全界自动地图'),4:('P3','厄不吞病患全部厄气替生完成医道'),5:('P3','赤翎自己的契/文自画新锚，不含厄当古劫电池'),6:('P1','U10：厄在九界与云紓有照护交接，不兼西极'),7:('P3','厄也不知道未运行盲路，不揭漏樁洗失手'),8:('P3','实件通訊不因厄与陸血缘自动全知'),9:('P3','九界实到与上端分簿已明，不搬厄到滄漣旁比血统'),10:('P3','厄不在圣土验许会；無先行新锚神识'),11:('P3','裴真挡刀，厄不替他抢赎罪动作'),12:('P1','U11：厄只护真实有限低量余厄，坊市角仍永久失'),13:('P3','各端本人实境，厄不借九界位远程帮仙战'),14:('P3','上端真仙反制无厄第二伴命'),15:('P3','一界输赢由真仙扣与两岸锚完成'),16:('P3','本人合源十雷独一，厄不成十一雷/入命图'),17:('P3','最强一击陸真得，厄不遥参与增幅'),18:('P3','太宸是我首讯不可由厄先嗷跨新锚'),19:('P3','两份约真实许可，厄不是赐全界自由门'),20:('P1','U12：家人认旧相与近候，修士渡印实际回家'),21:('P1','U13：厄自己辨当下断口，不讲八万年前记忆'),22:('P3','朋友真实各走，不用厄旁白把故事全复盘'),23:('P3','生恋情/勿沉归还不让厄代逼承诺'),24:('P3','厄不随封去蒼梧约；赤翎居处非伏雷坳'),25:('P1','U14：合一仍活着，厄亲口选择留守不被吞成雷')}
}
def state(i,unit):
    if i==65:
        mm=re.search(r'第(\d+)章',unit)
        k=int(mm.group(1)) if mm else (10 if unit=='B002' else 1)
        return ('约32／伴命前' if k<10 else '约32／伴命当场' if k==10 else '约32／伴命后','西极场无厄；厄仍本尊上端' if k==6 else '长亭雷身场无厄；本尊上端同源痛非完整知情' if k==7 else '望归雷身场无厄；本尊上端' if k==8 else '本尊身旁／指骨口' if k<10 else '第10当场壳耗；随后空骨沉睡','E2' if k<10 else 'E1：逆主动作后睡' if k==10 else 'E0')
    if i in [66,67,69]:return ('约32–33／R期','劫藏内沉睡，不能醒龙','沉睡，无人话／劫吼／示警')
    if i==68:return ('约33–34／R366–730','第17尾本人恢复至尊后成熟；此前劫藏沉睡','篇尾首次再现人话；此前无现形')
    if i==70:return ('约34／24尾伤养四日','原白沙园在尾成熟再现前：劫藏沉睡，不随露臺现龙','无声；可记想念，不写厄亲看花')
    if i in [71,72,81,82]:return ('约34–35／S期','成熟厄在陸本尊实际所在界；不随其他雷身／下界支线复制','可人话，劫吼不破仙法；古殼不恢复')
    if i in [73,74]:return ('约35–36／P0–359','厄在九界伏雷坳；本尊空指骨实物赴圣土，厄不同行','本支实场无厄；九界可人话，非跨壁课会')
    if i==75:return ('约36–37／Q0–365与后归家','厄九界实在；陸战时上端。第25自主守口，两截合一仍活','成熟人话／动作；不抢太宸新锚首讯')
    if i==76:return ('22首敗／24問山／44終勝','24问山若本尊真同场可在旁；44远景厄已守伏雷坳，不随远游','当代可表达；非石的随身地脉')
    if i==77:return ('25–32／七年','本尊未同场的程独立戏無厄；同城短会才可在本尊处','约26前仍早期叫声/动作；20篇后才人话')
    if i==78:return ('24–44／二十年','24本尊短访可能同场；44厄已守伏雷坳，不赴车终战','早期动作；不得二十年远程追读')
    if i==79:return ('18–43／馮本土自主线','无陸实场不硬安厄；34–35问罪本人时厄可随，43守伏雷坳','依实际阶段，不授她跨界无限能力')
    return ('古史八万年前→当代19–37及后','古史厄未出生；三地各自人物戏无厄；本人出现按同界/睡期区分','古史无厄；19仍动作；33.4睡；35聖土无厄')
def add(i,u,p,a,b,desc='',forced=None):
    tm,loc,expr=state(i,u)
    fix=forced or fixes.get(i,{}).get(int(re.search(r'第(\d+)章',u).group(1)) if re.search(r'第(\d+)章',u) else -1,('P3','本节点原胜负保留；无厄描写不是硬错，按已定实际位置可安静在场／异地不插'))
    if '第13甲段' in u or '第13乙段' in u:fix=('P1','U15伤者移送与师门问睡厄；厄已劫藏休养不出形')
    if any(x in u for x in ['第13丙段','第13丁段','第13戊段']):fix=('P3','睡厄零介入，宗门各自真胜、伤养和返程审批实付')
    n,q=proof(p,a,b)
    full='\n'.join(Path(p).read_text(encoding='utf-8-sig').splitlines()[a:b])
    ch=re.search(r'第(\d+)章',u); ch=int(ch.group(1)) if ch else None
    ev=re.search(r'B(\d{3})',u); ev=int(ev.group(1)) if ev else None
    hist=re.match(r'(\d{2,3})\s',u); hist=int(hist.group(1)) if hist else None
    if i==80 and hist:
        if hist<=101:tm='八万年前→古代后续';loc='厄十岁前尚未诞生；古史人物独立场';expr='E−'
        elif hist==102:tm='当代程未闌前事';loc='程独立现场；无厄同场证据';expr='E−（本场不演厄）'
        elif hist<=105:tm='陸19岁返鄉';loc='厄随陸本尊同界；纸绘/叫声期';expr='E1'
        elif hist<=108:tm='33.4行楼';loc='厄在本尊劫藏沉睡';expr='E0'
        elif hist<=111:tm='35–36圣土钟药庭';loc='厄九界伏雷坳；陸在圣土';expr='E−（本场异地）'
        elif hist<=115:tm='25后至28前的分地查证';loc='各地人物独立现场；不造厄参与文/艾现场';expr='E−（本场无亲见）'
        else:tm='37立锚/是我之后';loc='各支收实副本；厄九界不代古史证人';expr='E2仅九界本人'
    if i==76 and hist==14:loc='44远景石本人终战；厄已守伏雷坳';expr='E−（本场异地）'
    if i==78 and hist in [21,22]:loc='38/44远景车本人战；厄已守伏雷坳';expr='E−（本场异地）'
    if i==79 and hist in [23,24,25]:loc='馮本人东溟现场；无陸同行厄的证据';expr='E−（本场独立人物）'
    if i==71 and (ch==10 or ev==78):loc='九界封/文/奚/云实场无厄；厄上端本尊处';expr='E−（本场异地）'
    if i==67:
        loc='劫藏内沉睡，无人话／劫吼／示警' if (ch is not None and ch>=13 and '第13章' not in u) or (ev is not None and ev>=13) else '空指骨内沉睡，无人话／劫吼／示警'
        if (ch==13 and '第13章' in u) or ev==12:loc='本场劫藏成：睡厄从空指骨移入劫藏，仍沉睡'
    sleeping=('沉睡' in loc or i in [66,67,69,70]) and not (i==68 and ch==17)
    knowledge='K0：未醒，不演新知情' if sleeping else 'K−：本场无厄亲见' if ('无厄' in loc or '尚未诞生' in loc or '异地' in expr) else 'K1：仅当下亲见/实告；原未另写知情'
    choice='A0：原未另演自主，不据此判消失'
    if sleeping:choice='A睡：无新自主回应，不现形'
    if i==65 and (ch==10 or ev==2):choice='自選不走，融回骨挡一次；叫名无应';knowledge='亲见陸致命危；不需识婁直全谋'
    if i==67 and ch==1:choice='睡无回答；陸习惯呼唤，非幻象回话'
    if i==67 and ch==12:choice='因果本相微动，非醒来替生选剪处'
    if i==67 and (ch==13 or ev==12):choice='原移入劫藏休养；仍无成熟现形'
    if i==68 and (ch==17 or ev==74):choice='葉篇尾原再现叫劫；B074仅写白沙，U05补此桥';loc='R730候选尾：白沙園R723–726之后才成熟';expr='E2；此前E0';sleeping=False
    if i==73 and ch==5:choice='原留伏雷坳；自主缘由未演，U09补'
    if i==75 and ch==21:choice='原仍在陸旁，不被三读强迫提前归位';knowledge='亲见当下断口/陸三读；无古史记忆'
    if i==75 and ch==25:choice='先感裂，自選守口；两截合一仍活';knowledge='亲感当下裂处与同源，非知未来兇手'
    battle='W0' if sleeping or '无厄' in loc or '尚未诞生' in loc else 'W限：原未另写战力，不增加胜负作用'
    if i==65 and (ch==10 or ev==2):battle='W伴：挡唯一致命冲击；不救第二击/反胜真仙'
    if i==75 and ch==25:battle='W守：接自己断口，不吞聖土/增十一雷'
    names=[x for x in ['陸沉','洛生衣','萬俟箏','赤翎','封寒','雲行','雲紓','文奕','岳','顧小滿','沈山河','商應璋','應琮','公冶','巫峙','晏回枝','祁承晏','烏蘅','薇恩','伊萊恩','阿勒隆','貝提爾','賀逢山','辛照晚','韓照嶺','公孫','裴照川','寇平','鑑月','走潮者','母親'] if x in full]
    friend=('原场：'+('/'.join(names[:5]) if names else u)+'；'+('睡厄未新交流' if sleeping else '厄关系互动未另演'))
    if i==65 and (ch==10 or ev==2):friend='陸：逆其退令保命；非主人服从'
    if i==67 and ch==12:friend='陸/生：医者分辨睡本相，不把厄剪死'
    if i==68 and (ch==17 or ev==74):friend='陸：换新籍仍叫劫；与父匣／勿沉保有记忆桥';knowledge='K1：本人当场与新名相认，不继承古代记忆'
    if i==75 and ch==25:friend='陸/走潮者：亲自留守，合一后仍厄，不从生命变法宝'
    cost='D0：原伤器耗不抹；古殼不返'
    if i==65 and (ch is not None and ch<10 or ev==1):cost='殼力仍在，不提前伴命；原仙伤自承'
    if i==65 and (ch==10 or ev==2):cost='有限殼力一次耗尽；骨实物仍在，沉睡'
    if sleeping and not(i==65 and(ch==10 or ev==2)):cost='D睡：古殼已耗/休養实付，不吞原伤洗血'
    if i==80 and hist and hist<=101:cost='厄尚未生，不存在殼/伴命；原古史死傷不可逆'
    if i==71 and '同一時期' in u:loc='鳳上無極独立场无厄；陸仅后S350–367收件';knowledge='K−：无厄亲见';expr='E−';choice='A0：不把独立鳳线拴给厄';battle='W0';friend='鳳/成燁自己争穗；厄未接触此原场'
    srcid=next(j for j in sources if sources[j]['path']==str(p))
    rows.append([str(i),u,tm,loc,knowledge,expr,choice,battle,friend,cost,f'行{n}「{q}」[来源]({rel(srcid)})',fix[0],fix[1]])
# Nine unique sources were fully read in tool batches before extracting evidence.
for i in [65,67,68,71,72,73,75]:
    p=sources[i]['path']; ls=Path(p).read_text(encoding='utf-8-sig').splitlines()
    heads=[(n,s) for n,s in enumerate(ls) if re.match(r'^### 第\d+(?:[甲乙丙丁戊]段|章)',s)]
    for z,(a,h) in enumerate(heads):
        nxt=next((n for n in range(a+1,len(ls)) if ls[n].startswith('### ') or ls[n].startswith('## ')),len(ls))
        add(i,h.replace('### ',''),p,a+1,nxt)
# Actual event outline of the unnumbered four-day White Sand Garden, not its metadata headings.
p=sources[70]['path']; ls=Path(p).read_text(encoding='utf-8-sig').splitlines()
for needle,label in [('雲問他養傷','W1邀花/医许车行'),('園裡有人','W2住园争床'),('第一夜白沙','W3空花/错图/乾空鱼'),('阮來找種','W4循今夜湿意见星河'),('阮先採','W5有限留影/留种'),('回去不是','W6回诊/再游之约')]:
    a=next(n for n,s in enumerate(ls) if s.startswith(needle)); end=next((n for n in range(a+1,len(ls)) if ls[n]==''),len(ls))
    add(70,label,p,a,end,forced=('P3','厄仍睡；保本人记鱼似尾、留影带给朋友，不新造厄看花治裂'))
# Shared B file maps all 138 actual events once; management IDs select their concrete local story.
p=sources[66]['path']; ls=Path(p).read_text(encoding='utf-8-sig').splitlines()
for a,s in enumerate(ls):
    m=re.match(r'^\*\*B(\d{3})\*\*',s)
    if not m:continue
    k=int(m.group(1)); i=65 if k<=2 else 67 if k<=13 else 66 if k<=50 else 67 if k<=63 else 68 if k<=74 else 71 if k<=80 else 72 if k<=84 else 82 if k<=86 else 81 if k<=97 else 82
    special={2:('P3','唯一伴命原事件保全，对照65第10'),4:('P1','U03仅改关系为故人，不改箏法门槛'),11:('P3','医生辨睡厄/三败/本人同意原事件保'),12:('P1','U04移藏具体物理交接'),17:('P1','U15舟换力时固定空骨/劫藏诊录，不让睡厄自护'),20:('P1','U15师门问厄睡况，不让厄替弟子笑'),40:('P3','有限醫口胜不唤厄挡刀'),71:('P3','本尊先九雷至尊首合，厄未提前醒'),74:('P1','U05成熟再现安排在白沙園后，与葉篇一致'),75:('P1','U06成熟厄不替全部活源承仙劫'),78:('P3','下界三人無厄同场，厄上端本尊旁'),90:('P3','兩戰淺傷真養六日；厄不吞代價'),92:('P3','第二戰真養，厄非主角全免傷'),95:('P3','陳限定勝不被厄偷改判'),117:('P3','真仙肩裂本人承，厄不二伴命'),125:('P3','老祖實身魂由陸殺，不給厄辨魂/吞魂全知'),132:('P1','U16成熟厄想親近与真实休息，不治七十日仙伤'),138:('P3','战录实递非厄跨界传话')}.get(k,('P3','本事件只按实际亲见留下知情；原主角与配角胜败/医养保全，不硬补厄战力'))
    add(i,f'B{k:03d}',p,a,a+1,desc=s[10:60].replace('|','／'),forced=special)
# Historical event IDs 10–26 and 94–118. Title-only grouping labels are excluded.
for a,s in enumerate(ls):
    m=re.match(r'^### (\d{2,3})\s',s)
    if not m:continue
    k=int(m.group(1)); i=76 if 10<=k<=14 else 77 if 15<=k<=18 else 78 if 19<=k<=22 else 79 if 23<=k<=26 else 80 if 94<=k<=118 else None
    if i is None:continue
    end=next((n for n in range(a+1,len(ls)) if ls[n].startswith('### ') or ls[n].startswith('## ')),len(ls))
    special=('P3','古史厄未诞生／当地独立人物实戏不安厄；源证不变') if k<103 or k>111 else ('P3','同场/睡期/聖土不同行各別核，不让厄自动讀出证据')
    add(i,s.replace('### ',''),p,a+1,end,forced=special)
    if 106<=k<=108:add(69,s.replace('### ',''),p,a+1,end,forced=('P3','33.4厄在劫藏睡；封真坠/陸真败/七日养/半楼所得保，不让厄指楼路'))
    if 109<=k<=111:add(74,s.replace('### ',''),p,a+1,end,forced=('P3','35–36厄留伏雷坳；钟藥庭自煉/真潮簿不可给它在場或远端读史'))
# Actual extra story bridges retained in leaf sources.
extras=[(68,'工作插弧　同一道禁',69,'厄劫藏睡，完整24日对照106–108'),(68,'傷養中的白沙園三夜',70,'白沙園后才篇尾成熟'),(71,'同一時期，上無極也有人把自己的火寫完',71,'鳳34.5本人独立事件无厄；陸只後S350–367收件'),(73,'朋友带着自己赢回的东西来：百道接入',73,'林妮亞本人先袋戰無厄，厄留伏雷坳')]
for src,needle,mid,desc in extras:
    pp=sources[src]['path']; aa=Path(pp).read_text(encoding='utf-8-sig').splitlines(); a=next(n for n,s in enumerate(aa) if s.startswith('#') and needle in s); b=next((n for n in range(a+1,len(aa)) if aa[n].startswith('## ')),len(aa))
    # Use source's actual link for these mapped bridges.
    add(src,needle,pp,a+1,b,desc=desc,forced=('P3',desc+'；不把时序接口标题计成新章'))

intro='''# 後段逐章／事件矩陣

2026-10-11｜Continuity→Character→Power→Chapter Editor实际顺序核读；非Independent Reviewer，未自行审世界丙。只交候选，不改正式。

范围：来源清单管理65–82，18故事、9个唯一主来源全文去重读取。共享09全部521行已分批实读，逐B001–B138与10–26／94–118实事件映射；同一材料在相关管理号重用注明，不把幕、状态、来源、日帐及修法metadata当章节。第53豁免原文未读审改，本文件不是全书正式PASS。无缺源；若正式源后续变化，重核该节点不沿旧证称已通过。

位置和能力栏是“现行劫厄规则＋本段实场”推定，不伪称每章原文都有一句厄在。原文未写厄，可能安静在场、可能物理异地，不能直接判P0。每行原文证据取该实际节点，行号与路径可重现；关联本源和交通边界见任务单及劫厄主源。P1是重要生命／关系候选缺口，P3保原故事；本批未找到必须判定为现行内文P0的厄硬错。第二访肩上旧龙与新母稿矛盾、世界交通新法是母稿接口P0，交主编另裁，非谎报现行叶篇现形。

优先插场U01–U16见[后段候选修订](後段候選修訂.md)。这些已交具体场面而非叫作者补剧情，仍待独立Reviewer核其生命感和不抢戏。所有睡期不语、不出形、不作战；伴命全书一次；24成熟在本人至尊首合以后且白沙園原排期之后；27厄留伏雷坳、空指骨由本人携；28合一不断命。

## 逐节点记录

'''
cols=['管理号','真实章／事件','时点','厄位置／状态','知情及来源边界','表达','自主','战局影响','关系／本段所得','代价锁','原文短证／路径','P级','具体处置']
out=intro+'规则代码：K0=沉睡未演新知情；K−=本场异地／未生无亲见；K1=只能当下亲见或本人实告、无读心／回史／跨身即时记忆。E−=本场不演厄；E0=沉睡不能人话或现形；E1=早期动作叫声（22伴命是动作例外）；E2=20篇后可成句人话。A0=原未专演自主，不能据此判消失；A睡=不造睡中自主行动。W0=本节点厄零新增战局作用；W限=可写有限身外本领但本批未添加胜負；W伴=唯一伴命；W守=本人的守口选择。D0=原伤器耗保全、古殼不恢复；D睡=真实休养不洗血。实际自主与关系已演的行逐项填写，不用默认盖掉原场。\n\n'+'| '+' | '.join(cols)+' |\n|'+ '|'.join(['---']*len(cols))+'|\n'
for r in rows:out+='| '+' | '.join(str(x).replace('|','／').replace('\n',' ') for x in r)+' |\n'
out+='\n## 覆盖清点\n\n'
for i in sorted(range(65,83)):
    rr=[r for r in rows if int(r[0])==i]
    out+=f'- 管理{i}《{sources[i]["name"]}》：{len(rr)}个真实节点；[唯一管理来源]({rel(i)})。\n'
out+='\n逐源指纹（读后提取时记录，正式只读）：\n\n'
seen=set()
for i in range(65,83):
    p=Path(sources[i]['path'])
    if p in seen:continue
    seen.add(p);out+=f'- [{p.parent.name}/{p.name}]({rel(i)})：{len(p.read_bytes())} bytes，SHA256 `{hashlib.sha256(p.read_bytes()).hexdigest().upper()}`。\n'
# Preserve the independently checked white-sand-garden evidence.
out=re.sub(r'(\| 68 \| 傷養中的白沙園三夜 .*?)行125「.*?」\[来源\]', r'\1行123「四日三夜佔既有傷養時段：首日上午覆診、午後付費車去，第二日養息短走，第三夜親見地下白花如星河，第四日回原住處覆診。」[来源]', out)
(base/'後段逐章矩陣.md').write_text(out,encoding='utf-8')
print(json.dumps({'rows':len(rows),'counts':{str(i):sum(int(r[0])==i for r in rows) for i in range(65,83)}},ensure_ascii=False))
