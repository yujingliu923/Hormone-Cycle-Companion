from __future__ import annotations

from datetime import date, datetime
from math import exp
import random
from typing import Dict, List

DEFAULT_CYCLE_LENGTH = 28
DEFAULT_MENSES_DAYS = 5
PHASE_NAMES = {
    "menstruation": "月经期",
    "follicular": "卵泡期",
    "ovulation": "排卵期",
    "luteal": "黄体期",
}

SYMPTOM_LIBRARY = {
    "menstruation": ["疲倦", "下腹痉挛", "情绪波动或敏感", "怕冷或需要更多安慰"],
    "follicular": ["体力恢复", "专注度提升", "心情平稳", "对新事物好奇"],
    "ovulation": ["性欲上升", "自信心增强", "社交欲强", "体温略微升高"],
    "luteal": ["乳房胀痛", "胃口变化", "睡眠质量起伏", "易怒或焦虑"],
}

SELF_ADVICE_VARIANTS = {
    "menstruation": [
        {
            "headline": "此时身体最需要被照顾，把行程降速是一种勇敢。",
            "items": [
                "泡一壶温暖的红糖姜茶或薰衣草茶，搭配热水袋，持续 20 分钟能改善血液循环。",
                "把重要会议与情绪消耗性的沟通延后，允许自己专注于伸展、阅读或静心练习。",
                "记录痛感与情绪在一天中的波动，必要时将数据带去与医生讨论，别自己扛。",
            ],
        },
        {
            "headline": "经期像一段维护窗口，把感受写下来也是疗愈。",
            "items": [
                "每天安排一个“暂停按钮”，轻柔转动骨盆或做猫牛式，缓解腰背紧绷。",
                "摄入铁质和维生素 C 的组合例如果汁+菠菜，帮助补充经血流失的营养。",
                "若出现强烈情绪，试着写下当下的三个感受，再为自己写一句安慰语。",
            ],
        },
        {
            "headline": "这个阶段最好的 KPI 是好好活着，给自己放宽标准。",
            "items": [
                "工作量若无法减少，至少设提醒做 5 分钟缓慢深呼吸，再继续任务。",
                "备好暖宝宝、薄毯等舒适物件，把身体照顾好，效率自然跟上。",
                "遇到难以处理的人际冲突时果断延迟回复，优先处理身体讯号。",
            ],
        },
        {
            "headline": "痛感提醒你需要援助，别犹豫将需求告诉信任的人。",
            "items": [
                "尝试轻柔的腹部按摩，从顺时针方向按压，搭配香油或乳液更放松。",
                "保持少量多餐，多补充温热汤品与高纤维食物减少水肿与便秘。",
                "在日程上标注“自我照护时段”，哪怕只是让自己静静发呆十分钟。",
            ],
        },
        {
            "headline": "身心走入低谷时，比平日更需要界限感与自我对话。",
            "items": [
                "把“我现在最不想做的三件事”写下来，并思考能否延期或委托。",
                "准备播放清单、香氛或舒缓播客，让感官获得安抚，情绪更易平稳。",
                "若痛经严重，可记录药物时间与效果，为下一次调整剂量与节奏做准备。",
            ],
        },
    ],
    "follicular": [
        {
            "headline": "卵泡期像身心重启，适合为自己设定优雅但有力的节奏。",
            "items": [
                "计划学习或策略性会议，把脑力旺盛的时间留给重要挑战。",
                "补充优质蛋白质与发酵食物，帮助修复组织并稳定血糖。",
                "尝试一个小小的造型或穿搭变化，强化“正在长成更好版本”的暗示。",
            ],
        },
        {
            "headline": "能量回升时请善用它，但别忘了给身体留余地。",
            "items": [
                "安排日光散步或轻度力量训练，刺激雌激素与多巴胺的良性循环。",
                "把待办事项拆成 3 个“必须完成”的核心任务，兼顾效率与成就感。",
                "执行新的饮食计划或作息调整，因为此时意志力相对更稳定。",
            ],
        },
        {
            "headline": "这是最适合拓展社交、创意与学习的周期窗口。",
            "items": [
                "安排一次高质量的脑力风暴或写作，灵感更容易来敲门。",
                "若想建立新的习惯，例如早起或瑜伽，现在的顺从度最高。",
                "多与信任的人分享愿景，积极情绪会放大坚持动力。",
            ],
        },
        {
            "headline": "感受渐渐稳定，务实与大胆可以并存。",
            "items": [
                "挑选一项想突破的技能，用 30-30-30 分块法进行深度练习。",
                "制定接下来 2 周的轻量 meal prep，让饮食与血糖维持在稳定範围。",
                "若有未解决的冲突，可在这段时间以开放姿态沟通，心态更平衡。",
            ],
        },
        {
            "headline": "借着这股生长感，为未来几周打下基础。",
            "items": [
                "在日历上规划运动与休息交错的节奏，避免一次冲太猛反而筋疲力尽。",
                "与身体对话：评估睡眠、排便、肤况等指标，逐步调成理想模样。",
                "练习“积极肯定”写作，具体记录三个感谢自己的理由，提高自信。",
            ],
        },
    ],
    "ovulation": [
        {
            "headline": "排卵期是自信值最高的时段，记得好好享受并守护界限。",
            "items": [
                "将重要简报、谈判或曝光安排在这几天，会更敢表达观点。",
                "若安排亲密互动，事前沟通欲望、界线与安全措施，保持尊重与乐趣。",
                "补充足够水分与电解质，避免因活动增加而忽略身体消耗。",
            ],
        },
        {
            "headline": "社交雷达灵敏时，也要准备一个舒适的出口帮情绪降温。",
            "items": [
                "尝试新的香氛、服装或妆容，让自己感受魅力和掌控感。",
                "把高强度训练或舞蹈留给此刻，借助激素优势练出爆发力。",
                "结束忙碌行程后立即安排长时间泡脚或冥想，避免神经过度兴奋。",
            ],
        },
        {
            "headline": "把握灵感高峰期，同时培养勇敢与觉察并存的能力。",
            "items": [
                "列出想主动推进的人际连接，发出邀请或给出肯定反馈。",
                "开启想尝试已久的内容创作或公开分享，声音更容易被听见。",
                "设置夜间的放松仪式，提醒自己从“亮度模式”切换到“修复模式”。",
            ],
        },
        {
            "headline": "能量旺盛易忽略界线，提醒自己适时休息与说“不”。",
            "items": [
                "在日程中插入可调节的缓冲带，防止行程堆叠导致情绪透支。",
                "若单身，可尝试高质量约会，但记得明确意图，保护内心安全。",
                "搭配含镁与维生素 B6 的饮食，帮助神经系统维持稳定。",
            ],
        },
        {
            "headline": "如果选择俏皮路线也别忘了尊重自己和他人的节奏。",
            "items": [
                "给自己一份大胆又舒适的礼物：一件喜欢的衣服或一次独处的短旅程。",
                "写下此刻最想达成的心愿与感受，未来低潮时拿出来提醒自己足够闪耀。",
                "建立“安全词”或支持名单，让所有冒险都在可控范围内进行。",
            ],
        },
    ],
    "luteal": [
        {
            "headline": "黄体期像情绪脚踏车，提前布置柔软的缓冲垫。",
            "items": [
                "调整咖啡因摄入，改喝花草茶或温水，以免加剧情绪波动。",
                "规划“整理角落”或慢速家务，边动手边整理思绪有助放松。",
                "和信任的人约定“预警机制”，当你发出暗号时对方知道需要支持。",
            ],
        },
        {
            "headline": "把“慢下来”当成策略，而不是失败。",
            "items": [
                "采用 20 分钟轻度运动配合缓慢拉伸，帮助身体消耗焦躁能量。",
                "准备高纤维加优质脂肪的零食，缓解暴食与血糖过山车。",
                "将需要情绪稳定的任务移到白天，晚上专注于放松与自我照顾。",
            ],
        },
        {
            "headline": "当情绪变得敏感，多一份规划就少一点冲突。",
            "items": [
                "提前告知身边人“我这几天可能比较脆弱”，设置期望更轻松。",
                "练习情绪标签：用更具体的字词描述感受，帮助大脑进入理性区。",
                "准备舒适的香氛或助眠音乐，提升睡眠质量减轻易怒。",
            ],
        },
        {
            "headline": "经前期常常放大焦虑，请寻找让自己踏实的仪式。",
            "items": [
                "建立固定的夜间书写流程，写下担心的事并列出可执行步骤。",
                "适度摄取富含色氨酸与镁的食物，如燕麦、香蕉与坚果，帮助神经放松。",
                "若出现严重的经前不适，勇敢寻求专业支持并评估补充剂或药物。",
            ],
        },
        {
            "headline": "将黄体期视为复盘阶段，好好与自己和解。",
            "items": [
                "给自己设定“温柔闹钟”，提醒多喝水、伸展、离开屏幕。",
                "练习对话式冥想：询问身体今天想要什么，再用行动回应它。",
                "把下一周期想完成的愿望写在便利贴上，提醒自己每阶段都在前进。",
            ],
        },
    ],
}

PARTNER_ADVICE_VARIANTS = {
    "menstruation": [
        {
            "headline": "经期的她对温度与语气更敏感，主动成为她的安全带。",
            "tips": [
                "留意她的脸色与动作，主动问一句“要不要我替你做某件事”。",
                "准备热水、暖宝宝或舒适的靠垫，把环境变得柔软一点。",
                "适时承担部分家务，让她不用为了琐事分神，身体才能休息。",
            ],
            "phrases": [
                "“如果你懒得动，我现在就去帮你倒热水，加柠檬还是姜片？”",
                "“今晚的家务别管了，我全部包下，你只要躺好。”",
                "“想不想靠在我肩上休息一会儿？我可以安静陪你发呆。”",
                "“你不用解释为什么心情不好，我在你身边，陪你一起扛。”",
                "“要不要我帮你联系医生或买止痛药？你只需要讲一个口令。”",
            ],
        },
        {
            "headline": "她可能情绪低落或脾气急，你给的理解越具体越有效。",
            "tips": [
                "用“我看见/我听见”开头描述你注意到的细节，表示你真正在意。",
                "即使你帮不上忙，也可以说“我在这”，提供稳定的存在感。",
                "主动替她挡掉非必要的社交与差事，守护她的小宇宙。",
            ],
            "phrases": [
                "“我看你今天气色不太好，不如我替你跟朋友说改期吧？”",
                "“我可以帮你挡住家里的杂事，你专心照顾自己就好。”",
                "“你愿意让我抱抱你吗？我只想让你舒服一点。”",
                "“我们一起看个轻松的影片好吗？你只要点头，我马上搞定设备。”",
                "“如果你想大哭或发脾气，我可以安静听着，绝不评判。”",
            ],
        },
        {
            "headline": "表达体贴的细节越多，她越能感到踏实与被理解。",
            "tips": [
                "准备一份经期应急包，例如护垫、止痛药、巧克力与暖贴。",
                "在她工作或学习时递上一杯温水，让她知道有人在乎她的状态。",
                "用眼神与肢体语言表示你愿意承担更多，不必等她开口。",
            ],
            "phrases": [
                "“我刚刚在包里放了你的暖宫贴，你需要时随时拿。”",
                "“我帮你查了附近哪家药局还有你常用的止痛药，要不要一起去？”",
                "“今天的行程我们可以完全照你的舒适度调整，你说了算。”",
                "“你只要负责舒服，其他的生活杂事我来处理，放心交给我。”",
                "“想吃什么告诉我，我马上点外卖或者亲自下厨。”",
            ],
        },
        {
            "headline": "经期时别急着给解决方案，先给拥抱、再问需求。",
            "tips": [
                "出现冲突时先暂停，用温柔语气说“我们可以晚点再聊”。",
                "准备一个守护清单：热水瓶、棉被、零食、剧集等随叫随到。",
                "尊重她想独处或想分享的选择，回应她“我听见了”。",
            ],
            "phrases": [
                "“你想要空间我就退一步，你想说话我就认真听，你决定。”",
                "“我把热水袋已经加热好了，你躺下我帮你放在小腹上。”",
                "“你只要摆出想吃的表情，我就去厨房翻东西。”",
                "“我们先暂停争论，我知道你现在需要的是被拥抱。”",
                "“我可以包办今晚的生活琐事，你就放空吧。”",
            ],
        },
        {
            "headline": "当她疼痛或情绪起伏时，一句暖心话胜过任何大道理。",
            "tips": [
                "时常提醒她“你可以脆弱”，给予肯定与安全感。",
                "提出实际可行的协助，例如帮忙预约、购药或陪诊。",
                "给她准备柔软的灯光与音乐，让空间也加入疗愈行列。",
            ],
            "phrases": [
                "“你不需要逞强，我可以当你的靠山。”",
                "“如果你半夜痛醒，随时叫醒我，我会马上起床帮你。”",
                "“我刚调好了你喜欢的灯光和音乐，希望能让你舒服一点。”",
                "“今晚你什么都不用做，只要告诉我你想被怎样照顾。”",
                "“我已经帮你把明天的行程挪掉了，你只要照顾好身体。”",
            ],
        },
    ],
    "follicular": [
        {
            "headline": "她的能量回升，需要你成为最佳队友共同规划新节奏。",
            "tips": [
                "鼓励她尝试新点子，提供后勤支持让她更专注于突破。",
                "主动安排健康的共同行程，如晨跑或轻度健身。",
                "肯定她的努力，同时提醒她保持休息，避免用力过猛。",
            ],
            "phrases": [
                "“你想启动的计划我们一起来排时间表，我可以当你的项目经理。”",
                "“明早我闹钟调好，带你去晨跑，跑完我请你喝豆浆。”",
                "“我帮你整理好书桌和设备，你专心发光就好。”",
                "“你的新点子真棒，要不要我帮你做简报或资料搜集？”",
                "“你忙的时候我来准备餐食，保证你有能量继续升级。”",
            ],
        },
        {
            "headline": "这阶段的她适合拓展社交与学习，陪她一起拥抱成长。",
            "tips": [
                "帮她记录灵感或愿望清单，提醒她逐一实现。",
                "安排一句真诚赞美，让她知道你观察到她的进步。",
                "若她想尝试新体验，做那个勇敢说“走啊”的伙伴。",
            ],
            "phrases": [
                "“你刚刚分享的想法我做成备忘录了，等你想推进时直接用。”",
                "“今晚我开车陪你去上课，下课顺便请你吃宵夜。”",
                "“你最近状态超好，我们来个拍照日把这份自信记录下来。”",
                "“你只要说一声想学习什么，我立刻帮你报名或找资源。”",
                "“我会提醒你适时休息，也会第一时间庆祝你的每个小成就。”",
            ],
        },
        {
            "headline": "她在建构新的节奏，你提供稳定后盾她就能跑得更远。",
            "tips": [
                "分担琐事让她专注目标，展现无条件的支持。",
                "主动询问她需要哪种鼓励，是肯定、陪伴或资源。",
                "把她的日程记在心里，重要时刻送上暖心惊喜。",
            ],
            "phrases": [
                "“我已经把你的重要会议写进我的行事历，到时提醒你。”",
                "“你要我帮忙督促运动还是饮食？我可以当最可靠的打卡伙伴。”",
                "“看得出你最近很努力，我超骄傲，想不想庆祝一下？”",
                "“你安心往前冲，生活后勤我全部cover。”",
                "“如果你要练习新技能，我可以当听众或假想客户。”",
            ],
        },
        {
            "headline": "能量回升也容易忽视休息，你可以温柔地帮她踩刹车。",
            "tips": [
                "提醒她安排恢复时间，不必把日程塞满。",
                "当她分心时，用幽默方式拉她回到身体感受。",
                "给她按摩肩颈或准备营养餐盒，守住基本体力。",
            ],
            "phrases": [
                "“今天的待办超多，我帮你挑几个可以延后的，好吗？”",
                "“闭上眼睛我帮你按肩膀两分钟，补充一点电力。”",
                "“你冲太快了，我来做你的节奏控制员，帮你排休息。”",
                "“我在冰箱放了高蛋白餐盒，忙时可以直接加热吃。”",
                "“我会在重要场合当你的拉拉队，也会提醒你喝水。”",
            ],
        },
        {
            "headline": "陪她一起制定阶段性目标，把彼此的步伐同步。",
            "tips": [
                "邀请她分享近期灵感，用问题引导她整理思路。",
                "准备共同看板或笔记，记录你们的计划与感受。",
                "在她犹豫时告诉她“你值得”，为她加速。",
            ],
            "phrases": [
                "“我们一起来开一个共享清单，把你的灵感全部写进去。”",
                "“如果你想要练习展示，我当观众给你最真诚的反馈。”",
                "“你的成长我看在眼里，想不想今晚聊聊下一步？”",
                "“我已经准备好庆祝清单，只等你完成任务就一起打卡。”",
                "“你尽管放心地去冒险，我就是你最稳的落点。”",
            ],
        },
    ],
    "ovulation": [
        {
            "headline": "排卵期的她更闪亮也更敏感，你的尊重会让她倍感安心。",
            "tips": [
                "安排浪漫但可控的活动，让她释放能量又不被耗尽。",
                "谈论愿景与梦想，借助她的自信值制定共同目标。",
                "在亲密互动前先确认界限与期待，展现成熟与体贴。",
            ],
            "phrases": [
                "“今晚想不想去你一直想试的那家餐厅？我已经预约了。”",
                "“你的魅力今天爆棚，我想和你一起记录这份光芒。”",
                "“如果你想亲密一点，我会放慢速度，确保你随时可以说停。”",
                "“我们可以聊聊未来几个月的计划吗？我想和你并肩去实现。”",
                "“你今天的每个想法都很酷，我愿意当那个最认真倾听的人。”",
            ],
        },
        {
            "headline": "她社交力强时别只当观众，要当她的专属助理兼守护者。",
            "tips": [
                "主动提供后勤支持，例如开车接送或准备补给。",
                "观察她是否过度耗能，及时帮她安排“退出”策略。",
                "以真诚赞美回应她的自信，别泼冷水。",
            ],
            "phrases": [
                "“我今天当你的专属司机，你只要负责闪耀。”",
                "“我在包里放了水跟营养棒，累了就来找我。”",
                "“你随时想离开我就给你一个‘暗号’，我马上护送你撤退。”",
                "“你的笑容今天特别迷人，我要珍藏这个版本的你。”",
                "“如果你要我帮忙过滤邀约，直接把标准告诉我，我来处理。”",
            ],
        },
        {
            "headline": "欲望的表达需要双向同意，你的细腻会让她更放松。",
            "tips": [
                "约会时先聊感受与界限，展现你对她的尊重。",
                "亲密之前准备好保护措施与舒适环境。",
                "给她空间选择节奏，尊重每一次“暂停”。",
            ],
            "phrases": [
                "“我们今晚可以慢慢来，你随时想停就跟我说，我都会照做。”",
                "“我准备了你喜欢的香气和音乐，希望让你感觉安心。”",
                "“我随身带了安全措施，想法一致我们再继续。”",
                "“你愿意和我聊聊现在的界线吗？我想确保我们都舒服。”",
                "“我喜欢你勇敢表达的样子，也会好好守护你的羞涩。”",
            ],
        },
        {
            "headline": "她在舞台中央时需要一个懂得打灯又随时挡刀的搭档。",
            "tips": [
                "替她记下赞美或灵感，回家后一起复盘让充实感持续。",
                "提醒她补水与休息，避免一口气过载。",
                "当她被误解或遭到冒犯时迅速站出来护航。",
            ],
            "phrases": [
                "“我帮你记下了大家对你的称赞，回家后一起回味。”",
                "“我知道你会拼到底，但我更想看到你笑着回家。”",
                "“有人不懂得尊重你我就出面处理，你只管继续发光。”",
                "“我在旁边看着就很骄傲，你愿意让我当今晚的记录者吗？”",
                "“需要我帮你挡掉哪个邀约吗？我可以直接替你拒绝。”",
            ],
        },
        {
            "headline": "当她想尝试新鲜事，你负责为她铺好软垫与撤退路线。",
            "tips": [
                "主动预约体验项目，并事先确认安全细节。",
                "把她喜欢的惊喜准备在活动后，延续好情绪。",
                "提醒她如果感到疲惫可以随时停下，不必取悦任何人。",
            ],
            "phrases": [
                "“我把你提过的体验课都排好了，你只要选喜欢的时间。”",
                "“活动结束后我准备了你爱吃的小甜点，帮你补充快乐能量。”",
                "“如果哪一步你觉得不舒服，我们立刻回家，谁都别管。”",
                "“我会一路观察你的表情，只要你皱眉我就马上护你。”",
                "“今晚所有安排都围绕你的感受来调整，你说了算。”",
            ],
        },
    ],
    "luteal": [
        {
            "headline": "黄体期像情绪云雨带，你要当稳定的晴空塔。",
            "tips": [
                "帮助她拆解烦躁原因，并提供具体协助选项。",
                "安排温柔的共处活动，让她感到被理解。",
                "提醒她适时休息，别硬撑社交或工作。",
            ],
            "phrases": [
                "“你只要告诉我哪件事最烦，我帮你想办法或直接去做。”",
                "“我们今晚关掉社交，窝在沙发看电影，我负责准备零食。”",
                "“如果你想骂人就对我骂没关系，我是你的垃圾回收桶。”",
                "“我在日历上帮你挪掉了几个行程，希望你能多睡一会儿。”",
                "“你不需要表现强大，我喜欢你所有真实的样子。”",
            ],
        },
        {
            "headline": "经前期容易自我怀疑，你的肯定要详实具体才能入心。",
            "tips": [
                "列举她近期完成的事情，让她看到真实成果。",
                "在她易怒时，用轻声与身体接触带来安全感。",
                "准备舒缓的香氛、音乐或热饮，营造安心氛围。",
            ],
            "phrases": [
                "“这周你完成三份提案、陪我两次约会，还照顾好自己，我全看在眼里。”",
                "“如果你今天不想说话，我们就静静牵手散步就好。”",
                "“我帮你准备了洋甘菊茶和薰衣草精油，睡前我们一起放松。”",
                "“你可以对我任性，明天醒来我依旧在你身边。”",
                "“你的焦虑我懂，我愿意当你最可靠的防波堤。”",
            ],
        },
        {
            "headline": "帮助她建立缓冲仪式，让情绪有处安放。",
            "tips": [
                "一起制定“温柔守则”：例如睡前不讨论争议话题。",
                "陪她做轻瑜伽或拉伸，边动边说说心事。",
                "帮她准备营养密度高的食物，稳定血糖。",
            ],
            "phrases": [
                "“今晚我们遵守温柔守则，只聊舒心的事，你看如何？”",
                "“我放好瑜伽垫了，想不想一边伸展一边聊聊最近的烦恼？”",
                "“冰箱我备了你喜欢的坚果和酸奶，饿了随时拿。”",
                "“你担心的事我们写下来，一条条想办法解决。”",
                "“你的情绪波动我能接住，我会一直在。”",
            ],
        },
        {
            "headline": "她容易对自己苛刻，你来提醒她已经够好并提供具体帮忙。",
            "tips": [
                "把她的优点说得具体，例如“我喜欢你认真又温柔的样子”。",
                "主动承担规划或决策，让她暂时放空。",
                "如果她说“不想社交”，帮她果断拒绝邀请。",
            ],
            "phrases": [
                "“我会负责和大家说明你需要休息，他们都会理解的。”",
                "“你的努力让我心疼，我想让你轻松一点，把任务交给我。”",
                "“你已经做得很好了，剩下的交给我来扛。”",
                "“今晚我们照顾好身体，其他的明天再战。”",
                "“我想听听你的担心，也想亲手为你减轻其中几项。”",
            ],
        },
        {
            "headline": "提前告知她你是最值得信赖的伙伴，情绪来了就依靠你。",
            "tips": [
                "建立“支持暗号”，她只要说出一个词你就知道要做什么。",
                "每晚固定问一句“今天有什么想让我做的吗”。",
                "帮她追踪睡眠、饮食与运动，温柔提醒调整。",
            ],
            "phrases": [
                "“记得我们的暗号吗？只要你说‘灯塔’，我就立刻赶到你身边。”",
                "“今天有没有哪件事想让我处理？我随叫随到。”",
                "“我帮你在手机上设了喝水提醒，你不想动时我就把杯子递过去。”",
                "“你若想聊天或沉默我都陪你，情绪来袭时也别客气叫我。”",
                "“我们一起追踪作息，等这阶段过去你会发现自己被好好照顾了。”",
            ],
        },
    ],
}


def _parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ValueError("请按照 YYYY-MM-DD 的格式填写日期。") from exc


def _gaussian(x: float, mu: float, sigma: float, height: float = 1.0) -> float:
    return height * exp(-((x - mu) ** 2) / (2 * sigma * sigma))


def _estimate_phase_key(cycle_day: int, cycle_length: int, menses_days: int, luteal_length: int = 14) -> str:
    ovulation_day = max(1, cycle_length - luteal_length)
    menses = range(1, menses_days + 1)
    ov_start = max(1, ovulation_day - 1)
    ov_end = min(cycle_length, ovulation_day + 1)
    ovulation = range(ov_start, ov_end + 1)
    luteal = range(ov_end + 1, cycle_length + 1)

    if cycle_day in menses:
        return "menstruation"
    if cycle_day in ovulation:
        return "ovulation"
    if cycle_day in luteal:
        return "luteal"
    return "follicular"


def _estimate_hormone_levels(cycle_day: int, cycle_length: int) -> Dict[str, int]:
    x = float(cycle_day)
    L = float(cycle_length)
    mu_est = max(2.0, L - 14.0)
    est_peak = _gaussian(x, mu_est, sigma=2.0, height=1.0)
    est_luteal = _gaussian(x, mu_est + 6.0, sigma=6.0, height=0.5)
    est_val = max(est_peak, est_luteal)

    mu_prog = mu_est + 5.0
    prog_val = _gaussian(x, mu_prog, sigma=4.0, height=1.0)

    lh_val = _gaussian(x, mu_est, sigma=0.8, height=1.0)
    t_val = _gaussian(x, mu_est, sigma=2.3, height=0.4)

    raw = {
        "estrogen": est_val,
        "progesterone": prog_val,
        "LH": lh_val,
        "testosterone": t_val,
    }
    base = max(raw.values()) or 1.0
    return {key: int(round((value / base) * 100)) for key, value in raw.items()}


def _advice_for_phase(
    phase_key: str,
    role: str,
    tone: str,
    seed: str | None = None,
) -> Dict[str, List[str] | str]:
    role = role if role in {"self", "partner"} else "self"
    tone = tone if tone in {"gentle", "playful"} else "gentle"

    if role == "self":
        variants = SELF_ADVICE_VARIANTS.get(phase_key) or SELF_ADVICE_VARIANTS["follicular"]
    else:
        variants = PARTNER_ADVICE_VARIANTS.get(phase_key) or PARTNER_ADVICE_VARIANTS["follicular"]

    # tone currently only affects排卵 self variant text, embed by adjusting headline earlier.
    if role == "self" and phase_key == "ovulation" and tone == "playful":
        # ensure至少一个玩味版本 first variant is playful? first entry not necessarily. we can adjust by editing first variant to include? Another approach: incre injection.
        variants = [
            {
                **variants[4],
                "headline": variants[4]["headline"].replace("如果选择俏皮路线", "⚡️ 排卵期玩心大开也别忘了界限"),
            }
        ] + variants[:4]

    rng_seed = f"{phase_key}-{role}-{tone}-{seed or ''}"
    rng = random.Random(rng_seed)
    return rng.choice(variants)


def calculate_cycle_details(
    last_period_date: str,
    *,
    observation_date: str | None = None,
    cycle_length: int = DEFAULT_CYCLE_LENGTH,
    menses_days: int = DEFAULT_MENSES_DAYS,
    role: str = "self",
    tone: str = "gentle",
) -> Dict[str, object]:
    if not last_period_date:
        raise ValueError("请填写上次月经开始日期。")
    if cycle_length < 20 or cycle_length > 40:
        raise ValueError("周期长度建议在 20-40 天之间。")
    if menses_days < 1 or menses_days > 10:
        raise ValueError("经期持续天数建议在 1-10 天之间。")

    start = _parse_date(last_period_date)
    observed = date.today() if not observation_date else _parse_date(observation_date)
    delta = (observed - start).days
    if delta < 0:
        raise ValueError("观察日期不能早于上次月经开始日期。")

    cycle_day = (delta % cycle_length) + 1
    phase_key = _estimate_phase_key(cycle_day, cycle_length, menses_days)
    hormones = _estimate_hormone_levels(cycle_day, cycle_length)
    symptoms = SYMPTOM_LIBRARY.get(phase_key, [])
    seed_value = f"{observed.isoformat()}-{cycle_day}"
    advice = _advice_for_phase(phase_key, role=role, tone=tone, seed=seed_value)

    return {
        "cycle_day": cycle_day,
        "cycle_length": cycle_length,
        "phase": PHASE_NAMES[phase_key],
        "phase_key": phase_key,
        "hormones": hormones,
        "symptoms": symptoms,
        "advice": advice,
        "observed_date": observed.isoformat(),
    }


def calculate_hormone_status(last_period_date: str, gender: str) -> Dict[str, object]:
    normalized = (gender or "female").lower()
    role = "self" if normalized == "female" else "partner"
    details = calculate_cycle_details(last_period_date, role=role)

    advice_text = details["advice"].get("headline", "")
    detail_items = details["advice"].get("items") or details["advice"].get("tips") or []
    suggestion = (advice_text + " " + " ".join(detail_items)).strip()

    return {
        "cycle_day": details["cycle_day"],
        "phase": details["phase"],
        "estrogen": float(details["hormones"]["estrogen"]),
        "progesterone": float(details["hormones"]["progesterone"]),
        "symptoms": details["symptoms"],
        "suggestions": suggestion or "根据自身感受调整节奏与日程。",
    }


__all__ = ["calculate_hormone_status", "calculate_cycle_details"]
