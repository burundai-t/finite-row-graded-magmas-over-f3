#!/usr/bin/env -S python3 -S
from __future__ import annotations
import csv
from pathlib import Path
from h_core import tau_x21, canonical_x21

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / 'generated' / 'degree2_chunks_exact'
TABLES = ROOT / 'tables'

SUMMARY_FIELDS = ['stratum','function_count','points','H_min','H_min_count','H_max','H_max_count','H_mean_num','H_mean_den','pure_count','pure_H_max','pure_H_max_count','N_neg_max','count_above_PAB_7020','count_ge_PAB_7020','count_below_affine_min_minus2268','count_above_affine_max_7302','Assoc_min','Assoc_max','stored_Hmin_rows','stored_Hmax_rows','stored_pure_frontier_rows']
LOCUS_FIELDS = ['locus','A_coeff','B_coeff','A','B','d','x21','tau_x21','canonical_x21','Assoc','rawI','rawB','rawH','I_tot','B_tot','H_tot','H_pos','H_neg_abs','N_neg','h_loc_min','h_loc_max','H_RRR','H_RRS','H_RSR','H_SRR','H_DIST']
ORBIT_FIELDS = ['locus','canonical_x21','orbit_members','orbit_size_effective_S3','tau_fixed','representative_x21','H_tot','I_tot','B_tot','H_pos','H_neg_abs','N_neg','Assoc']

def read_csv(path: Path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))

def write_csv(path: Path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

def as_int(row, key):
    return int(row[key])

def aggregate_summary(rows):
    H_min = min(as_int(r, 'H_min') for r in rows)
    H_max = max(as_int(r, 'H_max') for r in rows)
    pure_H_max = max(as_int(r, 'pure_H_max') for r in rows)
    out = {k: 0 for k in SUMMARY_FIELDS}
    out['stratum'] = 'degree_le2_x_Delta_exact'
    out['function_count'] = 729
    out['points'] = sum(as_int(r, 'points') for r in rows)
    out['H_min'] = H_min
    out['H_min_count'] = sum(as_int(r, 'H_min_count') for r in rows if as_int(r, 'H_min') == H_min)
    out['H_max'] = H_max
    out['H_max_count'] = sum(as_int(r, 'H_max_count') for r in rows if as_int(r, 'H_max') == H_max)
    out['H_mean_num'] = sum(as_int(r, 'H_mean_num') for r in rows)
    out['H_mean_den'] = sum(as_int(r, 'H_mean_den') for r in rows)
    out['pure_count'] = sum(as_int(r, 'pure_count') for r in rows)
    out['pure_H_max'] = pure_H_max
    out['pure_H_max_count'] = sum(as_int(r, 'pure_H_max_count') for r in rows if as_int(r, 'pure_H_max') == pure_H_max)
    out['N_neg_max'] = max(as_int(r, 'N_neg_max') for r in rows)
    out['count_above_PAB_7020'] = sum(as_int(r, 'count_above_PAB_7020') for r in rows)
    out['count_ge_PAB_7020'] = sum(as_int(r, 'count_ge_PAB_7020') for r in rows)
    out['count_below_affine_min_minus2268'] = sum(as_int(r, 'count_below_affine_min_minus2268') for r in rows)
    out['count_above_affine_max_7302'] = sum(as_int(r, 'count_above_affine_max_7302') for r in rows)
    out['Assoc_min'] = min(as_int(r, 'Assoc_min') for r in rows)
    out['Assoc_max'] = max(as_int(r, 'Assoc_max') for r in rows)
    return out

def normalize_loci(rows, summary):
    H_min = int(summary['H_min'])
    H_max = int(summary['H_max'])
    pure_H_max = int(summary['pure_H_max'])
    filtered = []
    seen = set()
    for r in rows:
        H = int(r['H_tot'])
        N = int(r['N_neg'])
        keep = None
        if H == H_max:
            keep = 'Hmax'
        elif H == H_min:
            keep = 'Hmin'
        elif H == pure_H_max and N == 0:
            keep = 'pure_frontier'
        if keep:
            r = dict(r)
            r['locus'] = keep
            r['tau_x21'] = tau_x21(r['x21'])
            r['canonical_x21'] = canonical_x21(r['x21'])
            key = (keep, r['x21'])
            if key not in seen:
                seen.add(key)
                filtered.append(r)
    return sorted(filtered, key=lambda r: (r['locus'], r['canonical_x21'], r['x21']))

def make_orbits(loci):
    by = {}
    for r in loci:
        by.setdefault((r['locus'], r['canonical_x21']), r)
    out = []
    for (locus, canon), r in sorted(by.items()):
        members = sorted({r['x21'], tau_x21(r['x21'])})
        out.append({
            'locus': locus,
            'canonical_x21': canon,
            'orbit_members': ';'.join(members),
            'orbit_size_effective_S3': len(members),
            'tau_fixed': str(len(members) == 1),
            'representative_x21': members[0],
            'H_tot': r['H_tot'],
            'I_tot': r['I_tot'],
            'B_tot': r['B_tot'],
            'H_pos': r['H_pos'],
            'H_neg_abs': r['H_neg_abs'],
            'N_neg': r['N_neg'],
            'Assoc': r['Assoc'],
        })
    return out

def main():
    summary_files = sorted(CHUNKS.glob('summary_*.csv'))
    loci_files = sorted(CHUNKS.glob('loci_*.csv'))
    if not summary_files or not loci_files:
        raise SystemExit(f'No chunk files found under {CHUNKS}')
    summaries = []
    loci_rows = []
    for p in summary_files:
        rows = read_csv(p)
        if rows: summaries.extend(rows)
    for p in loci_files:
        loci_rows.extend(read_csv(p))
    summary = aggregate_summary(summaries)
    loci = normalize_loci(loci_rows, summary)
    summary['stored_Hmin_rows'] = sum(1 for r in loci if r['locus'] == 'Hmin')
    summary['stored_Hmax_rows'] = sum(1 for r in loci if r['locus'] == 'Hmax')
    summary['stored_pure_frontier_rows'] = sum(1 for r in loci if r['locus'] == 'pure_frontier')
    orbits = make_orbits(loci)
    write_csv(TABLES / 'H_degree2_exact_summary.csv', [summary], SUMMARY_FIELDS)
    write_csv(TABLES / 'H_degree2_frontier_loci.csv', loci, LOCUS_FIELDS)
    write_csv(TABLES / 'H_degree2_frontier_orbits.csv', orbits, ORBIT_FIELDS)
    print('Layer1H degree<=2 chunk aggregation: PASS')
    print(f"  chunks: {len(summary_files)} summary files, {len(loci_files)} loci files")
    print(f"  points: {summary['points']}, H range: [{summary['H_min']},{summary['H_max']}], pure max: {summary['pure_H_max']}")

if __name__ == '__main__':
    main()
