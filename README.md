# 多语言文本与音频生产管线

面向已上线手游项目的生产管线：把从引擎与表格导出的、分散各处的文本与音频信息，
收敛成引擎可直接消费的配置表。

覆盖语言：简体中文 / 日文 / 韩文 / 英文 / 德文 / 法文。

---

## 目录结构

```
Designmode-Portfolio/
├── tools/          代码：文本管线 9 个、音频管线 9 个、批处理 11 个
├── config/         配置层示例：类型注册表、校验清单、字段黑名单、proto 别名
├── launchers/      6 个双击入口
├── samples/        三条可运行 demo（虚构数据）
├── spec/           可校验规范：5 条规则 + 执行器 + 两条用例
└── docs/           设计产出
```

## 一、管线结构

### 文本管线

两条入口结构相同（**散文件 → 汇总表**），最后按 ukey 合流：

```
   引擎 / 表格导出
   ├── SETextCSV/*.csv                按功能类别导出的文本 CSV
   │       │  列名规则：<表名>_SGL_<语言> / <表名>_PLR_<语言> / <表名>_<类型>_<语言>
   │       ▼
   │   generate_se_csv_text.py ──────► SEText_output/se_text_00_csv.xlsx
   │
   └── SETextTXTSource/*.txt          扁平的 <key>_<语言>.txt
           │  ① 按 key 归档成目录  ② 解析 @: 分块
           ▼
       generate_se_txt_text.py ──────► SEText_output/se_text_00_txt.xlsx

                    ┌──────────────────────┴──────────────────────┐
                    ▼                                             ▼
            merge_se_text.py                             validate_config.py
            按 ukey 合并两个来源                            表头 ↔ proto 类型校验
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  se_text_ukey.xlsx      exception.xlsx
  （最终文本表）           （一对多翻译异常）

                    │
                    ▼
              引擎侧消费 / 打包交付
```

### 音频管线

```
   sci / bpx 资源 ──► Sound table export.py ──► 音效表（含 WAV / MD5 列）
                                       │
                        ┌──────────────┴──────────────┐
                        ▼                             ▼
              Sound wav export.py            SoundMD5ToCSV.py
              Scenario* export.py            （wav/aif → MD5，完整性校验）
                        │
                        ▼
              Merge sound and wav.py（音效表与资源核对）
```

### 配置层在管线中的位置

```
se_csv_text_type.json        ──► 两个生成入口（决定按哪些列名去捞文本）
translate_config.json        ──► validate_config.py（决定哪些字段必须校验为字符串）
LocalizationBlacklist.json   ──► 产出过滤（决定哪些字段不进翻译流程）
```

## 二、`tools/` 工具

### `tools/localization/` —— 文本管线（9 个）

| 脚本 | 作用 |
|---|---|
| `util.py` | 共享契约：语言集合与列序、默认 sheet 名、换行标识 `<br>`、`is_invalid_chinese()` |
| `generate_se_csv_text.py` | 读按类别导出的 CSV，按 `<表名>_<类型>_<语言>` 列名提取，汇总进 `se_text_00_csv.xlsx` |
| `generate_se_txt_text.py` | 读扁平 `<key>_<语言>.txt`，先按 key 归档成目录，再解析 `@:` 分块汇总进 `se_text_00_txt.xlsx` |
| `merge_se_text.py` | 按 ukey 合并，产出 `se_text_ukey.xlsx`；一对多的翻译另存 `exception.xlsx` |
| `validate_config.py` | 调 Protocol 生成脚本，逐字段校验表头是否为字符串类型，不通过即报错 |
| `proto_util.py` | proto 类型解析（`get_cpp_type` / `find_message_types` / `CPPTYPE_STRING`） |
| `localization_cfg.py` | 配置驱动引擎：递归 `Name/Children`、默认值逐层继承、重复字段自动生成 `_{field}Num` 计数列 |
| `json_to_lua.py` | JSON → Lua 序列化 |
| `localization_util.py` | 工作路径与字段元数据管理 |

### `tools/sound/` —— 音频管线（9 个）

| 脚本 | 作用 |
|---|---|
| `Sound table export.py` | 最大的一支（21.9 KB）：扫描 sci / bpx 资源，构建音效表（含 `WAV` / `MD5` 列） |
| `Sound wav export.py` | 按表导出 wav，并产出导出清单 |
| `Scenario table export.py` | 场景音效表：列为 `EventName / WAV(SE) / WAV(Project) / MD5` |
| `Scenario wav export.py` | 场景语音导出 |
| `Merge sound and wav.py` / `_other.py` | 把音效表与实际资源合并核对 |
| `SoundMD5ToCSV.py` | 遍历目录下 wav / aif / aiff 计算 MD5 转表 |
| `CopyThat.py` | 资源批量拷贝 |
| `illusion.py` | 读取目录下 txt 的内容与文件名清单 |

### `tools/batch/` —— 批处理（11 个）

| 脚本 | 作用 |
|---|---|
| `MergeXlsx.py` / `Mergez.py` | 把音频索引表与产出表合并成总表 |
| `Readir.py` / `ReadAndTrans.py` / `ReadAndTrans1.py` | 目录遍历 + 把客户端绝对路径改写成相对路径 |
| `SizeChar.py` | 统计目录内文件体积 |
| `address.py` | 按文件名是否含数字筛选并搬运 CSV |
| `Delete.py` / `DeleteMain.py` | 清理脚本（按后缀 / 按体积阈值） |
| `ReadNetText.py` | 抓取内部工单页文本（URL 已脱敏） |
| `wwise_event_test.py` | 引擎内 Python 侧的 Wwise 音频性能测试（`unreal_engine` + `PythonScriptLibrary`） |

## 三、`launchers/` 双击入口

自带 Python 运行时，使用者不需要会命令行。

| 批处理 | 调用 |
|---|---|
| `提取SE文本_CSV.bat` | `generate_se_csv_text.py` |
| `提取SE文本_TXT.bat` | `generate_se_txt_text.py` |
| `合并SE文本se_text_ukey.bat` | `merge_se_text.py` |
| `校验配置文件.bat` | `validate_config.py` |
| `OnajiFile.bat` / `SubeteFile.bat` | 生成文件名清单（当前目录 / 递归） |

## 四、`config/` 配置层

配置定义了"哪些内容需要本地化、按什么规则校验"，是整条文本管线的规则来源。

> **本仓库中的配置为裁剪示例。** 原始项目的 `translate_config.json` 覆盖 198 张表、
> `proto_alias.json` 含 455 条协议别名；这里保留**完整结构与代表性条目**，表名与枚举值
> 已替换为通用示例，路径替换为 `<WORK_ROOT>` 占位符。配置驱动是这套管线的主张，
> 具体业务数据不在本仓库中。

| 文件 | 规模（示例 / 原始） | 作用 |
|---|---|---|
| `se_csv_text_type.json` | 65 / 65 个类型名 | 文本字段的类型注册表，导出脚本据此寻找 `<表名>_<类型>_<语言>` 形式的列 |
| `translate_config.json` | 6 / 198 张表 | 「表 → 需翻译字段」的唯一真源，校验入口据此逐字段比对 proto 类型 |
| `LocalizationBlacklist.json` | 5 / 35 张表 | 字段级本地化黑名单 |
| `proto_alias.json` | 12 / 455 条 | proto 字段别名映射 |

### 类型注册表

同一个表里并存多种文本字段：`NAME`（名称）、`HELP`（帮助文本）、`TALK00~02`（对话）、
`UINAME`（界面名）……共 65 种。导出脚本不硬编码这些类型，
新增一种文本类型时改配置、不改代码。

### 校验清单

被翻译的表里，只有一部分字段是给玩家看的字符串，其余是 ID、枚举、数值。
这份清单（原始项目 198 张表）是"哪些字段必须翻译"的唯一真源；
`validate_config.py` 拿它比对 proto 类型，发现非字符串就报错。

文件开头是该配置的使用说明：

> - 表格对应的协议英文名可以在这个配置里查找：`<WORK_ROOT>/Table/config/converlist.xml`
> - 列表最后一项后面不要加逗号
> - 枚举类型的字符串不用配置，`<WORK_ROOT>/Table/result`，这个目录可以查看转表生成的 json 文件，如果是数字就是枚举
> - 只能配置 string 类型的变量，类型可以查看 `<WORK_ROOT>/Protocol/resproto/proto_res_c.proto`

### 字段级黑名单

有些字段是字符串，但不该被翻译：地图编辑文件路径、NavMesh 路径、关卡持久化路径、
BGM 资源名、默认天气名等。这类字段一旦进了翻译流程，只会产出无意义的"译文"并污染下游。

```json
{ "demo_map_cfg": { "MapEditFile": false, "NavMeshFile": false,
                    "PersistentLevelPath": false, "BGMusic": false,
                    "DefaultWeatherName": false, "MiniMapPath": false } }
```

判断依据是：**字符串不等于需要翻译**。

## 五、`samples/` 运行样例

三条 demo 覆盖三个分支，全部虚构数据，不依赖业务路径。
统一前置（在 `samples\` 目录下）：

```bat
set PYTHONPATH=..\tools\localization
```

### demo 1 · CSV 分支

```
输入  SETextCSV/DemoText.csv + se_csv_text_type.json
脚本  tools/localization/generate_se_csv_text.py
产出  SEText_output/se_text_00_csv.xlsx
```

```bat
python ..\tools\localization\generate_se_csv_text.py
```

输入 CSV 按真实行布局构造：行 1-2 注释 / 行 3 列名 / 行 4-6 元信息 / 行 7+ 数据。
运行输出 `处理csv文件完成!`，产出 4 条 ukey × 8 语言列：

| ukey | ja | ko | en | de | fr |
|---|---|---|---|---|---|
| 星门石 | スターポータル | 스타 게이트 | Star Gate Stone | Sternentorstein | Pierre de portail |
| 治疗药水 | 回復薬 | 치유 물약 | Healing Potion | Heiltrank | Potion de soin |
| 恢复少量生命值。 | HPを少し回復する。 | 체력을 조금 회복한다. | Restores a small amount of HP. | Stellt ein wenig HP wieder her. | Restaure un peu de PV. |
| 用于快速移动的装置。 | 高速移動に使う装置。 | 고속 이동에 쓰는 장치. | A device used for fast travel. | Ein Gerät für schnelles Reisen. | Un appareil de voyage rapide. |

运行中可观察到：`<表名>_<类型>_<语言>` 列名被正确解析（表名取自 CSV 文件名大写）；
不含中文的行被 `is_invalid_chinese()` 丢弃；输出列序由 `se_excel_languages` 固定；
产出按 ukey 排序，多次运行结果一致。

### demo 2 · txt 分支

```
输入  SETextTXTSource/DemoItem_<语言>.txt   （6 种语言，3 个 key）
脚本  tools/localization/generate_se_txt_text.py
产出  SETextTXT/DemoItem/<语言>.txt + SEText_output/se_text_00_txt.xlsx
```

```bat
python ..\tools\localization\generate_se_txt_text.py
```

源文件首行故意放了 `// 注释` 与 `$header` 行，运行输出 `处理txt文件完成!`，
产出 3 条 × 9 语言列，注释行未进入产出。

处理过程：扁平文件先按 key 归档成 `SETextTXT/<key>/<语言>.txt`，
再按 `@:` 分块解析（`@:0001\n治疗药水` → key `0001` / value `治疗药水`），
ukey 取中文列（`SeColName.chs = 0`）。

### demo 3 · 音频分支（MD5 完整性校验）

```
输入  sound_md5/*.wav|*.aif        （4 个音频 + 1 个 txt 干扰项）
脚本  tools/sound/SoundMD5ToCSV.py
产出  sound_md5/SoundMD5.csv
```

```bat
python ..\tools\sound\SoundMD5ToCSV.py sound_md5
```

后缀白名单为 `wav / aif / aiff`，`readme.txt` 被跳过。产出：

```
sound_md5 | ui_click_backup.wav | ef64bd89a69408f4af2d43113fec7818
sound_md5 | ui_click.wav        | ef64bd89a69408f4af2d43113fec7818
sound_md5 | ui_confirm.aif      | 780f35abea6354477d11de2be304e4c9
sound_md5 | ui_hover.wav        | 71e43f502350c8ba951bacc693b1ac10
```

排序键是 `md5 + path + 文件名` 且降序，内容相同的资源因此相邻排列。

音频主管线没有 demo：`Sound table export.py` / `Scenario table export.py`
需要真实的 sci / bpx 资源格式与 Wwise 导出表，无法用虚构数据构造。

### `samples/` 目录

```
samples/
├── se_csv_text_type.json                  demo 1 的类型配置
├── SETextCSV/DemoText.csv                 demo 1 输入
├── SETextTXTSource/DemoItem_<语言>.txt     demo 2 输入
├── SEText_output/
│   ├── se_text_00_csv.xlsx                demo 1 产出模板与结果
│   └── se_text_00_txt.xlsx                demo 2 产出模板与结果
└── sound_md5/                             demo 3 输入（含产出 SoundMD5.csv）
```

## 六、`spec/` 可校验规范

把本地化生产过程中的判定知识，从脚本代码里抽成可执行、可校验的规范。
规范只声明「检查什么 + 判定条件 + 违反后果」，**不含可执行代码**；
执行器提供一组有限的检查算子，新增规则只需改 JSON。

```
spec/
├── localization.spec.json   规范本体：5 条规则
├── run_spec.py              执行器（5 个检查算子）
├── cases/pass.json          合规快照
├── cases/fail.json          违规快照
└── README.md                规范格式与扩展方式
```

| ID | 规则 | 违反后果 | 来源 |
|---|---|---|---|
| LOC-001 | 待翻译字段必须为 `string` | abort | `validate_config.py` |
| LOC-002 | 黑名单字段不得进入翻译清单 | exclude | `LocalizationBlacklist.json` |
| LOC-003 | 作为唯一键的中文列必须含中文 | exclude | `util.is_invalid_chinese()` |
| LOC-004 | 导出列名必须符合 `<表名>_<类型>_<语言>` | abort | `generate_se_csv_text.py` |
| LOC-005 | 同一 ukey 的多条译文必须报异常 | report | `merge_se_text.py` |

```bat
python spec\run_spec.py --snapshot spec\cases\pass.json
python spec\run_spec.py --snapshot spec\cases\fail.json
python spec\run_spec.py --snapshot spec\cases\fail.json --json
```

退出码：`0` 全部通过 / `1` 存在 abort 级违反 / `2` 输入或规范无法解析。

合规快照 5/5 通过，退出码 0；违规快照 5 条规则全部触发，退出码 1，
报告定位到具体表与字段：

```
[FAIL] LOC-001  待翻译字段必须为字符串类型
        [Error] 非字符串表头, c_monster_cfg.Level (int32)
        [Error] 非字符串表头, c_monster_cfg.DropRate (float)
[FAIL] LOC-004  导出列名必须符合类型约定
        [Error] 列名不符合 <表名>_<类型>_<语言> 约定: DEMOTEXT_NAME_JP
总规则 5  通过 0  违反 5  判定 FAIL
```

规范的设计约束：

1. **用 JSON 而非 YAML** —— 零依赖，任何运行时可直接加载，无需解析器；
2. **规范不含代码** —— 只有声明与数据，因此可被静态审阅，也可被 Agent 当作数据消费；
3. **算子集封闭** —— `check.kind` 写未知值直接报错退出，不求值任意表达式；
4. **每条规则必须带 `provenance` 与 `examples`** —— 规则指向来源脚本，且 pass / fail 样例各一条，执行器可自测；
5. **`action` 只有三种** —— `abort` 阻断流程、`exclude` 排除该项继续、`report` 记录但不阻断。

详见 `spec/README.md`。

## 七、`docs/` 设计产出

| 文件 | 说明 |
|---|---|
| `charts/CHAOS.json`、`charts/HARD.json` | 音游谱面，同一首曲目的两个难度 |

### 音游谱面结构

```json
{
  "format_version": 1,
  "time_base": 480,            // 每拍 480 tick
  "start_offset_time": 0.0,
  "page_list": [...],          // 分页
  "tempo_list": [...],         // 变速（BPM 变化）
  "event_order_list": [...],   // 事件时间轴
  "note_list": [...]           // 音符
}
```

## 八、处理规模

| 项 | 量级 |
|---|---|
| 按 key × 语言拆分的文本文件 | 34,733 个 / 431 MB |
| 按功能类别导出的文本 CSV | 399 个 / 175 MB |
| 交给翻译的只读配置表 | 196 张 |
| 需要翻译的配置表（校验清单覆盖） | 198 张 |
| 音频索引表（`WwiseAudio`） | 71,661 行 × 8 列 |
| 音频总表（`OutputAll`，合并后） | 78,315 行 × 8 列 |

## 九、设计与实现要点

1. **两条文本入口结构同构。** 数据来源不同（类别 CSV / key 散文件），但都收敛成同一种
   「ukey + 语言列」的表，因此合并与校验只需实现一次。
2. **ukey 用中文原文。** 中文列同时充当唯一键，并用 `is_invalid_chinese()` 校验，
   表填错会在这一步被挡下，不会流到下游。
3. **一对多不静默。** 遇到同一 ukey 的多种译文时写入 `exception.xlsx`，不任取一条。
4. **校验独立成入口。** 配置表由多岗位共同维护，"能否通过校验"是可以由任何人自行执行的动作。
5. **规则与代码分离。** 类型注册表与校验清单都是配置文件，
   新增文本类型、新增待翻译表都不需要改代码。
6. **重复字段带计数字段。** 重复字段自动产出 `_{field}Num`（长度），因为运行时不掌握数组长度。
7. **音频靠 MD5 对齐。** 表与资源分离存储，用 MD5 而非文件名判断唯一性，
   重名、改名、跨目录拷贝都不会漏。
8. **交付方式面向非程序员。** 自带运行时 + 双击批处理。

## 十、环境与限制

- 管线为 **Python 3**（三个入口脚本头部标注 3.11），依赖 `openpyxl`、`pandas`、
  `requests`、`beautifulsoup4`。
- `localization_cfg.py` 与 `json_to_lua.py` 原为 Py2 遗留（`basestring`），已移植到 Py3。
- 部分批处理内的运行时路径名为历史遗留（`Python27`），与脚本声明的 3.11 不一致，尚未统一。
- 部分文件为 **GBK 编码**（中文 Windows 时代的注释），保持原编码未转码。
- 业务路径均已替换为 `<WORK_ROOT>` / `<SOURCE_ROOT>` 等占位符，
  除 `samples/` 外的脚本无法直接运行；`samples/` 走相对路径，可以跑。
