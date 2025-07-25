#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OMNeT++ 6.1 / opp_scavetool 결과 후처리 스크립트
- scavetool 필터 사용 안 함(= Parse error 회피)
- 전체 벡터/스칼라를 CSV로 덤프 후, Python에서 name/module 키워드로 필터링

추출 예시:
1) Throughput: packetReceivedFromPeer + packetBytes 포함 벡터
2) Contention Window 변화: contentionWindowChanged 포함 벡터
3) Retry 관련 스칼라
4) Packet Loss Rate: sentPk vs packetDropRetryLimitReached

필요하면 KEYWORDS만 바꾸면 됨.
"""

import os
import sys
import glob
import csv
import subprocess
from typing import List, Tuple

# ------------------------- 사용자 설정 -------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'data')

# 결과 파일(.vec/.sca) 위치 (요청대로 고정)
RESULTS_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'ini', 'results')

# --- Python 측 필터 키워드 (name/module 컬럼 기준) ---
# Throughput (MAC 수신 바이트) 후보 키워드
THR_NAME_KEYS    = ['packetReceivedFromPeer', 'packetBytes']
THR_MODULE_KEYS  = ['host[0]', 'wlan[0]', 'mac', 'dcf']   # 필요시 조정

# Contention Window 변화
CW_NAME_KEYS     = ['contentionWindowChanged']           # 이름에 이 문자열 포함

# Retry, Drop, Sent 은 스칼라에서 정확한 name 사용
RETRY_NAMES      = ['packetSentToPeerWithRetry:count',
                    'packetSentToPeerWithoutRetry:count']
# UdpBasicApp의 실제 통계 이름으로 변경
SENT_NAME        = 'packetSent:count'
SENT_MODULE_KEY  = 'app[0]'
DROP_NAME        = 'packetDropRetryLimitReached:count'
DROP_MODULE_KEY  = 'mac.dcf'
# ---------------------------------------------------------------

def run_cmd(cmd: List[str], desc: str) -> str:
    print(f"🚀 {desc}...")
    print("   $", " ".join(cmd))
    try:
        p = subprocess.run(cmd, check=True, text=True,
                           capture_output=True, encoding='utf-8')
        if p.stdout.strip():
            print(p.stdout.strip())
        print("✅ 완료\n")
        return p.stdout
    except FileNotFoundError:
        print(f"❌ '{cmd[0]}' 명령을 찾을 수 없습니다. PATH 설정 확인.")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"❌ 에러: {desc}")
        print("---- stdout ----")
        print(e.stdout)
        print("---- stderr ----")
        print(e.stderr)
        sys.exit(1)

def ensure_files() -> Tuple[List[str], List[str]]:
    vec_files = glob.glob(os.path.join(RESULTS_DIR, '*.vec'))
    sca_files = glob.glob(os.path.join(RESULTS_DIR, '*.sca'))
    if not vec_files and not sca_files:
        print(f"❌ .vec / .sca 결과 파일을 찾을 수 없습니다. 경로: {RESULTS_DIR}")
        sys.exit(1)
    print(f"🔎 vec files: {len(vec_files)}개 / sca files: {len(sca_files)}개 발견")
    return vec_files, sca_files

def dump_all(vec_files: List[str], sca_files: List[str],
             vec_out: str, sca_out: str):
    # 벡터 전체
    cmd_v = ['opp_scavetool', 'x', '-v', '-F', 'CSV-R', '-o', vec_out] + vec_files
    run_cmd(cmd_v, "벡터 전체 덤프")

    # 스칼라 전체
    # [수정] export 명령어에서는 -s 옵션을 사용하지 않음
    cmd_s = ['opp_scavetool', 'x', '-F', 'CSV-S', '-x', 'allowMixed=true', '-o', sca_out] + sca_files
    run_cmd(cmd_s, "스칼라 및 파라미터 전체 덤프")

def filter_rows(in_csv: str, out_csv: str,
                name_keys: List[str] = None,
                module_keys: List[str] = None,
                name_or_keys: List[str] = None):
    """
    - name_keys: name에 모두 포함되어야 하는 부분 문자열 리스트 (AND)
    - module_keys: module에 모두 포함되어야 하는 부분 문자열 리스트 (AND)
    - name_or_keys: name이 이 값들 중 하나라도 '포함'해야 함 (OR)
    """
    name_keys   = name_keys or []
    module_keys = module_keys or []
    name_or_keys  = name_or_keys or []

    kept = 0
    with open(in_csv, newline='', encoding='utf-8') as fi, \
         open(out_csv, 'w', newline='', encoding='utf-8') as fo:
        reader = csv.DictReader(fi)
        if not reader.fieldnames:
            return
        writer = csv.DictWriter(fo, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            name_val   = row.get('name', '')
            module_val = row.get('module', '')

            if name_or_keys:
                if not any(k in name_val for k in name_or_keys):
                    continue

            if name_keys and not all(k in name_val for k in name_keys):
                continue
            if module_keys and not all(k in module_val for k in module_keys):
                continue

            writer.writerow(row)
            kept += 1

    print(f"ℹ️  {os.path.basename(out_csv)}: {kept} rows kept "
          f"(name_keys={name_keys}, module_keys={module_keys}, name_or_keys={name_or_keys})")

def sum_scalar(csv_path: str, name_target: str, module_key: str = None) -> float:
    """CSV 파일에서 특정 스칼라 값들을 합산하는 함수"""
    total = 0.0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if name_target in row.get('name', ''):
                if module_key and module_key not in row.get('module', ''):
                    continue
                try:
                    total += float(row.get('value', '0'))
                except (ValueError, TypeError):
                    pass
    return total

def main():
    print("--- OMNeT++ 결과 데이터 후처리 시작 ---")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"📁 결과 저장: {OUTPUT_DIR}\n")

    vec_files, sca_files = ensure_files()

    # 1) 전체 덤프
    all_vec_csv = os.path.join(OUTPUT_DIR, 'all_vectors.csv')
    all_sca_csv = os.path.join(OUTPUT_DIR, 'all_scalars.csv')
    dump_all(vec_files, sca_files, all_vec_csv, all_sca_csv)

    # 2) Throughput 벡터 추출
    thr_csv = os.path.join(OUTPUT_DIR, 'throughput.csv')
    filter_rows(all_vec_csv, thr_csv,
                name_keys=THR_NAME_KEYS,
                module_keys=THR_MODULE_KEYS)

    # 3) CW 벡터 추출
    cw_csv = os.path.join(OUTPUT_DIR, 'cw_data.csv')
    filter_rows(all_vec_csv, cw_csv,
                name_keys=CW_NAME_KEYS)

    # 4) Retry 스칼라 추출
    retry_csv = os.path.join(OUTPUT_DIR, 'retry_counts.csv')
    filter_rows(all_sca_csv, retry_csv,
                name_or_keys=RETRY_NAMES)

    # 5) Packet Loss Rate 계산
    total_sent    = sum_scalar(all_sca_csv, SENT_NAME, module_key=SENT_MODULE_KEY)
    total_dropped = sum_scalar(all_sca_csv, DROP_NAME, module_key=DROP_MODULE_KEY)
    loss_rate = (total_dropped / total_sent * 100.0) if total_sent > 0 else 0.0

    summary = (
        "----- 요약 -----\n"
        f"- 총 전송 패킷(sentPk): {total_sent:.0f}\n"
        f"- 재시도 한계 드랍(packetDropRetryLimitReached): {total_dropped:.0f}\n"
        f"- 패킷 손실률: {loss_rate:.2f}%\n"
    )
    print(summary)

    summary_file = os.path.join(OUTPUT_DIR, 'packet_loss_summary.txt')
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary.strip())

    print(f"✅ 요약 저장: {summary_file}")
    print("\n--- 모든 후처리 작업 완료 ---")

if __name__ == "__main__":
    main()
