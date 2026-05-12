#!/usr/bin/env -S python3 -S
from h_core import column_blind_x21, h_metrics, h_direct_tot, standard_six, assoc_tot, tau_x21
EXPECTED={
'g1_PAB':(219,756,0,1512,2160,2592,7020),'g2_transparent':(273,828,72,1332,1332,1728,5292),'g3_su2_transparent':(285,348,96,276,24,144,888),'g4_echo':(561,108,0,720,72,0,900),'g5_self_referential':(489,972,0,1080,-216,0,1836),'g6_anti_complement':(219,828,72,1224,1476,1620,5220)}
def main():
    for label,x in {'PAB':column_blind_x21(1,2,'000'),'row_complement':column_blind_x21(2,1,'000'),'cb_Hmax_example':column_blind_x21(0,1,'220')}.items():
        m=h_metrics(x); assert h_direct_tot(x)==(m['I_tot'],m['B_tot'],m['H_tot']); assert h_metrics(tau_x21(x))['H_tot']==m['H_tot']
    for label,x in standard_six().items():
        m=h_metrics(x); got=(assoc_tot(x),m['H_RRR'],m['H_SRR'],m['H_RRS'],m['H_RSR'],m['H_DIST'],m['H_tot']); assert got==EXPECTED[label],(label,got)
    print('Layer 1H master-formula verifier: PASS')
    print('  direct 9^4 vs normalized 3^7: PASS')
    print('  standard-six H table: PASS')
    print('  tau/S3 invariance smoke check: PASS')
if __name__=='__main__': main()
