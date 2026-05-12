#!/usr/bin/env -S python3 -S
from __future__ import annotations
import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TABLES=ROOT/'tables'

def rows(name):
    with open(TABLES/name,newline='') as f:
        return list(csv.DictReader(f))

def one(name):
    rr=rows(name)
    assert len(rr)==1, f'{name}: expected one row, got {len(rr)}'
    return rr[0]

def check_consistency(rr, name):
    for i,r in enumerate(rr):
        assert int(r['H_tot'])==int(r['I_tot'])-int(r['B_tot']), f'{name}[{i}] H=I-B mismatch'
        assert int(r['H_tot'])==int(r['H_pos'])-int(r['H_neg_abs']), f'{name}[{i}] signed mismatch'

def by(rows_, *keys):
    return {tuple(r[k] for k in keys):r for r in rows_}

def main():
    std=rows('H_standard_six.csv')
    exp={'g1_PAB':7020,'g2_transparent':5292,'g3_su2_transparent':888,'g4_echo':900,'g5_self_referential':1836,'g6_anti_complement':5220}
    assert len(std)==6
    for r in std:
        assert int(r['H_tot'])==exp[r['label']]
    check_consistency(std,'standard')

    cb=rows('H_column_blind_all_diags.csv')
    aff=rows('H_affine_all_diags.csv')
    assert len(cb)==243
    assert len(aff)==19683
    for rr,name,lo,hi,pure_count in [(cb,'cb',1836,7302,159),(aff,'affine',-2268,7302,723)]:
        H=[int(r['H_tot']) for r in rr]
        assert min(H)==lo and max(H)==hi, name
        pure=[r for r in rr if int(r['N_neg'])==0]
        assert len(pure)==pure_count, name
        assert max(int(r['H_tot']) for r in pure)==7020, name
        assert sum(1 for h in H if h>7020)==12, name
        assert sum(1 for h in H if h>=7020)==18, name
        check_consistency(rr,name)

    loci={r['locus'] for r in rows('H_frontier_orbits.csv')}
    assert {'Hmax_7302','Hmin_minus2268','pure_frontier_7020'}.issubset(loci)

    d2=one('H_degree2_exact_summary.csv')
    assert int(d2['function_count'])==729
    assert int(d2['points'])==14348907
    assert int(d2['H_min'])==-2268 and int(d2['H_min_count'])==8
    assert int(d2['H_max'])==7302 and int(d2['H_max_count'])==12
    assert int(d2['pure_count'])==3177
    assert int(d2['pure_H_max'])==7020 and int(d2['pure_H_max_count'])==6
    assert int(d2['count_above_PAB_7020'])==12
    assert int(d2['count_ge_PAB_7020'])==18
    assert int(d2['count_below_affine_min_minus2268'])==0
    assert int(d2['count_above_affine_max_7302'])==0
    assert int(d2['N_neg_max'])==468

    d2_loci=rows('H_degree2_frontier_loci.csv')
    assert len(d2_loci)==26
    assert sum(1 for r in d2_loci if r['locus']=='Hmin' and int(r['H_tot'])==-2268)==8
    assert sum(1 for r in d2_loci if r['locus']=='Hmax' and int(r['H_tot'])==7302)==12
    assert sum(1 for r in d2_loci if r['locus']=='pure_frontier' and int(r['H_tot'])==7020 and int(r['N_neg'])==0)==6
    check_consistency(d2_loci,'degree2_loci')
    d2_orb=rows('H_degree2_frontier_orbits.csv')
    assert len(d2_orb)==15
    assert sum(1 for r in d2_orb if r['locus']=='Hmin')==5
    assert sum(1 for r in d2_orb if r['locus']=='Hmax')==6
    assert sum(1 for r in d2_orb if r['locus']=='pure_frontier')==4

    # v0.4 structural additions.
    cls=rows('H_frontier_locus_class_summary.csv')
    assert len(cls)==4
    assert sum(1 for r in cls if r['locus']=='Hmin')==2
    assert any(r['locus']=='Hmin' and int(r['Assoc'])==81 and int(r['N_neg'])==288 for r in cls)
    assert any(r['locus']=='Hmin' and int(r['Assoc'])==189 and int(r['N_neg'])==432 for r in cls)
    assert any(r['locus']=='pure_frontier' and int(r['H_neg_abs'])==0 and int(r['N_neg'])==0 for r in cls)

    sig=rows('H_frontier_term_signature_summary.csv')
    assert len(sig)==15
    sigmap=by(sig,'locus','block')
    assert int(sigmap[('Hmax','RRR')]['neg_union_terms'])==6
    assert int(sigmap[('Hmax','RRS')]['always_pos_terms'])==54
    assert int(sigmap[('Hmax','SRR')]['always_zero_terms'])==54
    assert int(sigmap[('pure_frontier','DIST')]['value_stable_terms'])==54
    assert all(int(sigmap[('pure_frontier',b)]['neg_union_terms'])==0 for b in ['RRR','RRS','RSR','SRR','DIST'])

    shell=rows('H_local_shell_summary.csv')
    assert len(shell)==14
    sh=by(shell,'center','radius')
    assert int(sh[('PAB','1')]['above_center'])==2
    assert int(sh[('PAB','2')]['above_center'])==0
    assert int(sh[('degree2_Hmax_representative','1')]['equal_center'])==1
    assert int(sh[('degree2_Hmax_representative','2')]['above_center'])==0
    assert int(sh[('affine_Hmin_assoc81_representative','1')]['above_center'])==42
    assert int(sh[('affine_Hmin_assoc81_representative','2')]['above_center'])==840

    print('Layer 1H level-2.5 verifier: PASS')
    print('  standard-six table: PASS')
    print('  column-blind × Δ exact range and purity frontier: PASS')
    print('  affine × Δ exact range and purity frontier: PASS')
    print('  degree≤2 × Δ exact range and purity frontier: PASS')
    print('  signed-spectrum consistency H=H_pos-H_neg_abs: PASS')
    print('  frontier term signatures: PASS')
    print('  local shell integration: PASS')

if __name__=='__main__':
    main()
