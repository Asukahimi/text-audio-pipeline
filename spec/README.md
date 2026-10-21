# 可校验规范（SPEC）

把本地化生产过程中的**判定知识**，从脚本代码里抽出来，写成可执行、可校验的规范。

规范只声明「检查什么 + 判定条件 + 违反后果」，**不含可执行代码**。
执行器提供一组有限的检查算子，新增规则只需改 JSON，不需要改执行器。

## 文件

```
spec/
├── localization.spec.json   规范本体：5 条规则
├── run_spec.py              执行器：读规范 + 快照，输出报告
└── cases/
    ├── pass.json            合规快照（全部规则通过）
    └── fail.json            违规快照（5 类违反各触发一次）
```

## 运行

```bat
python spec\run_spec.py --snapshot spec\cases\pass.json
python spec\run_spec.py --snapshot spec\cases\fail.json
python spec\run_spec.py --snapshot spec\cases\fail.json --json
```

退出码：`0` 全部通过 / `1` 存在 abort 级违反 / `2` 输入或规范无法解析。

合规快照的输出：

```
[PASS] LOC-001  待翻译字段必须为字符串类型
[PASS] LOC-002  黑名单字段不得进入翻译清单
[PASS] LOC-003  作为唯一键的中文列必须含中文
[PASS] LOC-004  导出列名必须符合类型约定
[PASS] LOC-005  同一 ukey 的多条译文必须报异常
总规则 5  通过 5  违反 0  判定 PASS
```

违规快照的输出（节选）：

```
[FAIL] LOC-001  待翻译字段必须为字符串类型
        [Error] 非字符串表头, c_monster_cfg.Level (int32)
        [Error] 非字符串表头, c_monster_cfg.DropRate (float)
[FAIL] LOC-004  导出列名必须符合类型约定
        [Error] 列名不符合 <表名>_<类型>_<语言> 约定: DEMOTEXT_NAME_JP
总规则 5  通过 0  违反 5  判定 FAIL
```

## 五条规则

| ID | 规则 | 违反后果 | 来源 |
|---|---|---|---|
| LOC-001 | 待翻译字段必须为 `string` | abort | `validate_config.py` |
| LOC-002 | 黑名单字段不得进入翻译清单 | exclude | `LocalizationBlacklist.json` |
| LOC-003 | 作为唯一键的中文列必须含中文 | exclude | `util.is_invalid_chinese()` |
| LOC-004 | 导出列名必须符合 `<表名>_<类型>_<语言>` | abort | `generate_se_csv_text.py` |
| LOC-005 | 同一 ukey 的多条译文必须报异常 | report | `merge_se_text.py` |

每条规则的 `provenance` 字段指向它所来源的脚本或配置——**规则不是凭空写的，是从真实工具里抽出来的**。

## 规则结构

```json
{
  "id": "LOC-004",
  "name": "导出列名必须符合类型约定",
  "intent": "为什么需要这条规则（人会看，Agent 用来判断边界情况）",
  "applies_to": "columns[*] except column_ignore",
  "assert": "column matches /^...$/",
  "check": { "kind": "column_name_matches", "params": { "pattern": "..." } },
  "on_violation": { "action": "abort", "code": "E_BAD_COLUMN_NAME", "message": "..." },
  "examples": { "pass": {...}, "fail": {...} },
  "provenance": { "script": "...", "config": "...", "note": "..." }
}
```

| 字段 | 作用 |
|---|---|
| `applies_to` | 规则的作用对象，用路径表达式描述 |
| `assert` | 判定条件的可读形式（给人看、给 Agent 理解） |
| `check` | 判定条件的可执行形式（执行器按 `kind` 分派算子） |
| `on_violation.action` | 只允许 `abort` / `exclude` / `report` 三种 |
| `examples` | 必填。pass 与 fail 各一条，执行器可自测 |
| `provenance` | 规则出处，指向脚本或配置 |

## 快照格式

执行器只读一份**证据快照**，不接触原始工程。快照描述一次管线运行的现场：

```json
{
  "tables":          [{ "name": "...", "fields": [
                         { "name": "...", "proto_type": "...",
                           "in_manifest": true, "blacklisted": false }] }],
  "columns":         ["DEMOTEXT_NAME_CHS", "DEMOTEXT_NAME_JA"],
  "column_ignore":   ["#IDAlias", "LINENO"],
  "generated_rows":  [{ "ukey": "治疗药水", "column": "DEMOTEXT_NAME_CHS" }],
  "merged":          [{ "ukey": "治疗药水", "translations": ["回復薬"] }]
}
```

## 检查算子集

| kind | 参数 | 判定 |
|---|---|---|
| `field_type_is` | `expected_type`, `only_when` | 字段类型是否等于期望值 |
| `not_in_blacklist` | — | 是否存在「进了清单 + 又在黑名单」的字段 |
| `ukey_has_cjk` | `pattern` | ukey 是否匹配中文正则 |
| `column_name_matches` | `pattern` | 列名是否匹配命名约定 |
| `no_multi_translation` | `allow_identical` | 是否存在一对多译文 |

算子集是封闭的：规范里写 `check.kind` 之外的值，执行器直接报错退出，**不会去求值任意表达式**。

## 增加一条规则

1. 在 `localization.spec.json` 的 `rules` 末尾追加一条，`check.kind` 用已有算子；
2. 若需要新判定逻辑，在 `run_spec.py` 里加一个 `@checker("新算子名")` 函数；
3. 在 `cases/pass.json` 里补一条能通过的数据，在 `cases/fail.json` 里补一条能触发的数据；
4. 跑两条用例，确认 pass 全过、fail 命中新规则。

## 设计约束

1. **规范用 JSON 而非 YAML。** 零依赖，任何运行时可直接加载，不需要解析器。
2. **规范不含代码。** 只有声明与数据，执行器实现算子。这样规范可以被静态审阅，也可以被 Agent 当作数据消费。
3. **封闭算子集。** 避免规则作者写出无法审查的判定逻辑。
4. **每条规则必须有 pass/fail 样例。** 没有样例的规则等于没写过。
5. **`action` 只有三种。** `abort` 阻断流程、`exclude` 排除该项继续、`report` 记录但不阻断。
