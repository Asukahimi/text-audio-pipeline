# -*- coding: utf-8 -*-
"""SPEC 执行器。

读取 localization.spec.json 与一份管线快照，逐规则校验并输出报告。
规范只声明「检查什么 / 判定条件 / 违反后果」，本执行器提供有限的算子集。
规范中不含可执行代码，因此新增规则只需改 JSON，不需要改这里。
"""
import argparse
import json
import re
import sys
import os

CHECKERS = {}


def checker(kind):
    def deco(fn):
        CHECKERS[kind] = fn
        return fn
    return deco


# ---------------------------------------------------------------- 算子集
@checker("field_type_is")
def _field_type_is(snap, params):
    """待翻译字段的类型必须等于 expected_type。"""
    want = params["expected_type"]
    only_when = params.get("only_when")
    out = []
    for tbl in snap.get("tables", []):
        for fld in tbl.get("fields", []):
            if only_when == "in_manifest" and not fld.get("in_manifest"):
                continue
            if fld.get("proto_type") != want:
                out.append({"table": tbl["name"], "field": fld["name"],
                            "proto_type": fld.get("proto_type")})
    return out


@checker("not_in_blacklist")
def _not_in_blacklist(snap, params):
    """进了待翻译清单 + 又在黑名单里的字段，是违规。"""
    out = []
    for tbl in snap.get("tables", []):
        for fld in tbl.get("fields", []):
            if fld.get("in_manifest") and fld.get("blacklisted"):
                out.append({"table": tbl["name"], "field": fld["name"]})
    return out


@checker("ukey_has_cjk")
def _ukey_has_cjk(snap, params):
    """ukey 必须含中文，否则说明列错位或表填错。"""
    pat = re.compile(params["pattern"])
    out = []
    for row in snap.get("generated_rows", []):
        if not pat.search(str(row.get("ukey", ""))):
            out.append({"column": row.get("column"), "ukey": row.get("ukey")})
    return out


@checker("column_name_matches")
def _column_name_matches(snap, params):
    """列名必须符合类型约定，否则会被静默漏掉。"""
    pat = re.compile(params["pattern"])
    ignore = set(snap.get("column_ignore", []))
    out = []
    for col in snap.get("columns", []):
        if col in ignore:
            continue
        if not pat.match(str(col)):
            out.append({"column": col})
    return out


@checker("no_multi_translation")
def _no_multi_translation(snap, params):
    """同一 ukey 多条译文要暴露出来。"""
    allow_identical = params.get("allow_identical", False)
    out = []
    for item in snap.get("merged", []):
        vals = item.get("translations") or []
        if len(vals) <= 1:
            continue
        if allow_identical and len(set(vals)) == 1:
            continue
        out.append({"ukey": item.get("ukey"), "count": len(vals)})
    return out


# ---------------------------------------------------------------- 主流程
def load_json(path, label):
    if not os.path.exists(path):
        print("[Error] %s 不存在: %s" % (label, path), file=sys.stderr)
        sys.exit(2)
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (ValueError, UnicodeDecodeError) as exc:
        print("[Error] %s 解析失败: %s" % (label, exc), file=sys.stderr)
        sys.exit(2)


def run(spec, snap):
    results = []
    for rule in spec.get("rules", []):
        kind = rule["check"]["kind"]
        fn = CHECKERS.get(kind)
        if fn is None:
            print("[Error] 规范使用了未实现的算子: %s (规则 %s)" % (kind, rule["id"]),
                  file=sys.stderr)
            sys.exit(2)

        violations = fn(snap, rule["check"].get("params", {}))
        tmpl = rule["on_violation"]["message"]
        for v in violations:
            v["message"] = tmpl.format(**v) if _fmt_ok(tmpl, v) else tmpl
        results.append({
            "id": rule["id"],
            "name": rule["name"],
            "status": "FAIL" if violations else "PASS",
            "action": rule["on_violation"]["action"],
            "code": rule["on_violation"]["code"],
            "violations": violations,
        })
    return results


def _fmt_ok(tmpl, mapping):
    try:
        tmpl.format(**mapping)
        return True
    except (KeyError, IndexError):
        return False


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="执行 localization.spec.json")
    ap.add_argument("--spec", default=os.path.join(here, "localization.spec.json"))
    ap.add_argument("--snapshot", required=True, help="管线快照 JSON")
    ap.add_argument("--json", action="store_true", help="额外输出机器可读报告")
    args = ap.parse_args()

    spec = load_json(args.spec, "规范")
    snap = load_json(args.snapshot, "快照")

    results = run(spec, snap)
    failed = [r for r in results if r["status"] == "FAIL"]
    aborts = [r for r in failed if r["action"] == "abort"]
    verdict = "FAIL" if aborts else ("WARN" if failed else "PASS")

    name = os.path.basename(args.snapshot)
    print("=" * 60)
    print("SPEC   %s  v%s" % (os.path.basename(args.spec), spec.get("spec_version")))
    print("快照   %s" % name)
    print("=" * 60)
    for r in results:
        mark = {"PASS": "PASS", "FAIL": "FAIL"}[r["status"]]
        print("[%s] %s  %s" % (mark, r["id"], r["name"]))
        for v in r["violations"]:
            print("        %s" % v["message"])
    print("-" * 60)
    print("总规则 %d  通过 %d  违反 %d  判定 %s"
          % (len(results), len(results) - len(failed), len(failed), verdict))

    report = {
        "spec": {"file": os.path.basename(args.spec), "version": spec.get("spec_version")},
        "snapshot": name,
        "summary": {"total": len(results), "passed": len(results) - len(failed),
                    "failed": len(failed), "verdict": verdict},
        "results": results,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    sys.exit(1 if aborts else 0)


if __name__ == "__main__":
    main()
