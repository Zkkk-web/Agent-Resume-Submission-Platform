from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 960, 540
FPS = 7
OUT = Path(__file__).with_name("product-demo.gif")
FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"


def font(size, bold=False):
    return ImageFont.truetype(FONT, size=size, index=1 if bold else 0)


def rounded(draw, box, radius=16, fill="white", outline="#DDDDDD", width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def text(draw, xy, value, size, fill="#111111", bold=False, anchor=None):
    draw.text(xy, value, font=font(size, bold), fill=fill, anchor=anchor)


def check(draw, x, y, dark=True):
    fill = "#111111" if dark else "white"
    stroke = "white" if dark else "#111111"
    draw.rectangle((x, y, x + 20, y + 20), fill=fill, outline="#111111", width=2)
    draw.line((x + 5, y + 10, x + 9, y + 14, x + 16, y + 6), fill=stroke, width=2)


def base(step, title, subtitle):
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)
    rounded(d, (24, 22, W - 24, H - 22), 22, "white", "#111111", 2)
    d.line((24, 78, W - 24, 78), fill="#111111", width=2)
    for x, fill in [(54, "#111111"), (76, "white"), (98, "white")]:
        d.ellipse((x - 6, 50 - 6, x + 6, 50 + 6), fill=fill, outline="#111111", width=2)
    text(d, (128, 50), "天才职业顾问 @ 泛函", 16, bold=True, anchor="lm")
    text(d, (W - 54, 50), "LOCAL FIRST", 12, fill="#777777", anchor="rm")
    text(d, (56, 116), title, 28, bold=True)
    text(d, (56, 151), subtitle, 14, fill="#666666")
    steps = ["读简历", "懂经历", "找岗位", "改简历", "辅助申请"]
    x0, gap = 596, 64
    for i, label in enumerate(steps):
        cx = x0 + i * gap
        active = i <= step
        d.ellipse((cx - 11, 110, cx + 11, 132), fill="#111111" if active else "white", outline="#111111", width=2)
        text(d, (cx, 121), str(i + 1), 9, fill="white" if active else "#111111", bold=True, anchor="mm")
        text(d, (cx, 147), label, 10, fill="#111111" if active else "#999999", anchor="mm")
        if i < 4:
            d.line((cx + 12, 121, cx + gap - 12, 121), fill="#111111" if i < step else "#DDDDDD", width=2)
    return im, d


def scene_one():
    im, d = base(0, "一句话开始找工作", "上传简历，剩下的流程由 Skill 自己推进。")
    rounded(d, (72, 205, 598, 279), 18, "#111111", "#111111")
    text(d, (98, 242), "帮我找适合的 AI 产品岗位，这是我的简历。", 17, fill="white", anchor="lm")
    rounded(d, (640, 205, 858, 279), 18, "#FFF7BF", "#111111")
    text(d, (749, 232), "林澄-简历.pdf", 14, bold=True, anchor="mm")
    text(d, (749, 254), "PDF · 已读取", 11, fill="#666666", anchor="mm")
    text(d, (72, 340), "我先在本地读材料，不会上传或投递。", 17, bold=True)
    for y, label in [(388, "原始简历保持不变"), (429, "未授权前不发送个人资料")]:
        check(d, 74, y - 14)
        text(d, (110, y - 4), label, 14, anchor="lm")
    return im


def scene_two():
    im, d = base(1, "先了解你，再推荐岗位", "从材料和简短追问中建立可长期复用的职业档案。")
    rounded(d, (58, 194, 430, 475), 18, "#F7F7F7", "#DDDDDD")
    text(d, (86, 228), "职业档案", 19, bold=True)
    for y, head, body in [
        (276, "目标方向", "AI 产品经理 / Agent 产品"),
        (326, "代表项目", "客服 Agent：自动解决率 34% → 63%"),
        (376, "个人贡献", "需求拆解、评测集、上线复盘"),
        (426, "意向地点", "杭州优先，可远程"),
    ]:
        text(d, (86, y), head, 12, fill="#777777")
        text(d, (174, y), body, 14, bold=True)
    rounded(d, (478, 214, 884, 328), 18, "white", "#111111")
    text(d, (506, 246), "Agent", 12, fill="#777777", bold=True)
    text(d, (506, 278), "你在这个项目里亲自做出的关键判断是什么？", 16, bold=True)
    rounded(d, (560, 354, 884, 446), 18, "#111111", "#111111")
    text(d, (584, 384), "候选人", 11, fill="#BBBBBB", bold=True)
    text(d, (584, 417), "我把模糊需求拆成评测集和验收指标……", 14, fill="white")
    return im


def scene_three():
    im, d = base(2, "63 个岗位来源，一起搜索", "从适合你的渠道中统一筛选、去重和排序。")
    sources = [("招聘官网", "持续更新"), ("招聘社区", "多类岗位"), ("聚合平台", "统一整理")]
    for i, (name, count) in enumerate(sources):
        x = 58 + i * 174
        rounded(d, (x, 205, x + 150, 285), 14, "white", "#111111")
        text(d, (x + 20, 232), name, 15, bold=True)
        text(d, (x + 20, 261), count, 12, fill="#777777")
        d.line((x + 75, 286, 610, 335), fill="#BBBBBB", width=2)
    rounded(d, (610, 194, 892, 458), 18, "#F7F7F7", "#DDDDDD")
    text(d, (634, 228), "统一候选清单", 18, bold=True)
    rows = [
        ("01", "AI 产品经理 · 杭州", "高匹配", "#FFF7BF"),
        ("02", "Agent 产品经理 · 远程", "高匹配", "white"),
        ("03", "AI 产品实习生 · 深圳", "较匹配", "white"),
    ]
    for i, (n, role, score, bg) in enumerate(rows):
        y = 258 + i * 58
        rounded(d, (628, y, 874, y + 44), 10, bg, "#D8D8D8", 1)
        text(d, (644, y + 22), n, 11, fill="#777777", bold=True, anchor="lm")
        text(d, (674, y + 22), role, 12, bold=True, anchor="lm")
        text(d, (858, y + 22), score, 11, bold=True, anchor="rm")
    for y, label in [(360, "推荐范围先由你确认"), (402, "会员、登录和暂不可用会如实标记"), (444, "同一岗位自动去重")]:
        check(d, 58, y - 10)
        text(d, (92, y), label, 14, bold=True, anchor="lm")
    return im


def scene_four():
    im, d = base(3, "选定 JD 后，只补最关键的信息", "不是机械改词，而是把真实经历变成岗位需要的证据。")
    rounded(d, (58, 198, 440, 462), 18, "white", "#111111")
    text(d, (86, 230), "岗位要求", 17, bold=True)
    requirements = ["Agent 产品经验", "评测集与数据复盘", "跨团队推动上线"]
    for i, req in enumerate(requirements):
        y = 278 + i * 54
        d.ellipse((86, y - 9, 104, y + 9), fill="#111111")
        if i < 2:
            d.line((90, y, 94, y + 4, 101, y - 4), fill="white", width=2)
        else:
            text(d, (95, y), "?", 11, fill="white", bold=True, anchor="mm")
        text(d, (120, y), req, 15, bold=True, anchor="lm")
    rounded(d, (486, 198, 892, 318), 18, "#FFF7BF", "#111111")
    text(d, (514, 229), "针对性问题", 12, fill="#666666", bold=True)
    text(d, (514, 262), "你如何推动算法、研发和业务", 16, bold=True)
    text(d, (514, 289), "共同完成上线验收？", 16, bold=True)
    rounded(d, (486, 342, 892, 462), 18, "#111111", "#111111")
    text(d, (514, 373), "写入岗位专用简历", 12, fill="#BBBBBB", bold=True)
    text(d, (514, 408), "补充：建立 Issue → PR → CI 的验收闭环", 15, fill="white", bold=True)
    text(d, (514, 435), "保留原简历，不编造经历", 12, fill="#BBBBBB")
    return im


def scene_five():
    im, d = base(4, "你检查，Agent 辅助申请", "简历可以编辑；登录、验证码和最终提交仍由你完成。")
    rounded(d, (58, 198, 578, 460), 18, "white", "#111111")
    text(d, (86, 230), "林澄｜AI 产品经理", 20, bold=True)
    d.line((86, 249, 548, 249), fill="#DDDDDD", width=2)
    for y, title, detail in [
        (288, "客服 Agent 产品", "自动解决率 34% → 63%"),
        (344, "评测与迭代", "80 条核心评测集 · 18 个 PR"),
        (400, "协作与交付", "Issue → PR → CI 端到端验收"),
    ]:
        text(d, (86, y), title, 14, bold=True)
        text(d, (230, y), detail, 13, fill="#666666")
    rounded(d, (620, 218, 888, 286), 14, "#111111", "#111111")
    text(d, (754, 252), "打开可编辑 HTML", 15, fill="white", bold=True, anchor="mm")
    rounded(d, (620, 314, 888, 382), 14, "#FFF7BF", "#111111")
    text(d, (754, 348), "确认后辅助填写", 15, bold=True, anchor="mm")
    text(d, (754, 426), "最终提交由你点击", 14, fill="#666666", bold=True, anchor="mm")
    return im


def main():
    scenes = [scene_one(), scene_two(), scene_three(), scene_four(), scene_five()]
    frames = []
    hold = 11
    fade = 3
    for i, current in enumerate(scenes):
        frames.extend([current.copy() for _ in range(hold)])
        if i + 1 < len(scenes):
            nxt = scenes[i + 1]
            frames.extend(Image.blend(current, nxt, (j + 1) / (fade + 1)) for j in range(fade))
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=round(1000 / FPS),
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(OUT)


if __name__ == "__main__":
    main()
