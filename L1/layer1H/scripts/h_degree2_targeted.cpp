#include <array>
#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>
#include <algorithm>
#include <cstdlib>
#ifdef _OPENMP
#include <omp.h>
#endif
using namespace std;
static inline int mod3(int x){ x%=3; return x<0?x+3:x; }
static inline int idx(int a,int e){ return 3*mod3(a)+mod3(e); }
static uint8_t ADD3[3][3];

struct TableRec { array<uint8_t,9> T; string coeff; string table; };
struct DiagRec { array<uint8_t,3> d; string diag; };
struct WPre { uint8_t u, ell, zw_inner_idx, ub, ell_b, utarget_prefix, leftB_prefix; };
struct LPre { uint8_t b,t,a,e,f, block, ixy, iyz; array<WPre,9> w; };
static vector<LPre> LPRE;

struct Metrics{
    int assoc=0;
    int rawI=0, rawB=0, rawH=0;
    int I_tot=0, B_tot=0, H_tot=0;
    int H_pos=0, H_neg_abs=0, N_neg=0;
    int h_loc_min=999, h_loc_max=-999;
    int H_blocks[5]={0,0,0,0,0};
};
struct Row{
    string locus, A_coeff, B_coeff, A, B, d, x21, tau_x21, canonical_x21;
    Metrics m;
};
struct Summary{
    long long points=0, H_sum=0;
    int H_min=1000000000, H_max=-1000000000, N_neg_max=0, assoc_min=1000000000, assoc_max=-1000000000;
    long long H_min_count=0, H_max_count=0, pure_count=0, pure_H_max_count=0;
    int pure_H_max=-1000000000;
    long long count_above_7020=0, count_ge_7020=0, count_below_minus2268=0, count_above_7302=0;
    vector<Row> min_rows, max_rows, pure_rows;
};

static inline int block_id(int b,int t){
    if(b==0 && t==0) return 0;
    if(b==0) return 1;
    if(t==0) return 2;
    if(t==b) return 3;
    return 4;
}
static inline uint8_t Mv(const array<uint8_t,27>& M,int s,int a,int e){ return M[9*mod3(s)+idx(a,e)]; }
string coeff6(int c0,int c1,int c2,int c3,int c4,int c5){
    string s; s.reserve(6); int v[6]={c0,c1,c2,c3,c4,c5}; for(int x:v) s.push_back(char('0'+x)); return s;
}
string table_str(const array<uint8_t,9>& T){ string s; s.reserve(9); for(int v:T) s.push_back(char('0'+v)); return s; }
string diag_str(const array<uint8_t,3>& d){ string s; s.reserve(3); for(int v:d) s.push_back(char('0'+v)); return s; }
string x21(const string& A,const string& B,const string& d){ return A+B+d; }
string tau_x21(const string& x){
    int vals[21]; for(int i=0;i<21;i++) vals[i]=x[i]-'0'; int y[21]={0};
    auto cidx=[](int a,int b,int e){ a=mod3(a); b=mod3(b); e=mod3(e); return (b==1)?3*a+e:9+3*a+e; };
    for(int a=0;a<3;a++) for(int e=0;e<3;e++){
        y[cidx(-a,2,-e)] = mod3(-vals[cidx(a,1,e)]);
        y[cidx(-a,1,-e)] = mod3(-vals[cidx(a,2,e)]);
    }
    y[18]=mod3(-vals[18]); y[19]=mod3(-vals[20]); y[20]=mod3(-vals[19]);
    string s; s.reserve(21); for(int i=0;i<21;i++) s.push_back(char('0'+y[i])); return s;
}
string canonical_x21(const string& x){ string t=tau_x21(x); return min(x,t); }

void init_pre(){
    for(int a=0;a<3;a++) for(int b=0;b<3;b++) ADD3[a][b]=uint8_t((a+b)%3);
    LPRE.clear(); LPRE.reserve(243);
    for(int b=0;b<3;b++) for(int t=0;t<3;t++) for(int a=0;a<3;a++) for(int e=0;e<3;e++) for(int f=0;f<3;f++){
        LPre L{}; L.b=b; L.t=t; L.a=a; L.e=e; L.f=f; L.block=block_id(b,t); L.ixy=9*b+3*a+e; L.iyz=9*mod3(t-b)+idx(e-b,f-b);
        int k=0;
        for(int u=0;u<3;u++) for(int ell=0;ell<3;ell++){
            WPre W{}; W.u=u; W.ell=ell; W.zw_inner_idx=9*mod3(u-t)+idx(f-t,ell-t); W.ub=mod3(u-b); W.ell_b=mod3(ell-b); W.utarget_prefix=9*u; W.leftB_prefix=9*u+ell; L.w[k++]=W;
        }
        LPRE.push_back(L);
    }
}

vector<TableRec> degree2_tables(){
    vector<TableRec> v; v.reserve(729); set<string> seen;
    for(int c0=0;c0<3;c0++) for(int c1=0;c1<3;c1++) for(int c2=0;c2<3;c2++)
    for(int c3=0;c3<3;c3++) for(int c4=0;c4<3;c4++) for(int c5=0;c5<3;c5++){
        TableRec r; r.coeff=coeff6(c0,c1,c2,c3,c4,c5);
        for(int a=0;a<3;a++) for(int e=0;e<3;e++){
            int val=c0+c1*a+c2*e+c3*a*a+c4*a*e+c5*e*e;
            r.T[idx(a,e)] = (uint8_t)mod3(val);
        }
        r.table=table_str(r.T);
        if(!seen.insert(r.table).second){ cerr << "duplicate degree<=2 table: " << r.table << "\n"; exit(2); }
        v.push_back(r);
    }
    return v;
}
vector<DiagRec> diags(){
    vector<DiagRec> out; out.reserve(27);
    for(int a=0;a<3;a++) for(int b=0;b<3;b++) for(int c=0;c<3;c++){
        DiagRec r; r.d={(uint8_t)a,(uint8_t)b,(uint8_t)c}; r.diag=diag_str(r.d); out.push_back(r);
    }
    return out;
}
array<uint8_t,27> buildM(const TableRec& A,const TableRec& B,const DiagRec& D){
    array<uint8_t,27> M{};
    for(int a=0;a<3;a++) for(int e=0;e<3;e++){
        M[idx(a,e)] = (uint8_t)((a==e)?D.d[a]:mod3(-a-e));
        M[9+idx(a,e)] = A.T[idx(a,e)];
        M[18+idx(a,e)] = B.T[idx(a,e)];
    }
    return M;
}
Metrics compute_metrics(const TableRec& A,const TableRec& B,const DiagRec& D){
    auto M=buildM(A,B,D); Metrics m;
    for(const auto& L: LPRE){
        const uint8_t xy=M[L.ixy];
        const uint8_t yz=M[L.iyz];
        const uint8_t epL=M[9*L.t+3*xy+L.f];
        const uint8_t epR=M[9*L.b+3*L.a+ADD3[L.b][yz]];
        m.assoc += (epL==epR);
        int di=0, db=0;
        for(const auto& W: L.w){
            const uint8_t zw_abs=ADD3[L.t][M[W.zw_inner_idx]];
            const uint8_t leftI=M[9*L.t+3*xy+zw_abs];
            const uint8_t right_inner=M[9*W.ub+3*yz+W.ell_b];
            const uint8_t rightI=M[9*L.b+3*L.a+ADD3[L.b][right_inner]];
            di += (leftI!=rightI);
            const uint8_t leftB=M[W.utarget_prefix+3*epL+W.ell];
            const uint8_t rightB=M[W.utarget_prefix+3*epR+W.ell];
            db += (leftB!=rightB);
        }
        m.rawI += di; m.rawB += db;
        int h=2*(di-db);
        m.H_blocks[L.block] += h;
        if(h>0) m.H_pos += h;
        else if(h<0){ m.H_neg_abs += -h; m.N_neg++; }
        if(h<m.h_loc_min) m.h_loc_min=h;
        if(h>m.h_loc_max) m.h_loc_max=h;
    }
    m.assoc*=3;
    m.rawH=m.rawI-m.rawB;
    m.I_tot=6*m.rawI; m.B_tot=6*m.rawB; m.H_tot=6*m.rawH;
    m.H_pos*=3; m.H_neg_abs*=3; m.N_neg*=3;
    for(int i=0;i<5;i++) m.H_blocks[i]*=3;
    return m;
}
Row make_row(const string& locus,const TableRec& A,const TableRec& B,const DiagRec& D,const Metrics& m){
    Row r; r.locus=locus; r.A_coeff=A.coeff; r.B_coeff=B.coeff; r.A=A.table; r.B=B.table; r.d=D.diag; r.x21=x21(r.A,r.B,r.d); r.tau_x21=tau_x21(r.x21); r.canonical_x21=min(r.x21,r.tau_x21); r.m=m; return r;
}
static const size_t ROW_CAP=5000;
void maybe_store(vector<Row>& v,const Row& r){ if(v.size()<ROW_CAP) v.push_back(r); }
void update_summary(Summary& s,const TableRec& A,const TableRec& B,const DiagRec& D,const Metrics& m){
    s.points++; s.H_sum += m.H_tot;
    s.assoc_min=min(s.assoc_min,m.assoc); s.assoc_max=max(s.assoc_max,m.assoc);
    s.N_neg_max=max(s.N_neg_max,m.N_neg);
    if(m.H_tot>7020) s.count_above_7020++;
    if(m.H_tot>=7020) s.count_ge_7020++;
    if(m.H_tot<-2268) s.count_below_minus2268++;
    if(m.H_tot>7302) s.count_above_7302++;
    if(m.H_tot < s.H_min){ s.H_min=m.H_tot; s.H_min_count=1; s.min_rows.clear(); maybe_store(s.min_rows, make_row("Hmin",A,B,D,m)); }
    else if(m.H_tot == s.H_min){ s.H_min_count++; maybe_store(s.min_rows, make_row("Hmin",A,B,D,m)); }
    if(m.H_tot > s.H_max){ s.H_max=m.H_tot; s.H_max_count=1; s.max_rows.clear(); maybe_store(s.max_rows, make_row("Hmax",A,B,D,m)); }
    else if(m.H_tot == s.H_max){ s.H_max_count++; maybe_store(s.max_rows, make_row("Hmax",A,B,D,m)); }
    if(m.N_neg==0){
        s.pure_count++;
        if(m.H_tot > s.pure_H_max){ s.pure_H_max=m.H_tot; s.pure_H_max_count=1; s.pure_rows.clear(); maybe_store(s.pure_rows, make_row("pure_frontier",A,B,D,m)); }
        else if(m.H_tot == s.pure_H_max){ s.pure_H_max_count++; maybe_store(s.pure_rows, make_row("pure_frontier",A,B,D,m)); }
    }
}
void merge_summary(Summary& dst, const Summary& src){
    dst.points += src.points; dst.H_sum += src.H_sum;
    dst.assoc_min=min(dst.assoc_min,src.assoc_min); dst.assoc_max=max(dst.assoc_max,src.assoc_max);
    dst.N_neg_max=max(dst.N_neg_max,src.N_neg_max);
    dst.count_above_7020 += src.count_above_7020; dst.count_ge_7020 += src.count_ge_7020; dst.count_below_minus2268 += src.count_below_minus2268; dst.count_above_7302 += src.count_above_7302;
    if(src.H_min < dst.H_min){ dst.H_min=src.H_min; dst.H_min_count=src.H_min_count; dst.min_rows=src.min_rows; }
    else if(src.H_min == dst.H_min){ dst.H_min_count += src.H_min_count; for(const auto &r:src.min_rows) maybe_store(dst.min_rows,r); }
    if(src.H_max > dst.H_max){ dst.H_max=src.H_max; dst.H_max_count=src.H_max_count; dst.max_rows=src.max_rows; }
    else if(src.H_max == dst.H_max){ dst.H_max_count += src.H_max_count; for(const auto &r:src.max_rows) maybe_store(dst.max_rows,r); }
    dst.pure_count += src.pure_count;
    if(src.pure_H_max > dst.pure_H_max){ dst.pure_H_max=src.pure_H_max; dst.pure_H_max_count=src.pure_H_max_count; dst.pure_rows=src.pure_rows; }
    else if(src.pure_H_max == dst.pure_H_max){ dst.pure_H_max_count += src.pure_H_max_count; for(const auto &r:src.pure_rows) maybe_store(dst.pure_rows,r); }
}
void write_summary(const string& path,const Summary& s){
    ofstream f(path); if(!f){ cerr << "cannot open "<<path<<"\n"; exit(4); }
    f << "stratum,function_count,points,H_min,H_min_count,H_max,H_max_count,H_mean_num,H_mean_den,pure_count,pure_H_max,pure_H_max_count,N_neg_max,count_above_PAB_7020,count_ge_PAB_7020,count_below_affine_min_minus2268,count_above_affine_max_7302,Assoc_min,Assoc_max,stored_Hmin_rows,stored_Hmax_rows,stored_pure_frontier_rows\n";
    f << "degree_le2_total_x_Delta,729," << s.points << ',' << s.H_min << ',' << s.H_min_count << ',' << s.H_max << ',' << s.H_max_count << ',' << s.H_sum << ',' << s.points << ',' << s.pure_count << ',' << s.pure_H_max << ',' << s.pure_H_max_count << ',' << s.N_neg_max << ',' << s.count_above_7020 << ',' << s.count_ge_7020 << ',' << s.count_below_minus2268 << ',' << s.count_above_7302 << ',' << s.assoc_min << ',' << s.assoc_max << ',' << s.min_rows.size() << ',' << s.max_rows.size() << ',' << s.pure_rows.size() << "\n";
}
void write_loci(const string& path,const Summary& s){
    ofstream f(path); if(!f){ cerr << "cannot open "<<path<<"\n"; exit(4); }
    f << "locus,A_coeff,B_coeff,A,B,d,x21,tau_x21,canonical_x21,Assoc,rawI,rawB,rawH,I_tot,B_tot,H_tot,H_pos,H_neg_abs,N_neg,h_loc_min,h_loc_max,H_RRR,H_RRS,H_RSR,H_SRR,H_DIST\n";
    auto wr=[&](const vector<Row>& rows,const string& locus){
        for(const auto& r:rows){ const Metrics& m=r.m;
            f << locus << ',' << r.A_coeff << ',' << r.B_coeff << ',' << r.A << ',' << r.B << ',' << r.d << ',' << r.x21 << ',' << r.tau_x21 << ',' << r.canonical_x21 << ',' << m.assoc << ',' << m.rawI << ',' << m.rawB << ',' << m.rawH << ',' << m.I_tot << ',' << m.B_tot << ',' << m.H_tot << ',' << m.H_pos << ',' << m.H_neg_abs << ',' << m.N_neg << ',' << m.h_loc_min << ',' << m.h_loc_max << ',' << m.H_blocks[0] << ',' << m.H_blocks[1] << ',' << m.H_blocks[2] << ',' << m.H_blocks[3] << ',' << m.H_blocks[4] << "\n";
        }
    };
    wr(s.min_rows,"Hmin"); wr(s.max_rows,"Hmax"); wr(s.pure_rows,"pure_frontier");
}
void write_orbits(const string& in_path,const string& out_path){
    ifstream in(in_path); ofstream out(out_path); if(!in || !out){ cerr << "cannot open orbit io\n"; exit(5); }
    string header,line; getline(in,header);
    map<pair<string,string>, set<string>> members;
    map<pair<string,string>, vector<string>> metrics;
    while(getline(in,line)){
        vector<string> col; string cur; stringstream ss(line); while(getline(ss,cur,',')) col.push_back(cur);
        if(col.size()<26) continue;
        string locus=col[0], x=col[6], tau=col[7], canon=col[8]; auto key=make_pair(locus,canon);
        members[key].insert(x); members[key].insert(tau);
        if(metrics[key].empty()) metrics[key]={x,col[15],col[13],col[14],col[16],col[17],col[18],col[9],col[1],col[2],col[5]};
    }
    out << "locus,canonical_x21,orbit_members,orbit_size_effective_S3,tau_fixed,representative_x21,H_tot,I_tot,B_tot,H_pos,H_neg_abs,N_neg,Assoc,A_coeff,B_coeff,d\n";
    for(auto &kv:members){
        string ms; bool first=true; for(auto &m:kv.second){ if(!first) ms+=';'; ms+=m; first=false; }
        auto mm=metrics[kv.first];
        out << kv.first.first << ',' << kv.first.second << ',' << ms << ',' << kv.second.size() << ',' << (kv.second.size()==1?"True":"False");
        for(auto &v:mm) out << ',' << v; out << "\n";
    }
}
int main(int argc,char** argv){
    init_pre();
    string root = argc>1 ? argv[1] : string("/mnt/data/layer1H_level25");
    long long offset = 0, limit = 0;
    if(argc>2) offset = atoll(argv[2]);
    if(argc>3) limit = atoll(argv[3]);
    string outdir = root + "/tables";
    auto tabs=degree2_tables(); auto ds=diags();
    long long full_total=(long long)tabs.size()*tabs.size()*ds.size();
    long long total=full_total;
    if(offset<0 || offset>=full_total){ cerr << "bad offset\n"; return 6; }
    if(limit>0 && offset+limit<full_total) total=offset+limit;
    cerr << "degree<=2 tables=" << tabs.size() << " full_points=" << full_total << " scanning=[" << offset << "," << total << ") count=" << (total-offset) << ((limit>0)?" (CHUNK)":"") << "\n";
    int nthreads=1;
#ifdef _OPENMP
    nthreads=omp_get_max_threads();
#endif
    vector<Summary> locals(nthreads);
#pragma omp parallel
    {
        int tid=0;
#ifdef _OPENMP
        tid=omp_get_thread_num();
#endif
        Summary local;
#pragma omp for schedule(static)
        for(long long p=offset;p<total;p++){
            long long q=p; int id=q%27; q/=27; int ib=q%729; q/=729; int ia=q;
            const auto& A=tabs[ia]; const auto& B=tabs[ib]; const auto& D=ds[id];
            Metrics m=compute_metrics(A,B,D);
            update_summary(local,A,B,D,m);
        }
        locals[tid]=std::move(local);
    }
    Summary global; for(auto &s:locals) merge_summary(global,s);
    write_summary(outdir+"/H_degree2_targeted_summary.csv",global);
    write_loci(outdir+"/H_degree2_frontier_loci.csv",global);
    write_orbits(outdir+"/H_degree2_frontier_loci.csv",outdir+"/H_degree2_frontier_orbits.csv");
    cerr << "degree<=2 summary H_min=" << global.H_min << " count="<<global.H_min_count << " H_max=" << global.H_max << " count="<<global.H_max_count << " pure_H_max=" << global.pure_H_max << " pure_count=" << global.pure_count << "\n";
    return 0;
}
